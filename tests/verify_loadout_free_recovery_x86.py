#!/usr/bin/env python3
"""Full original RB erase state and ownership comparisons on balanced trees."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/loadout_free.cpp','src/loadout_lookup.cpp','src/loadout_erase.cpp','src/loadout_iterator.cpp','src/loadout_map.cpp','src/subobject_id.cpp','tests/fixtures/loadout_map_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-erase.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbol='?Free@Loadout@@YAXXZ';dll=ROOT/'build/loadout_free_recovery.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1e000000',f'/out:{dll}']+objects+['/export:'+symbol,'/export:LoadoutLookupTree,DATA'],check=True)
 h=X86Harness();h.load(original);new=h.load(dll);uc=h.uc;heap=0x23000000;uc.mem_map(heap,0x10000);head=heap;nil=heap+64;tree=h.scratch;out=tree+64;events=[];count=0;rng=random.Random(2003)
 def hook(uc,address,size,user):
  if address==0x6391a7a:events.append(h.word(uc.reg_read(UC_X86_REG_ESP)+4));h.return_stub(0)
 uc.hook_add(UC_HOOK_CODE,hook)
 for depth in range(1,7):
  length=2**depth-1
  for trial in range(30):
   uc.mem_write(heap,rng.randbytes(0x10000));nodes=[heap+128+i*64 for i in range(length)]
   def build(lo,hi,parent):
    if lo>=hi:return nil
    mid=(lo+hi)//2;p=nodes[mid];left=build(lo,mid,p);right=build(mid+1,hi,p)
    uc.mem_write(p,struct.pack('<IIII',left,parent,right,mid));uc.mem_write(p+40,b'\1\0');h.write_word(p+24,heap+0x8000+mid*32);return p
   root=build(0,length,head);uc.mem_write(head,struct.pack('<IIII',nodes[0],root,nodes[-1],0));uc.mem_write(head+40,b'\0\0');uc.mem_write(nil,struct.pack('<IIII',nil,nil,nil,0));uc.mem_write(nil+40,b'\1\1');uc.mem_write(tree,struct.pack('<III',0,head,nil)+b'\0'*4+struct.pack('<I',length))
   seed=bytes(uc.mem_read(heap,0x10000));results=[]
   for exports,tree_address in [(None,0x63fc2a8),(new,new['LoadoutLookupTree'])]:
    uc.mem_write(heap,seed);uc.mem_write(tree_address,struct.pack('<III',0,head,nil)+b'\0'*8);events.clear()
    h.invoke(0x6311b50 if exports is None else exports[symbol])
    results.append((bytes(uc.mem_read(heap,0x10000)),bytes(uc.mem_read(tree_address,20)),list(events)))
   assert results[0]==results[1],(depth,trial)
   assert struct.unpack_from('<I',results[0][1],16)[0]==(-length)&0xffffffff
   assert len(results[0][2])==length*2;count+=1
 report=dict(status='passed',differential_calls=count,initial_trees=180,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['src/loadout_rb.hpp','src/loadout_tree.hpp','tests/verify_loadout_free_recovery_x86.py']},not_verified=['Insertion-generated arbitrary RB color distributions','Arbitrary corrupted tree recovery','Native heap/exception failure','Exact instruction matching'])
 (ROOT/'analysis/loadout-free-recovery-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} Free recovery calls, exact tree/payload memory, size underflow and release order')
if __name__=='__main__':main()
