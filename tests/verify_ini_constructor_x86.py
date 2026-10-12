#!/usr/bin/env python3
"""Original constructor full write footprint over nonzero object storage."""
import hashlib,json,pathlib,random,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ECX,UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert digest(source)=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/ini_reader_constructor.cpp','src/file_map.cpp','tests/fixtures/file_map_x86_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/('ini-ctor-'+pathlib.Path(f).stem+'.obj');objects.append(str(obj))
  subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbol='??0INI_Reader@@QAE@XZ';dll=ROOT/'build/ini_constructor.dll'
 subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1f000000',f'/out:{dll}']+objects+['/export:'+symbol],check=True)
 h=X86Harness();orig=h.load(source);new=h.load(dll);uc=h.uc;tidy=h.stop+0x200;h.write_word(0x63991b8,tidy)
 def hook(uc,address,size,user):
  if address!=tidy:return
  sp=uc.reg_read(UC_X86_REG_ESP);obj=uc.reg_read(UC_X86_REG_ECX);assert h.word(sp+4)==0
  for offset in [4,8,12]:h.write_word(obj+offset,0)
  h.return_stub(0);uc.reg_write(UC_X86_REG_ESP,sp+8)
 uc.hook_add(UC_HOOK_CODE,hook);rng=random.Random(2003);count=0
 for region in [0x20500000,0x22000000,0x7a000000,0xd1000000]:
  if region!=h.scratch:uc.mem_map(region,0x10000)
  for offset in [0,1,2,3,16,0x4000]:
   obj=region+offset
   for seed in [b'\0'*0x1568,b'\xa5'*0x1568,rng.randbytes(0x1568)]:
    outputs=[]
    for exports in [orig,new]:
     uc.mem_write(obj,seed);returned=h.invoke(exports[symbol],(),obj);assert returned==obj
     outputs.append(bytes(uc.mem_read(obj,0x1568)))
    assert outputs[0]==outputs[1],(hex(obj),next((i for i,(a,b) in enumerate(zip(*outputs)) if a!=b),None))
    count+=1
 report=dict(status='passed',differential_calls=count,source_hashes={f:digest(ROOT/f) for f in files+['src/ini_reader.hpp','src/file_map.hpp','tests/verify_ini_constructor_x86.py']},original_sha256=digest(source),compiled_dll_sha256=digest(dll),full_object_write_footprint=True,allocator_byte_from_this_high_byte=True,not_verified=['Native MSVCP60 initialization','Exception unwinding','Exact instruction matching'])
 (ROOT/'analysis/ini-constructor-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} constructors, return ABI and full 0x1568-byte footprint')
if __name__=='__main__':main()
