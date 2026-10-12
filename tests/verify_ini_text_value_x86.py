#!/usr/bin/env python3
"""Differential text entry decoding, comments and section-boundary rewind."""
import hashlib,json,pathlib,random,subprocess
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 sources=['src/ini_text_value.cpp','src/ini_text_header.cpp','src/ini_reader.cpp','src/string_index.cpp','src/text_file.cpp','src/file_map.cpp','tests/fixtures/file_map_x86_runtime.cpp','tests/fixtures/ini_text_runtime.cpp'];build=ROOT/'build';objects=[];commands=[]
 for source in sources:
  obj=build/(pathlib.Path(source).stem+'-line.obj');objects.append(str(obj));cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/source),'-o',str(obj)];subprocess.run(cmd,check=True);commands.append(cmd)
 symbol='?read_value@INI_Reader@@QAE_NXZ';dll=build/'ini_text_value.dll'
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1c000000',f'/out:{dll}']+objects+['/export:'+symbol,'/export:?read_header@INI_Reader@@QAE_NXZ','/export:?get_state@INI_Reader@@QBEXAAUState@1@@Z','/export:?set_state@INI_Reader@@QAEXABUState@1@@Z'];subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(dll);uc=h.uc;uc.mem_map(0x23000000,0x10000)
 data=0x23000000;o=h.scratch;r=o+0x2000;ol=o+0x428;rl=r+0x428;rng=random.Random(2003);cases=[]
 inputs=[b'',b'key=value',b'orphan',b'=empty name',b'key  =  value  ;comment',b';skip\n\nK=V',b'K=V\n[NEXT]\nX=Y',b'[NEXT]',b'K=V\r\n \t[NEXT]',b'key\0tail=value\0tail',b'key="a;b"',b'#hash=value',b'A'*1023+b'=V\nNEXT=YES']
 inputs += [b''.join(rng.choice([b' ',b'\t',b';comment',b'value=1',b' key  = value  ;x',b'orphan',b'=v',b'A=B=C',b'\0'])+rng.choice([b'\n',b'\r',b'\r\n',b'\n\r']) for _ in range(rng.randrange(40))) for _ in range(300)]
 calls=0
 def pair():
  nonlocal calls
  a=h.invoke(orig[symbol],(),o)&255;b=h.invoke(new[symbol],(),r)&255
  assert a==b
  assert bytes(uc.mem_read(o,0x1568))==bytes(uc.mem_read(r,0x1568)),'Reader state mismatch'
  assert bytes(uc.mem_read(ol,1024))==bytes(uc.mem_read(rl,1024)),'Line buffer/tail/parser fields mismatch'
  calls+=1;return bool(a)
 for blob in inputs:
  uc.mem_write(data,blob or b'\0');seed=rng.randrange(2**32)
  for obj in [o,r]:uc.mem_write(obj,b'\0'*0x1568);h.write_word(obj+24,data);h.write_word(obj+28,len(blob));h.write_word(obj+36,seed)
  for obj in [o,r]:uc.mem_write(obj+0x428,b'\xaa'*2048)
  lines=[]
  while pair():
   raw=bytes(uc.mem_read(ol,1024));n=raw.index(0);lines.append(dict(length=n,bytes_hex=raw[:n].hex(),cursor=h.word(o+32)))
  assert not pair() # A next section rewinds repeatedly; EOF increments repeatedly.
  cases.append(dict(sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),lines=lines))
 # Missing mapping and stale cursor do not advance position, but still increment line count.
 for obj in [o,r]:h.write_word(obj+24,0);h.write_word(obj+28,99);h.write_word(obj+32,55);h.write_word(obj+36,0xffffffff)
 assert not pair();assert h.word(o+32)==55 and h.word(o+36)==0
 # Traverse real text INI files through alternating header/value calls, checking
 # entire reader state and snapshot restoration under the original API.
 real_files=[];sections=0;entries=0;integration_calls=0
 header_symbol='?read_header@INI_Reader@@QAE_NXZ';getstate='?get_state@INI_Reader@@QBEXAAUState@1@@Z';setstate='?set_state@INI_Reader@@QAEXABUState@1@@Z'
 def api(name,args=(),other_args=None):
  nonlocal integration_calls
  if other_args is None:other_args=args
  a=h.invoke(orig[name],args,o);b=h.invoke(new[name],other_args,r)
  if name not in [getstate,setstate]:assert a&255==b&255
  assert bytes(uc.mem_read(o,0x1568))==bytes(uc.mem_read(r,0x1568)),name
  integration_calls+=1;return a&255
 candidates=[]
 for path in (ROOT/'original/_FL Fresh Install-deutsch').rglob('*'):
  if path.is_file() and path.suffix.lower()=='.ini':
   blob=path.read_bytes()
   if blob[:4]!=b'BINI' and len(blob)<65536:candidates.append((path,blob))
 for path,blob in candidates:
  uc.mem_write(data,blob or b'\0')
  for obj in [o,r]:uc.mem_write(obj,b'\0'*0x1568);h.write_word(obj+24,data);h.write_word(obj+28,len(blob))
  file_sections=file_entries=0
  while api(header_symbol):
   sections+=1;file_sections+=1
   so=o+0x5000;sr=o+0x6000;uc.mem_write(so,b'\xaa'*0xc08);uc.mem_write(sr,b'\xaa'*0xc08)
   api(getstate,(so,),(sr,));assert bytes(uc.mem_read(so,0xc08))==bytes(uc.mem_read(sr,0xc08))
   api(setstate,(so,),(sr,))
   while api(symbol):entries+=1;file_entries+=1
  real_files.append(dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(blob).hexdigest(),sections=file_sections,entries=file_entries))
 report=dict(status='passed',original_sha256=HASH,compiled_dll_sha256=digest(dll),source_hashes={p:digest(ROOT/p) for p in sources+['src/text_file.hpp','src/file_map.hpp','src/ini_reader.hpp','src/string_index.hpp']},differential_calls=calls,integration_calls=integration_calls,real_text_files=real_files,real_sections=sections,real_entries=entries,input_cases=len(inputs),cases=cases,commands=commands,mocks=[],not_verified=['Actual file mapping acquisition','Aliased destination/input','Malformed pointers','Complete reader lifecycle and real file IO','Exact instruction matching'])
 (ROOT/'analysis/ini-text-value-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {calls} text-value cases plus {integration_calls} integrated calls over {len(real_files)} real text files / {sections} sections / {entries} entries')
if __name__=='__main__':main()
