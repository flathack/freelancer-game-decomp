#!/usr/bin/env python3
"""Loadout vector ownership and distinct construction/assignment padding semantics."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/loadout_map.cpp','src/subobject_id.cpp','tests/fixtures/loadout_map_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-map.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbols=['??0Map@Loadout@@QAE@ABU01@@Z','??4Map@Loadout@@QAEAAU01@ABU01@@Z','??1Map@Loadout@@QAE@XZ'];dll=ROOT/'build/loadout_map.dll'
 subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1d000000',f'/out:{dll}']+objects+['/export:'+n for n in symbols],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;uc.mem_map(0,4096);uc.mem_map(0x23000000,0x10000);target=h.scratch;source=target+64;heap=0x23000000;events=[];count=0;rng=random.Random(2003)
 def hook(uc,address,size,user):
  if address not in [0x6391abc,0x6391a7a]:return
  arg=h.word(uc.reg_read(UC_X86_REG_ESP)+4);events.append(('new' if address==0x6391abc else 'free',arg));h.return_stub(heap+0x4000 if address==0x6391abc else 0)
 uc.hook_add(UC_HOOK_CODE,hook)
 for symbol in symbols:
  for length in range(8):
   for old_length in range(8):
    for capacity in [old_length,old_length+3]:
     for self_assign in ([False,True] if symbol==symbols[1] else [False]):
      srcseed=rng.randbytes(24);dstseed=rng.randbytes(24);memory=rng.randbytes(0x5000);results=[]
      for exports in [orig,new]:
       uc.mem_write(source,srcseed);uc.mem_write(target,dstseed);uc.mem_write(heap,memory);events.clear()
       for obj,base,n,cap in [(source,heap,length,length),(target,heap+0x1000,old_length,capacity)]:
        first=base if cap else 0;h.write_word(obj+8,first);h.write_word(obj+12,first+n*32);h.write_word(obj+16,first+cap*32)
       args=() if symbol==symbols[2] else (target if self_assign else source,)
       ret=h.invoke(exports[symbol],args,target)
       results.append((None if symbol==symbols[2] else ret,bytes(uc.mem_read(target,24)),bytes(uc.mem_read(source,24)),bytes(uc.mem_read(heap,0x5000)),list(events)))
      assert results[0]==results[1],(symbol,length,old_length,capacity,self_assign)
      count+=1
 report=dict(status='passed',differential_calls=count,export_count=3,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['src/loadout_map.hpp','tests/verify_loadout_map_x86.py']},not_verified=['Default constructor allocator indeterminacy','Allocation failure/exception unwinding','Partial object overlap','Native heap','Exact instruction matching'])
 (ROOT/'analysis/loadout-map-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} Map copies/assignments/destructors, exact object/heap/padding/release effects')
if __name__=='__main__':main()
