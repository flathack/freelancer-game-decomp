#!/usr/bin/env python3
"""Actual Goods initialization followed by both indexes' unique/multi insertions."""
import hashlib,json,pathlib,random,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/good_info_list_initialize.cpp','src/good_index_insert.cpp','src/good_index_emplace.cpp','tests/fixtures/good_info_list_initialize_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-good-index.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 ctor='??0GoodInfoList@@QAE@XZ';dll=ROOT/'build/good_index.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1e000000',f'/out:{dll}']+objects+['/export:'+ctor,'/export:good_index_emplace'],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;uc.mem_map(0,4096);heap=0x23000000;uc.mem_map(heap,0x10000);cursor=heap;events=[];rng=random.Random(2003);count=0
 def hook(uc,address,size,user):
  nonlocal cursor
  if address==0x6391abc:
   n=h.word(uc.reg_read(UC_X86_REG_ESP)+4);assert n in [12,24];p=cursor;cursor+=(n+15)&~15;events.append((n,p));h.return_stub(p)
 uc.hook_add(UC_HOOK_CODE,hook)
 for case in range(100):
  seed=rng.randbytes(256);memory=rng.randbytes(16384);keys=[0,0xffffffff,0x80000000]+[rng.randrange(32) if case%2 else rng.getrandbits(32) for _ in range(77)];snapshots=[]
  for exports,address in [(orig,0x63221d0),(new,new['good_index_emplace'])]:
   cursor=heap;events.clear();uc.mem_write(heap,memory);uc.mem_write(h.scratch,seed);uc.mem_write(h.stack+0x8000-17,bytes([case]));h.invoke(exports[ctor],(),h.scratch);states=[]
   for i,key in enumerate(keys):
    tree=h.scratch+(12 if i%2 else 32);uc.mem_write(tree+12,bytes([case%3]));out=h.scratch+128;value=h.scratch+160;uc.mem_write(out,b'\xa5'*8);h.write_word(value,key);h.write_word(value+4,0x28000000+i*192)
    returned=h.invoke(address,(out,value),tree)
    states.append((returned,bytes(uc.mem_read(h.scratch,256)),bytes(uc.mem_read(heap,16384)),list(events)))
   snapshots.append(states)
  assert snapshots[0]==snapshots[1],case;count+=len(keys)
 report=dict(status='passed',differential_calls=count,sequences=100,indexes_per_sequence=2,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['src/good_index_rb.hpp','tests/verify_good_index_emplace_x86.py']},not_verified=['Goods file loading','Native heap/CRT','Allocation failures','Aliased input/tree/result','Exact instruction matching'])
 (ROOT/'analysis/good-index-emplace-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} Goods index insertions after actual reconstructed initialization')
if __name__=='__main__':main()
