#!/usr/bin/env python3
"""Complete reconstructed Loadout tree operation sequences against original code."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/loadout_tree_initialize.cpp','src/loadout_lookup.cpp','src/loadout_insert.cpp','src/loadout_insert_unique.cpp','src/loadout_iterator.cpp','src/loadout_erase.cpp','src/loadout_free.cpp','src/loadout_map.cpp','src/subobject_id.cpp','tests/fixtures/loadout_map_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-tree-integrated.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbols=['loadout_tree_initialize','loadout_tree_emplace','loadout_tree_erase','?Get@Loadout@@YAPBUMap@1@I@Z','?Free@Loadout@@YAXXZ'];dll=ROOT/'build/loadout_tree_integrated.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1a000000',f'/out:{dll}']+objects+['/export:'+s for s in symbols]+['/export:LoadoutLookupTree,DATA'],check=True)
 h=X86Harness();original_exports=h.load(original);new=h.load(dll);uc=h.uc;uc.mem_map(0,4096);heap=0x23000000;uc.mem_map(heap,0x20000);cursor=heap;events=[];out=h.scratch;value=out+128;state=out+256;rng=random.Random(2003);counts=dict(initialize=0,insert=0,lookup=0,erase=0,free=0)
 contexts=[(0x63fc2a8,True),(new['LoadoutLookupTree'],False)]
 def hook(uc,address,size,user):
  nonlocal cursor
  if address==0x6391abc:
   size=h.word(uc.reg_read(UC_X86_REG_ESP)+4);p=cursor;cursor+=(max(size,1)+15)&~15;events.append(('new',size,p));h.return_stub(p)
  elif address==0x6391a7a:events.append(('free',h.word(uc.reg_read(UC_X86_REG_ESP)+4)));h.return_stub(0)
 uc.hook_add(UC_HOOK_CODE,hook)
 def pair(kind,args=()):
  nonlocal cursor
  seed=bytes(uc.mem_read(heap,0x20000));tree_seed=bytes(uc.mem_read(contexts[1][0],20));start=cursor;results=[]
  for tree,baseline in contexts:
   uc.mem_write(heap,seed);uc.mem_write(tree,tree_seed);cursor=start;events.clear();uc.mem_write(out,b'\xa5'*16)
   addresses={'initialize':0x6311de0,'insert':0x6311e50,'erase':0x6312060,'lookup':original_exports[symbols[3]],'free':original_exports[symbols[4]]} if baseline else dict(zip(['initialize','insert','erase','lookup','free'],[new[s] for s in symbols]))
   returned=h.invoke(addresses[kind],args,tree if kind in ['initialize','insert','erase'] else None)
   if kind=='initialize':assert returned==tree
   results.append((returned if kind=='lookup' else None,bytes(uc.mem_read(heap,0x20000)),bytes(uc.mem_read(tree,20)),bytes(uc.mem_read(out,16)),cursor,list(events)))
  assert results[0]==results[1],(kind,args)
  counts[kind]+=1;return results[0][0]
 for trial in range(60):
  uc.mem_write(heap,rng.randbytes(0x20000));cursor=heap;uc.mem_write(contexts[1][0],b'\xa5'*20);uc.mem_write(state,bytes([rng.randrange(256),rng.randrange(256)]));pair('initialize',(state,state+1))
  keys=list(dict.fromkeys([0,0xffffffff,0x80000000]+[rng.randrange(2**32) for _ in range(rng.randrange(5,50))]));order=keys+keys[:5];rng.shuffle(order)
  for key in order:
   payload=bytearray(rng.randbytes(28));struct.pack_into('<I',payload,0,key);length=rng.randrange(4);first=heap+0x18000 if length else 0;struct.pack_into('<III',payload,12,first,first+length*32,first+length*32);uc.mem_write(value,bytes(payload));pair('insert',(out,value));assert pair('lookup',(key,))
  assert pair('lookup',(next(i for i in range(1,100) if i not in keys),))==0
  rng.shuffle(keys)
  for key in keys[:len(keys)//2]:
   payload_pointer=pair('lookup',(key,));pair('erase',(out,payload_pointer-16));assert pair('lookup',(key,))==0
  if trial%2==0:
   for tree,_ in contexts:h.write_word(tree+16,0)
  pair('free');pair('free')
 report=dict(status='passed',operation_counts=counts,sequences=60,differential_calls=sum(counts.values()),fixture_sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['src/loadout_tree.hpp','src/loadout_rb.hpp','src/loadout_map.hpp','tests/verify_loadout_tree_integrated_x86.py']},not_verified=['Native heap and allocation failure','Global native startup','Complete Loadout file loading','Exact instruction matching'])
 (ROOT/'analysis/loadout-tree-integrated-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {sum(counts.values())} integrated tree calls over 60 sequences; {counts}')
if __name__=='__main__':main()
