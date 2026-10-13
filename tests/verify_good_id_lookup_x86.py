#!/usr/bin/env python3
"""Original lower-bound Loadout tree lookup against reconstructed code."""
import hashlib,json,pathlib,random,struct,subprocess
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 source=ROOT/'src/good_archetype_lookup.cpp';obj=ROOT/'build/loadout_lookup.obj';dll=ROOT/'build/good_id_lookup.dll';symbol='?find_by_archetype@GoodList@@YAPBUGoodInfo@@I@Z';combine='?arch_is_combinable@@YA_NI@Z'
 subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-c',str(source),'-o',str(obj)],check=True)
 second=ROOT/'build/good_id_lookup.obj';subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-c',str(ROOT/'src/good_id_lookup.cpp'),'-o',str(second)],check=True)
 extra=['?find_by_id@GoodList@@YAPBUGoodInfo@@I@Z','?Good2Arch@@YAII@Z','?Arch2Good@@YAII@Z']
 subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1b000000',f'/out:{dll}',str(obj),str(second),'/export:GoodIDTree,DATA']+['/export:'+n for n in extra]+['/export:'+symbol,'/export:GoodArchetypeTree,DATA','/export:'+combine],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;heap=0x23000000;uc.mem_map(heap,0x10000);rng=random.Random(2003);count=0
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
  uc.mem_write(heap,b'\xa5'*0x10000);uc.mem_write(head,struct.pack('<IIII',nil,root,nil,0));uc.mem_write(nil,struct.pack('<IIII',nil,nil,nil,0))
  for key,node in nodes.items():uc.mem_write(node,struct.pack('<IIII',*children[key],key))
  goods={}
  for i,(key,node) in enumerate(nodes.items()):
   ptr=heap+0x6000+i*128 if rng.randrange(5) else 0;goods[key]=ptr;h.write_word(node+16,ptr)
   if ptr:uc.mem_write(ptr+112,bytes([rng.randrange(256)]));h.write_word(ptr+72,rng.randrange(2**32));h.write_word(ptr+80,rng.randrange(2**32))
  for tree in [0x63fab94,new['GoodArchetypeTree'],0x63fab80,new['GoodIDTree']]:uc.mem_write(tree,struct.pack('<III',0,head,nil))
  before=bytes(uc.mem_read(heap,0x10000));queries=keys+[0,1,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]+[rng.randrange(2**32) for _ in range(50)]
  for query in queries:
   a=h.invoke(orig[symbol],(query,));b=h.invoke(new[symbol],(query,));expected=goods.get(query,0)
   assert a==b==expected,(iteration,query,a,b,expected);count+=1
   flag=uc.mem_read(expected+112,1)[0] if expected else 0
   a=h.invoke(orig[combine],(query,))&255;b=h.invoke(new[combine],(query,))&255;assert a==b==flag;count+=1
   expected_values=[expected,h.word(expected+80) if expected else 0,h.word(expected+72) if expected else 0]
   for name,want in zip(extra,expected_values):
    a=h.invoke(orig[name],(query,));b=h.invoke(new[name],(query,));assert a==b==want,(name,query,a,b,want);count+=1
  assert bytes(uc.mem_read(heap,0x10000))==before
 # Every noncanonical flag byte passes through raw AL unchanged.
 for flag in range(256):
  key=next(k for k,p in goods.items() if p);ptr=goods[key];uc.mem_write(ptr+112,bytes([flag]))
  a=h.invoke(orig[combine],(key,))&255;b=h.invoke(new[combine],(key,))&255;assert a==b==flag;count+=1
 report=dict(status='passed',differential_calls=count,trees=300,source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/good_id_lookup.cpp','src/good_archetype_lookup.cpp','src/loadout_tree.hpp','tests/verify_good_id_lookup_x86.py']},not_verified=['GoodList database creation and Loadout loader integration','Native runtime','Exact instruction matching'])
 (ROOT/'analysis/good-id-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} Goods ID/archetype mapping and lookup calls across 300 shapes, exact metadata/pointers')
if __name__=='__main__':main()
