#!/usr/bin/env python3
"""Equipment append and Cargo combine, including legacy nontermination."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/equip_desc_vector_append.cpp','src/equip_desc_vector_add.cpp','tests/fixtures/equip_collection_runtime.cpp','tests/fixtures/loadout_map_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-add.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-mno-sse','-mno-sse2','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbol='?append@EquipDescVector@@QAEXABU1@@Z';dll=ROOT/'build/equip_vector_append.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1c000000',f'/out:{dll}']+objects+['/export:'+symbol],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;heap=0x23000000;uc.mem_map(heap,0x10000);uc.mem_map(0,4096);vector=h.scratch;value=vector+64;hp=vector+256;uc.mem_write(hp,b'BAY\0bay\0OTHER\0');compare=h.stop+256;h.write_word(0x639902c,compare);events=[];count=0;rng=random.Random(2003)
 def text(p):
  out=b''
  while uc.mem_read(p,1)[0]:out+=bytes(uc.mem_read(p,1));p+=1
  return out
 def hook(uc,address,size,user):
  sp=uc.reg_read(UC_X86_REG_ESP)
  if address==0x6391abc:events.append(('new',h.word(sp+4)));h.return_stub(heap+0x8000)
  elif address==0x6391a7a:events.append(('free',h.word(sp+4)));h.return_stub(0)
  elif address==compare:
   a=text(h.word(sp+4)).lower();b=text(h.word(sp+8)).lower();h.return_stub(((a>b)-(a<b))&0xffffffff)
 uc.hook_add(UC_HOOK_CODE,hook)
 def pair(seed,obj,input_,limit=1000000,self_append=False):
  nonlocal count
  results=[]
  for exports in [orig,new]:
   uc.mem_write(heap,seed);uc.mem_write(vector,obj);uc.mem_write(value,input_);events.clear()
   try:h.invoke(exports[symbol],(vector if self_append else value,),vector,max_instructions=limit);state='returned'
   except AssertionError as e:assert str(e)=='Missing return';state='instruction_limit'
   results.append((state,bytes(uc.mem_read(vector,16)),bytes(uc.mem_read(value,16)),bytes(uc.mem_read(heap,0x10000)),list(events)))
  if self_append and state=='instruction_limit':assert results[0][0]==results[1][0]
  else:assert results[0]==results[1],(obj.hex(),input_.hex())
  count+=1;return results[0][0]
 for old in range(12):
  for added in range(12):
   for cap in [old,old+added,old+added+5]:
    seed=rng.randbytes(0x10000);first=heap if cap else 0;source=heap+0x4000 if added else 0
    obj=struct.pack('<IIII',0x12345678,first,first+old*32,first+cap*32);input_=struct.pack('<IIII',0xabcdef01,source,source+added*32,source+added*32)
    assert pair(seed,obj,input_)=='returned'
 nonterminating=0
 for old in [1,2,3]:
  obj=struct.pack('<IIII',0,heap,heap+old*32,heap+old*32)
  assert pair(rng.randbytes(0x10000),obj,b'\xa5'*16,2000,True)=='instruction_limit';nonterminating+=1
 report=dict(status='passed',differential_calls=count,nonreturning_cases=nonterminating,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['src/equip_desc_collections.hpp','tests/verify_equip_vector_append_x86.py']},not_verified=['Full self-append memory evolution beyond instruction budget','Partial vector/storage aliasing','Full Loadout loader integration','Native CRT/heap','Exact instruction matching'])
 (ROOT/'analysis/equip-vector-append-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} vector append cases, including {nonterminating} original nonreturning paths')
if __name__=='__main__':main()
