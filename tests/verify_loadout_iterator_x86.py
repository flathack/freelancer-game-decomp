#!/usr/bin/env python3
"""Original lower-bound Loadout tree lookup against reconstructed code."""
import hashlib,json,pathlib,random,struct,subprocess
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 source=ROOT/'src/loadout_iterator.cpp';obj=ROOT/'build/loadout_iterator.obj';dll=ROOT/'build/loadout_iterator.dll';symbol='@loadout_tree_next@4'
 subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-c',str(source),'-o',str(obj)],check=True)
 subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1b000000',f'/out:{dll}',str(obj),'/export:'+symbol],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;heap=0x23000000;uc.mem_map(heap,0x10000);rng=random.Random(2003);count=0
 for iteration in range(300):
  keys=sorted(set([0,0xffffffff,0x80000000]+[rng.randrange(2**32) for _ in range(rng.randrange(70))]))
  order=keys[:];rng.shuffle(order);head=heap;nil=heap+64;nodes={key:heap+128+i*64 for i,key in enumerate(keys)};children={key:[nil,nil,nil] for key in keys};root=nil
  for key in order:
   if root==nil:root=nodes[key];children[key][1]=head;continue
   current=next(k for k,v in nodes.items() if v==root)
   while True:
    side=0 if key<current else 2
    if children[current][side]==nil:children[current][side]=nodes[key];children[key][1]=nodes[current];break
    current=next(k for k,v in nodes.items() if v==children[current][side])
  uc.mem_write(heap,b'\xa5'*0x10000);uc.mem_write(head,struct.pack('<IIII',nodes[keys[0]],root,nodes[keys[-1]],0));uc.mem_write(nil,struct.pack('<IIII',nil,nil,nil,0))
  for key,node in nodes.items():uc.mem_write(node,struct.pack('<IIII',*children[key],key))
  uc.mem_write(nil+41,b'\1');uc.mem_write(head+41,b'\0')
  for node in nodes.values():uc.mem_write(node+41,b'\0')
  before=bytes(uc.mem_read(heap,0x10000));iterator=h.scratch
  for index,key in enumerate(keys):
   results=[]
   for address in [0x63126d0,new[symbol]]:
    h.write_word(iterator,nodes[key]);h.invoke(address,(),iterator);results.append(h.word(iterator))
   expected=nodes[keys[index+1]] if index+1<len(keys) else head
   assert results[0]==results[1]==expected,(iteration,key,results,expected)
   count+=1
  assert bytes(uc.mem_read(heap,0x10000))==before
 report=dict(status='passed',differential_calls=count,trees=300,source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/loadout_iterator.cpp','src/loadout_tree.hpp','tests/verify_loadout_iterator_x86.py']},not_verified=['Integration into iterator erase','Incrementing end/invalid iterators','Native runtime','Exact instruction matching'])
 (ROOT/'analysis/loadout-iterator-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} Loadout iterator steps across 300 shapes, exact successors/end and unchanged tree')
if __name__=='__main__':main()
