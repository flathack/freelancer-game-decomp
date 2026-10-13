#!/usr/bin/env python3
"""Original SubObjectID counters: full wraparound and byte write footprints."""
import hashlib,json,pathlib,random,struct,subprocess
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 source=ROOT/'src/subobject_id.cpp';obj=ROOT/'build/subobject_id.obj';dll=ROOT/'build/subobject_id.dll'
 symbols=[];families=[]
 for name,method,initial in [('EquipIdMaker','CreateEquipID',0x21),('CollGroupIdMaker','CreateGroupID',3),('ShieldIdMaker','CreateShieldID',0xfff0)]:
  names=[f'??0{name}@SubObjectID@@QAE@XZ',f'?Reset@{name}@SubObjectID@@QAEXXZ',f'?{method}@{name}@SubObjectID@@QAEGXZ',f'??4{name}@SubObjectID@@QAEAAV01@ABV01@@Z'];symbols+=names;families.append((names,initial))
 subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-c',str(source),'-o',str(obj)],check=True)
 subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1c000000',f'/out:{dll}',str(obj)]+['/export:'+s for s in symbols],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;base=h.scratch;target=base+8;count=0;rng=random.Random(2003)
 def pair(symbol,seed,args=(),return_kind=None):
  nonlocal count
  results=[]
  for exports in [orig,new]:
   uc.mem_write(base,seed);ret=h.invoke(exports[symbol],args,target)
   results.append((ret&65535 if return_kind=='word' else ret if return_kind=='pointer' else None,bytes(uc.mem_read(base,64))))
  assert results[0]==results[1],(symbol,args,results)
  count+=1;return results[0]
 for family,(names,initial) in enumerate(families):
  for pattern in [0,0xa5,255]:
   for symbol in names[:2]:
    _,data=pair(symbol,bytes([pattern])*64);assert struct.unpack_from('<H',data,8)[0]==initial
  seeds=range(65536) if family==0 else [0,1,2,3,0x20,0x21,0xffef,0xfff0,0xfffe,0xffff]+[rng.randrange(65536) for _ in range(300)]
  for value in seeds:
   seed=bytearray(b'\xa5'*64);struct.pack_into('<H',seed,8,value);ret,data=pair(names[2],bytes(seed),return_kind='word');assert ret==(value+1)&65535 and struct.unpack_from('<H',data,8)[0]==ret
  for offset in [8,9,16,31]:
   for _ in range(20):
    seed=rng.randbytes(64);ret,data=pair(names[3],seed,(base+offset,),'pointer');assert ret==target and data[8:10]==seed[offset:offset+2]
 report=dict(status='passed',differential_calls=count,export_count=len(symbols),exports=symbols,exhaustive_equipment_counter_inputs=65536,source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/subobject_id.cpp','src/subobject_id.hpp','tests/verify_subobject_id_x86.py']},not_verified=['Integration into Loadout::Map and world objects','Native execution','Exact instruction matching'])
 (ROOT/'analysis/subobject-id-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} calls across 12 SubObjectID exports, exhaustive 16-bit increment and full guarded writes')
if __name__=='__main__':main()
