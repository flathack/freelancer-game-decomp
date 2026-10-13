#!/usr/bin/env python3
"""Equipment append and Cargo combine, including legacy nontermination."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/equip_desc_vector_add.cpp','tests/fixtures/equip_collection_runtime.cpp','tests/fixtures/loadout_map_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-add.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-mno-sse','-mno-sse2','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbol='?add_equipment_item@EquipDescVector@@QAEHABUEquipDesc@@_N@Z';dll=ROOT/'build/equip_vector_add.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1c000000',f'/out:{dll}']+objects+['/export:'+symbol],check=True)
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
 def pair(seed,obj,input_,combine,limit=1000000):
  nonlocal count
  results=[]
  for exports in [orig,new]:
   uc.mem_write(heap,seed);uc.mem_write(vector,obj);uc.mem_write(value,input_);events.clear()
   try:ret=h.invoke(exports[symbol],(value,combine),vector,max_instructions=limit);state='returned'
   except AssertionError as e:assert str(e)=='Missing return';ret=None;state='instruction_limit'
   results.append((state,ret,bytes(uc.mem_read(vector,16)),bytes(uc.mem_read(heap,0x10000)),list(events)))
  assert results[0]==results[1],(combine,results[0][:3],results[1][:3]);count+=1;return results[0][0]
 for old in range(10):
  for capacity in [old,old+1,old+5]:
   for combine in [0,1]:
    seed=rng.randbytes(0x10000);first=heap if capacity else 0;obj=struct.pack('<IIII',0,first,first+old*32,first+capacity*32);incoming=bytearray(rng.randbytes(32));struct.pack_into('<I',incoming,4,0xabcdef);struct.pack_into('<I',incoming,8,hp)
    # Existing IDs differ, so combine falls through to append.
    seed=bytearray(seed)
    for i in range(old):struct.pack_into('<I',seed,i*32+4,i)
    assert pair(bytes(seed),obj,bytes(incoming),combine)=='returned'
 statuses=[0,0x80000000,0x3e800000,0x3f000000,0x3f400000,0x3f7fffff,0x3f800000,0x40000000,0xbf800000,0x7f800000,0xff800000,0x7fc00001,0x7f800001]
 for a in statuses:
  for b in statuses:
   for _ in range(5):
    seed=bytearray(rng.randbytes(0x10000));incoming=bytearray(rng.randbytes(32))
    for payload in [seed,incoming]:struct.pack_into('<I',payload,4,7);struct.pack_into('<I',payload,8,hp);payload[24]=255;struct.pack_into('<I',payload,28,99)
    struct.pack_into('<I',seed,16,a);struct.pack_into('<I',incoming,16,b);struct.pack_into('<I',incoming,8,hp+4)
    assert pair(bytes(seed),struct.pack('<IIII',0,heap,heap+32,heap+64),bytes(incoming),1)=='returned'
 nonterminating=0
 for mismatch in [24,28,8]:
  seed=bytearray(rng.randbytes(0x10000));incoming=bytearray(seed[:32]);struct.pack_into('<I',seed,4,7);struct.pack_into('<I',incoming,4,7);struct.pack_into('<I',seed,8,hp);struct.pack_into('<I',incoming,8,hp);seed[24]=incoming[24]=0;struct.pack_into('<I',seed,28,0);struct.pack_into('<I',incoming,28,0)
  if mismatch==24:incoming[24]=1
  elif mismatch==28:struct.pack_into('<I',incoming,28,1)
  else:struct.pack_into('<I',incoming,8,hp+8)
  assert pair(bytes(seed),struct.pack('<IIII',0,heap,heap+32,heap+64),bytes(incoming),1,50000)=='instruction_limit';nonterminating+=1
 report=dict(status='passed',differential_calls=count,nonreturning_cases=nonterminating,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['src/equip_desc_collections.hpp','tests/verify_equip_vector_add_x86.py']},not_verified=['Aliased append input and vector storage','Full Loadout loader integration','Native CRT/heap','Exact instruction matching'])
 (ROOT/'analysis/equip-vector-add-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} append/merge cases, including {nonterminating} original nonreturning paths')
if __name__=='__main__':main()
