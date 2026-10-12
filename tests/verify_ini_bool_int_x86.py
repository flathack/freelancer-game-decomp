#!/usr/bin/env python3
"""Differential binary bool/int conversion, including raw bool bytes and x87 _ftol."""
import hashlib,json,pathlib,random,re,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 build=ROOT/'build';objects=[];commands=[]
 sources=['src/ini_reader_values.cpp','src/ini_reader.cpp','src/file_map.cpp','tests/fixtures/ini_values_x86_runtime.cpp','tests/fixtures/ini_reader_x86_runtime.cpp','tests/fixtures/file_map_x86_runtime.cpp']
 for source in sources:
  out=build/(pathlib.Path(source).stem+'-values.obj');objects.append(str(out));cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-mno-sse','-mno-sse2','-c',str(ROOT/source),'-o',str(out)];subprocess.run(cmd,check=True);commands.append(cmd)
 bool_symbol='?get_value_bool@INI_Reader@@QAE_NI@Z';int_symbol='?get_value_int@INI_Reader@@QAEHI@Z';dll=build/'ini_bool_int.dll'
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x17000000',f'/out:{dll}']+objects+['/export:'+bool_symbol,'/export:'+int_symbol];subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(dll);uc=h.uc;uc.mem_map(0x23000000,0x10000)
 o=h.scratch;r=o+0x2000;block=0x23000000;entry=block+0x10;parameter=block+0x20;strings=block+0x100;fp=block+0x2000
 uc.mem_write(strings,b'Header\0Value\0');uc.mem_write(block,struct.pack('<HH',0,1));uc.mem_write(entry,struct.pack('<HB',7,1))
 for obj in [o,r]:
  uc.mem_write(obj,b'\0'*0x1568);h.write_word(obj+0x1450,strings);h.write_word(obj+0x1454,block);h.write_word(obj+0x145c,entry);h.write_word(obj+0x1460,parameter);uc.mem_write(obj+0x1564,b'\1')
 compare=h.stop+0x200;atoi=h.stop+0x220;sprintf=h.stop+0x240;message=h.stop+0x260;ftol=h.stop+0x280
 for iat,address in [(0x639902c,compare),(0x6399248,atoi),(0x639931c,sprintf),(0x6399378,message),(0x6399320,ftol)]:h.write_word(iat,address)
 # Execute FSTP m80 in the emulator, then convert the exact representation in the hook.
 uc.mem_write(ftol,b'\xdb\x3d'+struct.pack('<I',fp)+b'\x90')
 logs=[]
 def text(ptr):
  out=bytearray()
  for i in range(256):
   b=uc.mem_read(ptr+i,1)[0]
   if not b:return bytes(out)
   out.append(b)
  raise AssertionError('Long test string')
 def hook(uc,address,size,user):
  sp=uc.reg_read(UC_X86_REG_ESP)
  if address==compare:
   a=text(h.word(sp+4)).lower();b=text(h.word(sp+8)).lower();h.return_stub(((a>b)-(a<b))&0xffffffff)
  elif address==atoi:
   value=text(h.word(sp+4));m=re.match(rb'\s*([+-]?\d+)',value);number=int(m.group(1)) if m else 0;h.return_stub(number&0xffffffff)
  elif address==sprintf:
   dst=h.word(sp+4);fmt=text(h.word(sp+8));assert fmt==b'header [%s] value %s missing parameter %u'
   output=b'header ['+text(h.word(sp+12))+b'] value '+text(h.word(sp+16))+b' missing parameter '+str(h.word(sp+20)).encode();uc.mem_write(dst,output+b'\0');h.return_stub(len(output))
  elif address==message:
   assert h.word(sp+4)==0 and text(h.word(sp+12))==b'ERROR' and h.word(sp+16)==0
   logs.append(text(h.word(sp+8)));h.return_stub(1);uc.reg_write(UC_X86_REG_ESP,sp+20)
  elif address==ftol+6:
   bits=bytes(uc.mem_read(fp,10));mantissa,signexp=struct.unpack('<QH',bits);exponent=signexp&0x7fff
   shift=exponent-16383-63
   magnitude=mantissa<<shift if shift>=0 else mantissa>>(-shift)
   value=-magnitude if signexp&0x8000 else magnitude
   if exponent==0x7fff or not -2**63<=value<2**63:value=-2**63
   h.return_stub(value&0xffffffff);uc.reg_write(UC_X86_REG_EDX,(value>>32)&0xffffffff)
 uc.hook_add(UC_HOOK_CODE,hook)
 cases=[];rng=random.Random(2003)
 cases += [(0,i,None) for i in range(256)]
 cases += [(1,i,None) for i in [0,1,0xffffffff,0x80000000,0x7fffffff]+[rng.randrange(2**32) for _ in range(300)]]
 cases += [(2,i,None) for i in [0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x4f000000,0x4f800000,0x7f800000,0xff800000,0x7fc00000,0x7f800001]+[rng.randrange(2**32) for _ in range(300)]]
 cases += [(3,32,s) for s in [b'true',b'TRUE',b'false',b'FALSE',b'1',b'0',b'-42',b' 12.5',b'garbage',b'2147483647',b'-2147483648']]
 cases += [(tag,0,None) for tag in range(4,256)]
 rows=[];calls=0
 def pair(symbol,index):
  nonlocal calls
  before=len(logs);a=h.invoke(orig[symbol],(index,),o);oldlogs=logs[before:];before=len(logs);b=h.invoke(new[symbol],(index,),r)
  if symbol==bool_symbol:a&=255;b&=255
  assert a==b,(symbol,index,a,b)
  assert oldlogs==logs[before:]
  assert bytes(uc.mem_read(o+0x144c,0x18))==bytes(uc.mem_read(r+0x144c,0x18))
  calls+=1;return a
 for tag,bits,string in cases:
  uc.mem_write(parameter,struct.pack('<BI',tag,bits))
  if string is not None:uc.mem_write(strings+bits,string+b'\0')
  rows.append(dict(tag=tag,bits=hex(bits),string=string.decode() if string is not None else None,bool_al=pair(bool_symbol,0),int_eax=hex(pair(int_symbol,0))))
 for index in [1,255,0xffffffff]:pair(bool_symbol,index);pair(int_symbol,index)
 for obj in [o,r]:h.write_word(obj+0x145c,0)
 pair(bool_symbol,0);pair(int_symbol,0)
 report=dict(status='passed_binary_bool_int',original_sha256=HASH,compiled_dll_sha256=digest(dll),
             source_hashes={p:digest(ROOT/p) for p in sources+['src/ini_reader_values.hpp','src/ini_reader.hpp','src/file_map.hpp']},
             differential_calls=calls,parameter_cases=len(cases),raw_boolean_bytes_checked=256,rows=rows,commands=commands,
             mocks=['ASCII stricmp','atoi decimal-prefix model for in-range strings','_ftol truncation/saturation model using actual emulated ST0','sprintf/MessageBox diagnostic model'],
             not_verified=['Real CRT/Win32 execution','Text get_value_bool/get_value_int paths','FPU exception/control-word fidelity','Malformed parameter memory access','Other typed getters','Exact instruction matching'])
 (ROOT/'analysis/ini-bool-int-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {calls} bool/int calls, {len(cases)} parameter cases, raw AL bytes, NaNs/infinities, missing-parameter diagnostics')
if __name__=='__main__':main()
