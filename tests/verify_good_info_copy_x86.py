#!/usr/bin/env python3
"""GoodInfo destruction: populated list unlinking and allocator callback states."""
import hashlib,json,pathlib,random,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/good_info_destroy.cpp','src/good_info_assign.cpp','tests/fixtures/good_info_assign_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-good-assign.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbol='??0GoodInfo@@QAE@ABU0@@Z';dll=ROOT/'build/good_info_copy.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1e000000',f'/out:{dll}']+objects+['/export:'+symbol,'/export:??1GoodInfo@@QAE@XZ'],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;uc.mem_map(0,4096);heap=0x23000000;uc.mem_map(heap,0x10000);events=[];rng=random.Random(2003);count=0
 cursor=heap+8192
 def hook(uc,address,size,user):
  nonlocal cursor
  if address==0x6391a7a:
   p=h.word(uc.reg_read(UC_X86_REG_ESP)+4);events.append(('free',p));h.return_stub(0)
  elif address==0x6391abc:
   n=h.word(uc.reg_read(UC_X86_REG_ESP)+4);assert n==40;p=cursor;cursor+=48;events.append(('allocate',n,p));h.return_stub(p)
 uc.hook_add(UC_HOOK_CODE,hook)
 for case in range(1000):
  obj=h.scratch;source=obj+256;uc.mem_write(obj,rng.randbytes(512));uc.mem_write(heap,rng.randbytes(16384));pos=heap
  for target in [obj,source]:
   length=rng.randrange(96);uc.mem_write(target+8,bytes(rng.randrange(1,256) for _ in range(length))+b'\0')
   for offset in [148,160,172]:
    n=rng.randrange(12);nodes=[pos+48*i for i in range(n+1)];pos+=48*(n+1);h.write_word(target+offset+4,nodes[0]);h.write_word(target+offset+8,rng.getrandbits(32))
    for i,node in enumerate(nodes):
     h.write_word(node,nodes[(i+1)%len(nodes)]);h.write_word(node+4,nodes[(i-1)%len(nodes)])
  initial=bytes(uc.mem_read(obj,512));initial_heap=bytes(uc.mem_read(heap,16384));results=[]
  for exports in [orig,new]:
   cursor=heap+8192;events.clear();uc.mem_write(obj,initial);uc.mem_write(heap,initial_heap);returned=h.invoke(exports[symbol],(source,),obj)
   copied=(returned,bytes(uc.mem_read(obj,512)),bytes(uc.mem_read(heap,16384)),list(events))
   events.clear();h.invoke(exports['??1GoodInfo@@QAE@XZ'],(),obj)
   results.append((copied,bytes(uc.mem_read(obj,512)),bytes(uc.mem_read(heap,16384)),list(events)))
  assert results[0]==results[1],case;count+=1
 report=dict(status='passed',differential_calls=count,storage_extent=192,lifecycle_sequences=count,destructor_calls=count,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['tests/verify_good_info_copy_x86.py']},not_verified=['Native/reconstructed GoodInfo vtable dispatch','Full GoodInfo polymorphic class layout','Allocation/exception failure','Partially overlapping objects or shared lists','Native CRT','Intermediate callback observations','Exact instruction matching'])
 (ROOT/'analysis/good-info-copy-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} GoodInfo copy constructors, full guarded storage/heap/allocation events and destruction')
if __name__=='__main__':main()
