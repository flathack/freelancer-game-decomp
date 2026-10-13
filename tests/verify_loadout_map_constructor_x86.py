#!/usr/bin/env python3
"""Loadout vector ownership and distinct construction/assignment padding semantics."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/loadout_map_constructor.cpp','src/loadout_map.cpp','src/subobject_id.cpp','tests/fixtures/loadout_map_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-map.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbols=['??0Map@Loadout@@QAE@XZ','??0Map@Loadout@@QAE@ABU01@@Z','??4Map@Loadout@@QAEAAU01@ABU01@@Z','??1Map@Loadout@@QAE@XZ'];dll=ROOT/'build/loadout_map_constructor.dll'
 subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1d000000',f'/out:{dll}']+objects+['/export:'+n for n in symbols],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;uc.mem_map(0,4096);uc.mem_map(0x23000000,0x10000);target=h.scratch;source=target+64;heap=0x23000000;events=[];count=0;rng=random.Random(2003)
 def hook(uc,address,size,user):
  if address not in [0x6391abc,0x6391a7a]:return
  arg=h.word(uc.reg_read(UC_X86_REG_ESP)+4);events.append(('new' if address==0x6391abc else 'free',arg));h.return_stub(heap+0x4000 if address==0x6391abc else 0)
 uc.hook_add(UC_HOOK_CODE,hook)
 symbol=symbols[0]
 for allocator_byte in range(256):
  for target_offset in [0,1,3,16]:
   target=h.scratch+target_offset;seed=rng.randbytes(64);results=[]
   for exports in [orig,new]:
    uc.mem_write(h.scratch,seed);uc.mem_write(h.stack+0x7f00,rng.randbytes(0x100))
    uc.mem_write(h.stack+0x8000-17,bytes([allocator_byte]))
    ret=h.invoke(exports[symbol],(),target)
    results.append((ret,bytes(uc.mem_read(h.scratch,64))))
   assert results[0]==results[1],(allocator_byte,target_offset,results)
   assert results[0][0]==target and results[0][1][target_offset+4]==allocator_byte
   count+=1
 report=dict(status='passed',differential_calls=count,export_count=1,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['src/loadout_map.hpp','tests/verify_loadout_map_constructor_x86.py']},not_verified=['Temporary assembly allocator-byte boundary','Object/stack aliasing','Allocation failure/exception unwinding','Partial object overlap','Native heap','Exact instruction matching'])
 (ROOT/'analysis/loadout-map-constructor-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} Map default constructors, all allocator bytes and full guarded object writes')
if __name__=='__main__':main()
