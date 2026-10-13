#!/usr/bin/env python3
"""GoodInfo destruction: populated list unlinking and allocator callback states."""
import hashlib,json,pathlib,random,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/good_info_destroy.cpp','tests/fixtures/good_info_destroy_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-good-destroy.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbol='??1GoodInfo@@QAE@XZ';dll=ROOT/'build/good_info_destroy.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1e000000',f'/out:{dll}']+objects+['/export:'+symbol],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;uc.mem_map(0,4096);heap=0x23000000;uc.mem_map(heap,0x10000);events=[];rng=random.Random(2003);count=0
 def hook(uc,address,size,user):
  if address==0x6391a7a:
   p=h.word(uc.reg_read(UC_X86_REG_ESP)+4);events.append((p,bytes(uc.mem_read(h.scratch,256)),bytes(uc.mem_read(heap,4096))));h.return_stub(0)
 uc.hook_add(UC_HOOK_CODE,hook)
 for case in range(500):
  seed=rng.randbytes(256);memory=rng.randbytes(4096);obj=h.scratch;uc.mem_write(obj,seed);uc.mem_write(heap,memory);cursor=heap
  for offset in [148,160,172]:
   length=rng.randrange(16);nodes=[cursor+48*i for i in range(length+1)];cursor+=48*(length+1);head=nodes[0];h.write_word(obj+offset+4,head);h.write_word(obj+offset+8,rng.getrandbits(32))
   for i,node in enumerate(nodes):
    h.write_word(node,nodes[(i+1)%len(nodes)]);h.write_word(node+4,nodes[(i-1)%len(nodes)])
  initial=bytes(uc.mem_read(obj,256));initial_heap=bytes(uc.mem_read(heap,4096));results=[]
  for exports in [orig,new]:
   events.clear();uc.mem_write(obj,initial);uc.mem_write(heap,initial_heap);h.invoke(exports[symbol],(),obj)
   results.append((bytes(uc.mem_read(obj,256)),bytes(uc.mem_read(heap,4096)),list(events)))
  assert results[0]==results[1],case;count+=1
 report=dict(status='passed',differential_calls=count,storage_extent=192,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['tests/verify_good_info_destroy_x86.py']},not_verified=['Native/reconstructed GoodInfo vtable dispatch','Full GoodInfo polymorphic class layout','Allocation/exception failure','Storage/stack aliasing','Native CRT','Exact instruction matching'])
 (ROOT/'analysis/good-info-destroy-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} GoodInfo destructors, full guarded storage/heap/free-call states')
if __name__=='__main__':main()
