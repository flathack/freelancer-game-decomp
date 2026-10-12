#!/usr/bin/env python3
"""Differential original text read_header path and header-buffer footprint."""
import hashlib,json,pathlib,random,subprocess
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 sources=['src/ini_text_header.cpp','src/ini_reader.cpp','src/string_index.cpp','src/text_file.cpp','src/file_map.cpp','tests/fixtures/file_map_x86_runtime.cpp','tests/fixtures/ini_text_header_runtime.cpp'];build=ROOT/'build';objects=[];commands=[]
 for source in sources:
  obj=build/(pathlib.Path(source).stem+'-line.obj');objects.append(str(obj));cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/source),'-o',str(obj)];subprocess.run(cmd,check=True);commands.append(cmd)
 symbol='?read_header@INI_Reader@@QAE_NXZ';dll=build/'ini_text_header.dll'
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1b000000',f'/out:{dll}']+objects+['/export:'+symbol];subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(dll);uc=h.uc;uc.mem_map(0x23000000,0x10000)
 data=0x23000000;o=h.scratch;r=o+0x2000;ol=o+40;rl=r+40;rng=random.Random(2003);cases=[]
 inputs=[b'',b'[A]',b'[]',b'[ unfinished',b'[ A ]',b'[;skip]\n[B]',b'[ ;keep]\r\n[C]',b';[comment]\nvalue=x\n [REAL] trailing',b'[A\0B]\n[C]',b'['+b'A'*1023+b']\n[B]',b'[A]\r[B]\n[C]\r\n[D]\n\r[E]']
 inputs += [b''.join(rng.choice([b' ',b'\t',b';comment',b'value=1',b'[A]',b'[ B ]',b'[;skip]',b'[]',b'[broken',b'\0'])+rng.choice([b'\n',b'\r',b'\r\n',b'\n\r']) for _ in range(rng.randrange(40))) for _ in range(300)]
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
  for line in [ol,rl]:uc.mem_write(line,b'\xaa'*1024)
  lines=[]
  while pair():
   raw=bytes(uc.mem_read(ol,1024));n=raw.index(0);lines.append(dict(length=n,bytes_hex=raw[:n].hex(),cursor=h.word(o+32)))
  assert not pair() # Counter advances on repeated EOF too.
  cases.append(dict(sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),lines=lines))
 # Missing mapping and stale cursor do not advance position, but still increment line count.
 for obj in [o,r]:h.write_word(obj+24,0);h.write_word(obj+28,99);h.write_word(obj+32,55);h.write_word(obj+36,0xffffffff)
 assert not pair();assert h.word(o+32)==55 and h.word(o+36)==0
 report=dict(status='passed',original_sha256=HASH,compiled_dll_sha256=digest(dll),source_hashes={p:digest(ROOT/p) for p in sources+['src/text_file.hpp','src/file_map.hpp','src/ini_reader.hpp','src/string_index.hpp']},differential_calls=calls,input_cases=len(inputs),cases=cases,commands=commands,mocks=[],not_verified=['Actual file mapping acquisition','Aliased destination/input','Malformed pointers','Text read_value and reader lifecycle','Exact instruction matching'])
 (ROOT/'analysis/ini-text-header-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {calls} text-header calls across {len(inputs)} inputs, exact reader/parser fields and full write footprints')
if __name__=='__main__':main()
