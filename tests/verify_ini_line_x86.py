#!/usr/bin/env python3
"""Differential INI string getters, shared-buffer lifetime, joins and diagnostics."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 sources=['src/ini_reader_line.cpp','src/ini_reader_strings.cpp','src/ini_reader.cpp','src/file_map.cpp','tests/fixtures/ini_strings_x86_runtime.cpp','tests/fixtures/ini_values_x86_runtime.cpp','tests/fixtures/ini_reconstructed_index_runtime.cpp','src/string_index.cpp','tests/fixtures/file_map_x86_runtime.cpp']
 build=ROOT/'build';objects=[];commands=[]
 for source in sources:
  out=build/(pathlib.Path(source).stem+'-lineptr.obj');objects.append(str(out));cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-mno-sse','-mno-sse2','-c',str(ROOT/source),'-o',str(out)];subprocess.run(cmd,check=True);commands.append(cmd)
 indexed='?get_value_string@INI_Reader@@QAEPBDI@Z';joined='?get_value_string@INI_Reader@@QAEPBDXZ';shared='?INIValuesStringBuffer@@3PADA';line='?get_line_ptr@INI_Reader@@QAEPBDXZ';textbuffer='?INITextLineBuffer@@3PADA';binarybuffer='?INIBinaryLineBuffer@@3PADA';dll=build/'ini_line.dll'
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x18000000',f'/out:{dll}']+objects+['/export:'+line,'/export:'+textbuffer+',DATA','/export:'+binarybuffer+',DATA','/export:'+indexed,'/export:'+joined,'/export:'+shared+',DATA','/export:?StringIndexBuffer@@3PADA,DATA'];subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(dll);assert new[shared]-new[binarybuffer]==256;uc=h.uc;uc.mem_map(0x23000000,0x10000)
 o=h.scratch;r=o+0x2000;block=0x23000000;entry=block+0x10;parameters=block+0x100;strings=block+0x2000;original_shared=0x658d900;rebuilt_shared=new[shared]
 uc.mem_write(strings,b'Header\0Value\0');uc.mem_write(block,struct.pack('<HH',0,1))
 sprintf=h.stop+0x200;message=h.stop+0x220;h.write_word(0x639931c,sprintf);h.write_word(0x6399378,message)
 def text(ptr):
  out=bytearray()
  for i in range(2048):
   b=uc.mem_read(ptr+i,1)[0]
   if not b:return bytes(out)
   out.append(b)
  raise AssertionError('Unterminated output')
 search=h.stop+0x240;h.write_word(0x6399300,search)
 events=[]
 def hook(uc,address,size,user):
  sp=uc.reg_read(UC_X86_REG_ESP)
  if address==search:
   ptr=h.word(sp+4);ch=h.word(sp+8)&255;result=0
   for i in range(1024):
    byte=uc.mem_read(ptr+i,1)[0]
    if byte==ch:result=ptr+i;break
    if not byte:break
   h.return_stub(result)
  elif address==sprintf:
   target=h.word(sp+4);fmt=text(h.word(sp+8))
   if fmt==b'%d':
    raw=h.word(sp+12);value=raw if raw<2**31 else raw-2**32;output=str(value).encode();events.append(('integer',raw))
   elif fmt==b'%g':
    bits=bytes(uc.mem_read(sp+12,8));value=struct.unpack('<d',bits)[0];output=format(value,'.6g').encode();events.append(('float64',bits.hex()))
   elif fmt==b'%s = ':output=text(h.word(sp+12))+b' = ';events.append(('line-name',output))
   elif fmt==b'%s = %s':output=text(h.word(sp+12))+b' = '+text(h.word(sp+16));events.append(('text-line',output))
   else:
    assert fmt==b'header [%s] value %s missing parameter %u'
    output=b'header ['+text(h.word(sp+12))+b'] value '+text(h.word(sp+16))+b' missing parameter '+str(h.word(sp+20)).encode();events.append(('diagnostic',output))
   uc.mem_write(target,output+b'\0');h.return_stub(len(output))
  elif address==message:
   assert h.word(sp+4)==0 and text(h.word(sp+12))==b'ERROR' and h.word(sp+16)==0;events.append(('message',text(h.word(sp+8))));h.return_stub(1);uc.reg_write(UC_X86_REG_ESP,sp+20)
 uc.hook_add(UC_HOOK_CODE,hook)
 def setup(values):
  for obj in [o,r]:
   uc.mem_write(obj,b'\0'*0x1600);h.write_word(obj+0x1450,strings);h.write_word(obj+0x1454,block);h.write_word(obj+0x145c,entry);h.write_word(obj+0x1460,parameters);uc.mem_write(obj+0x1564,b'\1')
  uc.mem_write(entry,struct.pack('<HB',7,len(values)))
  for i,(tag,bits) in enumerate(values):uc.mem_write(parameters+5*i,struct.pack('<BI',tag,bits))
 def category(pointer,obj,buffer):
  if pointer in [0x63fc198,new[textbuffer]]:return 'text-line'
  if pointer in [0x658d800,new[binarybuffer]]:return 'binary-line'
  if pointer==buffer:return 'shared'
  if pointer in [0x6400350,new['?StringIndexBuffer@@3PADA']]:return 'index'
  if pointer==obj+0x1464:return 'joined'
  if strings<=pointer<strings+0x1000:return ('table',pointer-strings)
  if pointer==obj+0x828:return 'text'
  return 'literal'
 calls=0;line_calls=0;rows=[]
 def pair(symbol,index=None):
  nonlocal calls,line_calls
  traces=[];pointers=[];outputs=[]
  for exports,obj,buffer in [(orig,o,original_shared),(new,r,rebuilt_shared)]:
   start=len(events);pointer=h.invoke(exports[symbol],() if index is None else (index,),obj);traces.append(events[start:]);pointers.append(category(pointer,obj,buffer));outputs.append(text(pointer))
  assert outputs[0]==outputs[1] and traces[0]==traces[1] and pointers[0]==pointers[1],(symbol,index,outputs,traces,pointers)
  assert bytes(uc.mem_read(o+0x1464,0x19c))==bytes(uc.mem_read(r+0x1464,0x19c)),'Joined/mode/tail side effects differ'
  assert text(original_shared)==text(rebuilt_shared),'Shared formatter state differs'
  if symbol==line:
   line_calls+=1
   if pointers[0]=='binary-line':assert bytes(uc.mem_read(0x658d800,256))==bytes(uc.mem_read(new[binarybuffer],256)),'Binary line-buffer footprint differs'
   if pointers[0]=='text-line':assert bytes(uc.mem_read(0x63fc198,2048))==bytes(uc.mem_read(new[textbuffer],2048)),'Text line-buffer footprint differs'
  calls+=1;return outputs[0]
 rng=random.Random(2003)
 values=[(0,i) for i in range(256)]+[(1,v) for v in [0,1,0xffffffff,0x80000000,0x7fffffff]+[rng.randrange(2**32) for _ in range(100)]]
 values += [(2,v) for v in [0,0x80000000,1,0x3f800000,0x7f800000,0xff800000,0x7fc00000,0x7f800001]+[rng.randrange(2**32) for _ in range(100)]]
 uc.mem_write(strings+32,b'literal,value\0');values += [(3,32)]+[(v,0) for v in range(4,256)]
 for value in values:
  setup([value]);output=pair(indexed,0);rows.append(dict(tag=value[0],bits=hex(value[1]),text_hex=output.hex()))
  assert pair(joined)==output
  assert pair(line)==b'Value = '+output
 # Shared buffer changes invalidate previously returned numeric strings; unknown tags reuse it.
 setup([(1,123),(1,456),(255,0),(3,32)]);assert pair(indexed,0)==b'123';assert pair(indexed,1)==b'456';assert pair(indexed,2)==b'456';assert pair(indexed,3)==b'literal,value'
 assert pair(joined)==b'123, 456, 456, literal,value'
 for _ in range(100):
  sequence=[(rng.randrange(2),rng.randrange(2**32)) for _ in range(rng.randrange(6))];setup(sequence);pair(joined);pair(line)
 for index in [1,255,0xffffffff]:setup([(1,5)]);assert pair(indexed,index)==b''
 setup([]);assert pair(joined)==b''
 for obj in [o,r]:h.write_word(obj+0x145c,0)
 assert pair(indexed,0)==b'';assert pair(joined)==b'';assert pair(line)==b''
 # Original unchecked join crosses its 256-byte buffer and overwrites the mode byte.
 uc.mem_write(strings+32,b'A'*255+b'\0');uc.mem_write(strings+512,b'TAIL\0')
 setup([(3,32),(3,512),(1,7)]);assert pair(joined)==b'A'*255+b', TAIL, 7'
 assert uc.mem_read(o+0x1564,1)==uc.mem_read(r+0x1564,1)==b' '
 # Non-indexed text mode is a direct buffer reference and does not touch join storage.
 for obj in [o,r]:uc.mem_write(obj+0x1564,b'\0');uc.mem_write(obj+0x828,b'text, value\0')
 assert pair(joined)==b'text, value'
 text_index_cases=0
 for value in [b' a , b , ',b'"a,b",c',b',,',b'\x89x\xa0,y',b'\vx\f,y']:
  for obj in [o,r]:uc.mem_write(obj+0x1564,b'\0');uc.mem_write(obj+0x828,value+b'\0')
  for index in [0,1,2,0xffffffff]:pair(indexed,index);text_index_cases+=1
 # Line writes into adjacent numeric storage. The next unknown tag observes it.
 overflow_cases=0
 uc.mem_write(strings+512,b'V'*100+b'\0')
 for name_size in [140,150,240,250,255,256,270]:
  uc.mem_write(strings+7,b'N'*name_size+b'\0')
  for values in [[(3,512),(1,7)],[(1,123),(255,0)],[(3,512)]]:
   setup(values);pair(line)
   assert bytes(uc.mem_read(0x658d800,512))==bytes(uc.mem_read(new[binarybuffer],512)), 'Static-storage overflow state differs'
   setup([(255,0)]);pair(indexed,0)
   overflow_cases+=1
 for name,value in [(b'',b''),(b'entry',b'  a,b'),(b'A'*1023,b'B'*1000)]:
  for obj in [o,r]:uc.mem_write(obj+0x1564,b'\0');uc.mem_write(obj+0x428,name+b'\0');uc.mem_write(obj+0x828,value+b'\0')
  assert pair(line)==name+b' = '+value
 report=dict(status='passed_string_getters_under_formatter_model',original_sha256=HASH,compiled_dll_sha256=digest(dll),
             source_hashes={p:digest(ROOT/p) for p in sources+['tests/verify_ini_line_x86.py','src/string_index.hpp','src/ini_reader_strings.hpp','src/ini_reader_values.hpp','src/ini_reader.hpp','src/file_map.hpp']},
             differential_calls=calls,line_calls=line_calls,static_storage_adjacency=256,controlled_line_overflow_cases=overflow_cases,text_index_cases=text_index_cases,reconstructed_string_index_used=True,indexed_parameter_cases=len(values),join_sequences=100,shared_buffer_and_unknown_tag_checks=True,controlled_join_overflow_checked=True,
             rows=rows,commands=commands,mocks=['sprintf integer/general-float model with exact argument comparison','MessageBox diagnostic model'],
             not_verified=['Static extents beyond reconstructed 512-byte BINI region','Authentic CRT locale/float formatting','Arbitrary oversized/overlapping joins','Real OS/FPU execution','Exact instruction matching'])
 (ROOT/'analysis/ini-line-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {calls} string/line comparisons, shared-buffer reuse, joins, diagnostics, controlled overflow and text-buffer path')
if __name__=='__main__':main()
