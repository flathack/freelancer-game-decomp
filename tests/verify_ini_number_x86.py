#!/usr/bin/env python3
"""Differential INI is_number, including permissive original syntax."""
import hashlib,itertools,json,pathlib,random,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 source=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';original_hash=hashlib.sha256(source.read_bytes()).hexdigest()
 assert original_hash=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/ini_reader_number.cpp','tests/fixtures/ini_number_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'.obj');objects.append(str(obj))
  subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbol='?is_number@INI_Reader@@QBE_NPBD@Z';dll=ROOT/'build/ini_number.dll'
 subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1e000000',f'/out:{dll}']+objects+['/export:'+symbol],check=True)
 h=X86Harness();orig=h.load(source);new=h.load(dll);uc=h.uc;lower=h.stop+0x200;h.write_word(0x63992f4,lower);events=[]
 def hook(uc,address,size,user):
  if address!=lower:return
  value=h.word(uc.reg_read(UC_X86_REG_ESP)+4);value=value if value<2**31 else value-2**32;events.append(value)
  h.return_stub(value+32 if 65<=value<=90 else value&0xffffffff)
 uc.hook_add(UC_HOOK_CODE,hook);rng=random.Random(2003)
 inputs=[b'',b'.',b'+',b'0x',b'.0x',b'1e',b'1e+',b'1e2+',b'1e.2',b'1.e-',b"'a'trailing",b"'1",b"'0xFF",b' 1',b'1 ',b'0XdeadBEEF']
 inputs += [bytes(v) for n in range(1,5) for v in itertools.product(b'01.e+-x\'',repeat=n)]
 inputs += [prefix+bytes([v])+suffix for v in range(1,256) for prefix,suffix in [(b'',b''),(b'0x',b''),(b'1',b''),(b"'",b"'")]]
 inputs += [bytes(rng.choice(b'0123456789.eE+-xXaAfF\' ') for _ in range(rng.randrange(1,40))) for _ in range(5000)]
 results=[];ptr=h.scratch+0x3000;obj=h.scratch
 for data in inputs:
  uc.mem_write(ptr,data+b'\0\0\0');uc.mem_write(obj,b'\xa5'*0x1568);comparisons=[]
  for exports in [orig,new]:
   events.clear();value=h.invoke(exports[symbol],(ptr,),obj)&255;comparisons.append((value,list(events)))
  assert comparisons[0]==comparisons[1],(data,comparisons)
  assert bytes(uc.mem_read(obj,0x1568))==b'\xa5'*0x1568
  results.append(dict(input_hex=data.hex(),accepted=bool(comparisons[0][0])))
 files+=['src/ini_reader.hpp','tests/verify_ini_number_x86.py']
 report=dict(status='passed',original_sha256=original_hash,compiled_dll_sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),differential_calls=len(inputs),source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},tolower_arguments_compared=True,results=results,not_verified=['Native CRT locale tolower','Null/malformed pointers','Exact instruction matching'])
 (ROOT/'analysis/ini-number-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {len(inputs)} is_number calls, exact tolower dispatch and unchanged reader')
if __name__=='__main__':main()
