#!/usr/bin/env python3
"""Original Loadout node construction/insertion: full state and heap footprint."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/loadout_insert_unique.cpp','src/loadout_insert.cpp','src/loadout_map.cpp','src/subobject_id.cpp','tests/fixtures/loadout_map_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-insert.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbol='loadout_tree_emplace';dll=ROOT/'build/loadout_emplace.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1f000000',f'/out:{dll}']+objects+['/export:'+symbol],check=True)
 h=X86Harness();h.load(original);new=h.load(dll);uc=h.uc;heap=0x23000000;uc.mem_map(heap,0x10000);uc.mem_map(0,4096);head=heap;nil=heap+64;tree=h.scratch;out=tree+64;value=tree+128;events=[];cursor=heap+256;count=0;rng=random.Random(2003)
 def hook(uc,address,size,user):
  nonlocal cursor
  if address==0x6391abc:
   n=h.word(uc.reg_read(UC_X86_REG_ESP)+4);p=cursor;cursor+=(max(n,1)+15)&~15;events.append(('new',n,p));h.return_stub(p)
  elif address==0x6391a7a:events.append(('free',h.word(uc.reg_read(UC_X86_REG_ESP)+4)));h.return_stub(0)
 uc.hook_add(UC_HOOK_CODE,hook)
 for trial in range(150):
  uc.mem_write(heap,rng.randbytes(0x10000));cursor=heap+256;uc.mem_write(head,struct.pack('<IIII',head,nil,head,0));uc.mem_write(head+40,b'\0\0');uc.mem_write(nil,struct.pack('<IIII',nil,nil,nil,0));uc.mem_write(nil+40,b'\1\1');uc.mem_write(tree,struct.pack('<III',0,head,nil)+bytes([trial%2])+b'\0'*7)
  keys=[0,0xffffffff,0x80000000]+[rng.randrange(2**32) for _ in range(rng.randrange(5,65))];keys=list(dict.fromkeys(keys));keys+=keys[:];rng.shuffle(keys)
  if trial==0:keys.sort()
  elif trial==1:keys.sort(reverse=True)
  for key in keys:
   parent=head;node=h.word(head+4)
   while node!=nil:parent=node;node=h.word(node+(0 if key<h.word(node+12) else 8))
   marker=parent if parent!=head and key<h.word(parent+12) and rng.randrange(2) else nil
   payload=bytearray(rng.randbytes(28));struct.pack_into('<I',payload,0,key);length=rng.randrange(4);first=heap+0xc000 if length else 0
   struct.pack_into('<III',payload,12,first,first+length*32,first+length*32);uc.mem_write(value,bytes(payload))
   seed=bytes(uc.mem_read(heap,0x10000));tree_seed=bytes(uc.mem_read(tree,20));start=cursor;results=[]
   for address in [0x6311e50,new[symbol]]:
    uc.mem_write(heap,seed);uc.mem_write(tree,tree_seed);cursor=start;events.clear();uc.mem_write(out,b'\xa5'*8);h.invoke(address,(out,value),tree)
    results.append((bytes(uc.mem_read(heap,0x10000)),bytes(uc.mem_read(tree,20)),bytes(uc.mem_read(out,8)),cursor,list(events)))
   assert results[0]==results[1],(trial,key,[(r[1].hex(),r[2],r[4]) for r in results]);count+=1
 report=dict(status='passed',differential_calls=count,trees=150,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['src/loadout_rb.hpp','src/loadout_tree.hpp','src/loadout_map.hpp','tests/verify_loadout_emplace_x86.py']},not_verified=['Hinted insertion API','Output/value aliasing','Allocation failure and exception unwinding','Native heap','Exact instruction matching'])
 (ROOT/'analysis/loadout-emplace-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} Loadout unique/multi inserts, duplicate results and full heap/tree state')
if __name__=='__main__':main()
