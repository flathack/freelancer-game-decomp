#!/usr/bin/env python3
"""Equipment collection searches: duplicate IDs, cursor semantics and const exports."""
import hashlib,json,pathlib,random,struct,subprocess
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 source=ROOT/'src/equip_desc_collection_search.cpp';obj=ROOT/'build/equip_collection_search.obj';dll=ROOT/'build/equip_collection_search.dll'
 symbols=['?traverse_equipment_type@EquipDescVector@@QAEPAUEquipDesc@@IPBU2@@Z','?traverse_equipment_type@EquipDescList@@QAEPAUEquipDesc@@IPBU2@@Z','?traverse_equipment_type@EquipDescList@@QBEPBUEquipDesc@@IPBU2@@Z','?find_equipment_item@EquipDescList@@QAEPAUEquipDesc@@G@Z','?find_equipment_item@EquipDescList@@QBEPBUEquipDesc@@G@Z']
 subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-c',str(source),'-o',str(obj)],check=True);subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1b000000',f'/out:{dll}',str(obj)]+['/export:'+s for s in symbols],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;heap=0x23000000;uc.mem_map(heap,0x10000);vector=h.scratch;linked=vector+32;head=heap;array=heap+0x1000;rng=random.Random(2003);count=0
 def pair(symbol,args,obj,expected):
  nonlocal count
  a=h.invoke(orig[symbol],args,obj);b=h.invoke(new[symbol],args,obj);assert a==b==expected,(symbol,args,a,b,expected);count+=1
 for trial in range(250):
  n=rng.randrange(33);archs=[rng.choice([0,1,2,3,0x80000000,0xffffffff]) for _ in range(n)];ids=[rng.choice([0,1,2,33,65535]) for _ in range(n)];nodes=[heap+128+i*64 for i in range(n)]
  uc.mem_write(heap,rng.randbytes(0x10000));uc.mem_write(vector,struct.pack('<IIII',0,array,array+n*32,array+n*32));uc.mem_write(linked,struct.pack('<III',0,head,n));uc.mem_write(head,struct.pack('<II',nodes[0] if n else head,nodes[-1] if n else head))
  for i,node in enumerate(nodes):
   uc.mem_write(node,struct.pack('<II',nodes[i+1] if i+1<n else head,nodes[i-1] if i else head));payload=bytearray(rng.randbytes(32));struct.pack_into('<H',payload,2,ids[i]);struct.pack_into('<I',payload,4,archs[i]);uc.mem_write(node+8,bytes(payload));uc.mem_write(array+i*32,bytes(payload))
  before=bytes(uc.mem_read(heap,0x10000));objects=bytes(uc.mem_read(vector,44))
  for arch in [0,1,2,3,4,0x80000000,0xffffffff]:
   for index in [-1]+list(range(n)):
    matches=[i for i in range(n) if archs[i]==arch]
    following=matches if index==-1 else [i for i in matches if i>index] if index in matches else []
    expected=following[0] if following else None
    pair(symbols[0],(arch,0 if index==-1 else array+index*32),vector,0 if expected is None else array+expected*32)
    for symbol in symbols[1:3]:pair(symbol,(arch,0 if index==-1 else nodes[index]+8),linked,0 if expected is None else nodes[expected]+8)
   pair(symbols[0],(arch,heap+0x9000),vector,0)
   for symbol in symbols[1:3]:pair(symbol,(arch,heap+0x9000),linked,0)
  for id_ in [0,1,2,33,34,65535]:
   expected=nodes[ids.index(id_)]+8 if id_ in ids else 0
   for symbol in symbols[3:]:pair(symbol,(id_,),linked,expected)
  assert bytes(uc.mem_read(heap,0x10000))==before and bytes(uc.mem_read(vector,44))==objects
 report=dict(status='passed',differential_calls=count,collection_shapes=250,exports=symbols,source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/equip_desc_collection_search.cpp','src/equip_desc_collections.hpp','src/equip_desc.hpp','tests/verify_equip_collection_search_x86.py']},not_verified=['Cargo merge/list mutation integration','Malformed/cyclic collections','Native execution','Exact instruction matching'])
 (ROOT/'analysis/equip-collection-search-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} collection searches across five exports, exact cursor/ID semantics and unchanged memory')
if __name__=='__main__':main()
