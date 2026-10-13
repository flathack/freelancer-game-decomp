#!/usr/bin/env python3
"""Actual Goods initialization followed by both indexes' unique/multi insertions."""
import hashlib,json,pathlib,random,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/archetype_id.cpp','src/archetype_equipment_lookup.cpp','tests/fixtures/archetype_lookup_runtime.cpp','src/good_info_list_initialize.cpp','src/good_index_insert.cpp','src/good_index_emplace.cpp','tests/fixtures/good_info_list_initialize_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-good-index.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 ids=['?Get'+kind+'ID@Archetype@@YAIABUID_String@@@Z' for kind in ['Asteroid','DynamicAsteroid','Equipment','Ship','Simple','Solar']]
 equipment='?GetEquipment@Archetype@@YAPAUEquipment@1@I@Z'
 ctor='??0GoodInfoList@@QAE@XZ';dll=ROOT/'build/archetype_lookup.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1e000000',f'/out:{dll}']+objects+['/export:'+ctor,'/export:good_index_emplace','/export:EquipmentArchetypeTree,DATA','/export:'+equipment]+['/export:'+symbol for symbol in ids],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;uc.mem_map(0,4096);heap=0x23000000;uc.mem_map(heap,0x10000);cursor=heap;events=[];rng=random.Random(2003);count=0;lookup_calls=0;id_calls=0;errors=[]
 uc.mem_write(h.scratch+512,(h.scratch+768).to_bytes(4,'little'));h.write_word(0x6399028,h.scratch+512)
 def hook(uc,address,size,user):
  nonlocal cursor
  if address==h.scratch+768:
   sp=uc.reg_read(UC_X86_REG_ESP);args=[h.word(sp+4+i*4) for i in range(5)]
   def string(p):
    data=bytearray()
    while uc.mem_read(p,1)[0]:data.extend(uc.mem_read(p,1));p+=1
    return bytes(data)
   errors.append((args[0],string(args[1]),string(args[2]),args[3],args[4]));h.return_stub(0)
  elif address==0x6391abc:
   n=h.word(uc.reg_read(UC_X86_REG_ESP)+4);assert n in [12,24];p=cursor;cursor+=(n+15)&~15;events.append((n,p));h.return_stub(p)
 uc.hook_add(UC_HOOK_CODE,hook)
 for case in range(100):
  seed=rng.randbytes(256);memory=rng.randbytes(16384);keys=[0,0xffffffff,0x80000000]+[rng.randrange(32) if case%2 else rng.getrandbits(32) for _ in range(77)];snapshots=[]
  for exports,address in [(orig,0x63221d0),(new,new['good_index_emplace'])]:
   cursor=heap;events.clear();uc.mem_write(heap,memory);uc.mem_write(h.scratch,seed);uc.mem_write(h.stack+0x8000-17,bytes([case]));h.invoke(exports[ctor],(),h.scratch);states=[];expected=[{},{}]
   for i,key in enumerate(keys):
    tree=h.scratch+(12 if i%2 else 32);uc.mem_write(tree+12,bytes([case%3]));out=h.scratch+128;value=h.scratch+160;uc.mem_write(out,b'\xa5'*8);h.write_word(value,key);h.write_word(value+4,0x28000000+i*192)
    returned=h.invoke(address,(out,value),tree)
    which=i%2;expected[which].setdefault(key,0x28000000+i*192)
    queries=[]
    for offset,index in [(32,0),(12,1)]:
     tree_storage=bytes(uc.mem_read(h.scratch+offset,20))
     uc.mem_write(0x63fbad4 if exports is orig else new['EquipmentArchetypeTree'],tree_storage)
     for query in [key,0,0xffffffff,0x80000000,(key+1)&0xffffffff,(key-1)&0xffffffff]:
      errors.clear();found=h.invoke(exports[equipment],(query,));assert found==expected[index].get(query,0)
      assert len(errors)==(0 if query in expected[index] else 1)
      queries.append((found,list(errors)))
    accesses=[]
    for symbol in ids:
     accesses.append(h.invoke(exports[symbol],(value,)));assert accesses[-1]==key
    states.append((queries,accesses,returned,bytes(uc.mem_read(h.scratch,256)),bytes(uc.mem_read(heap,16384)),list(events)))
   snapshots.append(states)
  assert snapshots[0]==snapshots[1],case;count+=len(keys)
 report=dict(status='passed',differential_calls=count*12,id_accessor_calls=count*6,insertion_calls=count,sequences=100,indexes_per_sequence=2,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['src/good_index_rb.hpp','tests/verify_archetype_lookup_x86.py']},not_verified=['Goods file loading','Native heap/CRT','Allocation failures','Aliased input/tree/result','Exact instruction matching'])
 (ROOT/'analysis/archetype-lookup-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count*12} Equipment lookups/error logs and {count*6} ID alias calls')
if __name__=='__main__':main()
