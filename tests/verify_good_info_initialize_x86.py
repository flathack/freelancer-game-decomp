#!/usr/bin/env python3
"""GoodInfo initialization: full storage, three sentinels and actual null-name ID."""
import hashlib,json,pathlib,random,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/good_info_initialize.cpp','src/create_id.cpp','tests/fixtures/good_info_initialize_runtime.cpp','tests/fixtures/flid_x86_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-good-init.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbol='??0GoodInfo@@QAE@XZ';singleton='?m_pTheMaker@CFLIDMaker@@2PAV1@A';dll=ROOT/'build/good_info_initialize.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1e000000',f'/out:{dll}']+objects+['/export:'+symbol,'/export:'+singleton+',DATA'],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;uc.mem_map(0,4096);heap=0x23000000;uc.mem_map(heap,0x10000);cursor=heap;events=[];rng=random.Random(2003);count=0
 def hook(uc,address,size,user):
  nonlocal cursor
  if address==0x6391abc:
   n=h.word(uc.reg_read(UC_X86_REG_ESP)+4);assert n in [40,8,0x41c];p=cursor;cursor+=(n+15)&~15;events.append((n,p));h.return_stub(p)
 uc.hook_add(UC_HOOK_CODE,hook)
 for byte in range(256):
  for offset in [0,1,3]:
   seed=rng.randbytes(256);memory=rng.randbytes(2048);obj=h.scratch+offset;results=[]
   for exports in [orig,new]:
    cursor=heap;events.clear();uc.mem_write(heap,memory);uc.mem_write(h.scratch,seed);uc.mem_write(h.stack+0x7f00,b'\xa5'*256);uc.mem_write(h.stack+0x8000-17,bytes([byte]));h.write_word(exports[singleton],0)
    returned=h.invoke(exports[symbol],(),obj)
    results.append((returned,bytes(uc.mem_read(h.scratch,256)),bytes(uc.mem_read(heap,2048)),list(events)))
   assert results[0]==results[1],(byte,offset);assert results[0][0]==obj;count+=1
 report=dict(status='passed',differential_calls=count,opaque_values=256,storage_extent=192,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['tests/verify_good_info_initialize_x86.py']},not_verified=['Native/reconstructed GoodInfo vtable dispatch','Full GoodInfo polymorphic class layout','Allocation/exception failure','Storage/stack aliasing','Native CRT','Exact instruction matching'])
 (ROOT/'analysis/good-info-initialize-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} GoodInfo constructors, full guarded storage/sentinels/CRC heap/allocation sequence')
if __name__=='__main__':main()
