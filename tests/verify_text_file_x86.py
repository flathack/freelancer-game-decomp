#!/usr/bin/env python3
"""Differential CR/LF, chunk-limit, EOF and buffer-footprint checks."""
import hashlib,json,pathlib,random,subprocess
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 sources=['src/text_file.cpp','src/file_map.cpp','tests/fixtures/file_map_x86_runtime.cpp'];build=ROOT/'build';objects=[];commands=[]
 for source in sources:
  obj=build/(pathlib.Path(source).stem+'-line.obj');objects.append(str(obj));cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/source),'-o',str(obj)];subprocess.run(cmd,check=True);commands.append(cmd)
 symbol='?read_line@TextFile32@@QAE_NAAULineParser32@@@Z';dll=build/'text_file.dll'
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1a000000',f'/out:{dll}']+objects+['/export:'+symbol];subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(dll);uc=h.uc;uc.mem_map(0x23000000,0x10000)
 data=0x23000000;o=h.scratch;r=o+64;ol=o+0x1000;rl=o+0x2000;rng=random.Random(2003);cases=[]
 inputs=[b'',b'a',b'\r',b'\n',b'\r\n',b'\n\r',b'\r\r',b'\n\n',b'a\rb\nc\r\nd\n\re',b'a\0b\nc',b'A'*1022+b'\r\nB',b'A'*1021+b'\r\nB',b'A'*1023+b'\nB',b'A'*4096]
 inputs += [bytes(rng.choice([0,9,10,13,32,65,90,128,255]) for _ in range(rng.randrange(2048))) for _ in range(200)]
 calls=0
 def pair():
  nonlocal calls
  a=h.invoke(orig[symbol],(ol,),o)&255;b=h.invoke(new[symbol],(rl,),r)&255
  assert a==b
  assert bytes(uc.mem_read(o,40))==bytes(uc.mem_read(r,40)),'Reader state mismatch'
  assert bytes(uc.mem_read(ol,1032))==bytes(uc.mem_read(rl,1032)),'Line buffer/tail/parser fields mismatch'
  calls+=1;return bool(a)
 for blob in inputs:
  uc.mem_write(data,blob or b'\0');seed=rng.randrange(2**32)
  for obj in [o,r]:uc.mem_write(obj,b'\0'*40);h.write_word(obj+24,data);h.write_word(obj+28,len(blob));h.write_word(obj+36,seed)
  for line in [ol,rl]:uc.mem_write(line,b'\xaa'*1032)
  lines=[]
  while pair():
   n=h.word(ol+1024);lines.append(dict(length=n,bytes_hex=bytes(uc.mem_read(ol,n)).hex(),cursor=h.word(o+32)))
  assert not pair() # Counter advances on repeated EOF too.
  cases.append(dict(sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),lines=lines))
 # Missing mapping and stale cursor do not advance position, but still increment line count.
 for obj in [o,r]:h.write_word(obj+24,0);h.write_word(obj+28,99);h.write_word(obj+32,55);h.write_word(obj+36,0xffffffff)
 assert not pair();assert h.word(o+32)==55 and h.word(o+36)==0
 report=dict(status='passed',original_sha256=HASH,compiled_dll_sha256=digest(dll),source_hashes={p:digest(ROOT/p) for p in sources+['src/text_file.hpp','src/file_map.hpp']},differential_calls=calls,input_cases=len(inputs),cases=cases,commands=commands,mocks=[],not_verified=['Actual file mapping acquisition','Aliased destination/input','Malformed pointers','Complete LineParser32 token methods','Exact instruction matching'])
 (ROOT/'analysis/text-file-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {calls} line reads across {len(inputs)} inputs, exact reader/parser fields and full write footprints')
if __name__=='__main__':main()
