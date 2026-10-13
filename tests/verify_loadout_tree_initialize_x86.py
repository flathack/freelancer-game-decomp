#!/usr/bin/env python3
"""Original Loadout tree initialization: opaque inputs and sentinel footprints."""
import hashlib,json,pathlib,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/loadout_tree_initialize.cpp','tests/fixtures/loadout_map_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-init.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbol='loadout_tree_initialize';dll=ROOT/'build/loadout_tree_initialize.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1a000000',f'/out:{dll}']+objects+['/export:'+symbol],check=True)
 h=X86Harness();h.load(original);new=h.load(dll);uc=h.uc;heap=0x23000000;uc.mem_map(heap,4096);comparator=h.scratch+128;allocator=comparator+1;events=[];count=0
 def hook(uc,address,size,user):
  if address==0x6391abc:
   n=h.word(uc.reg_read(UC_X86_REG_ESP)+4);assert n==44;p=heap+len(events)*64;events.append((n,p));h.return_stub(p)
 uc.hook_add(UC_HOOK_CODE,hook)
 for a in range(256):
  for c in range(256):
   offset=(a+c)%4;tree=h.scratch+offset;uc.mem_write(comparator,bytes([c,a]));results=[]
   for address in [0x6311de0,new[symbol]]:
    uc.mem_write(h.scratch,b'\xa5'*64);uc.mem_write(heap,b'\xcc'*128);events.clear();ret=h.invoke(address,(comparator,allocator),tree)
    results.append((ret,bytes(uc.mem_read(h.scratch,64)),bytes(uc.mem_read(heap,128)),list(events)))
   assert results[0]==results[1],(a,c)
   assert results[0][0]==tree and len(results[0][3])==2;count+=1
 report=dict(status='passed',differential_calls=count,opaque_input_combinations=65536,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['src/loadout_tree.hpp','tests/verify_loadout_tree_initialize_x86.py']},not_verified=['Allocation failure/exception path','Aliased input/object storage','Native heap','Global startup and full Loadout loading','Exact instruction matching'])
 (ROOT/'analysis/loadout-tree-initialize-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} tree constructors, exact guarded object/sentinel bytes and allocation order')
if __name__=='__main__':main()
