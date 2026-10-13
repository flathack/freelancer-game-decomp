#!/usr/bin/env python3
"""Original lower-bound Loadout tree lookup against reconstructed code."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/loadout_lookup.cpp','src/loadout_free.cpp','src/loadout_map.cpp','src/subobject_id.cpp','tests/fixtures/loadout_map_runtime.cpp'];objects=[];dll=ROOT/'build/loadout_free.dll';symbol='?Free@Loadout@@YAXXZ'
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-free.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1b000000',f'/out:{dll}']+objects+['/export:'+symbol,'/export:LoadoutLookupTree,DATA'],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;heap=0x23000000;uc.mem_map(heap,0x10000);rng=random.Random(2003);count=0
 events=[]
 def hook(uc,address,size,user):
  if address==0x6391a7a:events.append(h.word(uc.reg_read(UC_X86_REG_ESP)+4));h.return_stub(0)
 uc.hook_add(UC_HOOK_CODE,hook)
 for iteration in range(300):
  keys=[] if iteration==0 else sorted(set([0,0xffffffff,0x80000000]+[rng.randrange(2**32) for _ in range(rng.randrange(70))]))
  order=keys[:];rng.shuffle(order);head=heap;nil=heap+64;nodes={key:heap+128+i*64 for i,key in enumerate(keys)};children={key:[nil,nil,nil] for key in keys};root=nil
  for key in order:
   if root==nil:root=nodes[key];continue
   current=next(k for k,v in nodes.items() if v==root)
   while True:
    side=0 if key<current else 2
    if children[current][side]==nil:children[current][side]=nodes[key];children[key][1]=nodes[current];break
    current=next(k for k,v in nodes.items() if v==children[current][side])
  uc.mem_write(heap,b'\xa5'*0x10000);uc.mem_write(head,struct.pack('<IIII',nodes[keys[0]] if keys else head,root,nodes[keys[-1]] if keys else head,0));uc.mem_write(nil,struct.pack('<IIII',nil,nil,nil,0))
  for key,node in nodes.items():uc.mem_write(node,struct.pack('<IIII',*children[key],key))
  # Complete node payloads: vector fields at node+24, node+28, node+32.
  for key,node in nodes.items():
   first=heap+0x8000+(key%128)*32 if key%3 else 0
   uc.mem_write(node+24,struct.pack('<III',first,first+32 if first else 0,first+64 if first else 0))
  seed=bytes(uc.mem_read(heap,0x10000));snapshots=[]
  for exports,tree in [(orig,0x63fc2a8),(new,new['LoadoutLookupTree'])]:
   uc.mem_write(heap,seed);uc.mem_write(tree,struct.pack('<III',0,head,nil)+b'\xa5'*4+struct.pack('<I',len(keys)));events.clear()
   h.invoke(exports[symbol]);snapshots.append((bytes(uc.mem_read(heap,0x10000)),bytes(uc.mem_read(tree,20)),list(events)))
  assert snapshots[0]==snapshots[1],iteration
  assert len(snapshots[0][2])==len(keys)*2
  count+=1
 report=dict(status='passed',differential_calls=count,trees=300,source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files+['src/loadout_tree.hpp','src/loadout_map.hpp','tests/verify_loadout_free_x86.py']},not_verified=['Inconsistent zero-size/nonempty iterator-erase fallback','Original tree initialization/insertion integration','Native runtime','Exact instruction matching'])
 (ROOT/'analysis/loadout-free-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} Loadout Free calls across 300 shapes, exact release order and full tree/payload memory')
if __name__=='__main__':main()
