#!/usr/bin/env python3
"""Differential EquipDesc ABI, mutation, padding and floating-return checks."""
import hashlib,json,pathlib,random,re,struct,subprocess
import pefile
from unicorn import UC_HOOK_CODE
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 pe=pefile.PE(str(SOURCE));symbols=[s.name.decode() for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name and
    (re.match(r'\?[^@]+@EquipDesc@@',s.name.decode()) or re.match(r'\?\?[01489MO]EquipDesc@@',s.name.decode()))]
 build=ROOT/'build';build.mkdir(exist_ok=True);commands=[]
 for source,out in [('src/equip_desc.cpp','equip_desc.obj'),('tests/fixtures/equip_desc_x86_runtime.cpp','equip_desc_runtime.obj'),('src/string_cache.cpp','equip_desc_string_cache.obj'),('src/common_constants.cpp','common_constants.obj'),('tests/fixtures/string_cache_x86_runtime.cpp','equip_desc_string_runtime.obj')]:
  cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-mno-sse','-mno-sse2','-fno-builtin','-c',str(ROOT/source),'-o',str(build/out)]
  subprocess.run(cmd,check=True);commands.append(cmd)
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x11000000',f'/out:{build}/equip_desc.dll',str(build/'equip_desc.obj'),str(build/'equip_desc_runtime.obj'),str(build/'equip_desc_string_cache.obj'),str(build/'common_constants.obj'),str(build/'equip_desc_string_runtime.obj')]+['/export:'+s+(',DATA' if 'CARGO_BAY_HP_NAME' in s else '') for s in symbols]
 subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(build/'equip_desc.dll');uc=h.uc
 # Execute original and reconstructed global initializers through real StringAlloc.
 uc.mem_map(0,4096);uc.mem_map(0x21000000,0x10000)
 heap=0x21000000
 equipment=h.scratch+0x2000
 calls=[]
 def hook(uc,addr,size,user):
  nonlocal heap
  from unicorn.x86_const import UC_X86_REG_ESP
  sp=uc.reg_read(UC_X86_REG_ESP)
  if addr==0x06391abc:
   size=h.word(sp+4);assert size in [20,24]
   ptr=heap;heap+=(size+15)&~15;h.return_stub(ptr)
  elif addr==h.stop+64:
   def string(ptr):
    value=bytearray()
    while True:
     byte=uc.mem_read(ptr,1)[0]
     if not byte:return bytes(value).lower()
     value.append(byte);ptr+=1
   a=string(h.word(sp+4));b=string(h.word(sp+8));h.return_stub(((a>b)-(a<b))&0xffffffff)
  elif addr==0x062f9370:
   from unicorn.x86_const import UC_X86_REG_ESP
   calls.append(h.word(uc.reg_read(UC_X86_REG_ESP)+4));h.return_stub(equipment)
 uc.hook_add(UC_HOOK_CODE,hook)
 h.write_word(0x639902c,h.stop+64)
 h.invoke(0x6309a60)
 crt_callbacks=h.initialize_crt(build/'equip_desc.dll');assert crt_callbacks==1
 original_bay=h.word(orig['?CARGO_BAY_HP_NAME@EquipDesc@@2UCacheString@@B'])
 rebuilt_bay=h.word(new['?CARGO_BAY_HP_NAME@EquipDesc@@2UCacheString@@B'])
 assert bytes(uc.mem_read(original_bay,4))==bytes(uc.mem_read(rebuilt_bay,4))==b'BAY\0'
 def object_bytes(ptr,bay):
  blob=bytearray(uc.mem_read(ptr,32))
  if struct.unpack_from('<I',blob,8)[0]==bay:struct.pack_into('<I',blob,8,0xfffffffe)
  return bytes(blob)
 rng=random.Random(2003);o=h.scratch;r=h.scratch+64;other=h.scratch+128;count=0;tested=set()
 def pair(symbol,args=(),mask=None,floating=False):
  nonlocal count
  a=h.invoke(orig[symbol],args,o,floating);b=h.invoke(new[symbol],args,r,floating)
  if mask is not None:a&=mask;b&=mask
  # this-reference results point into separate instances.
  if symbol.startswith('??0') or symbol.startswith('??4') or symbol.startswith('?get_hardpoint'):
   a-=o;b-=r
  if not (symbol.startswith('?set_') or symbol.startswith('?make_internal')):
   assert a==b,(symbol,a,b)
  assert object_bytes(o,original_bay)==object_bytes(r,rebuilt_bay),symbol
  count+=1;tested.add(symbol)
 ctor='??0EquipDesc@@QAE@XZ';copy='??0EquipDesc@@QAE@ABU0@@Z';assignment='??4EquipDesc@@QAEAAU0@ABU0@@Z'
 for _ in range(100):
  poison=bytes(rng.randrange(256) for _ in range(32));uc.mem_write(o,poison);uc.mem_write(r,poison);pair(ctor)
  blob=bytearray(rng.randrange(256) for _ in range(32));blob[12]=rng.randrange(2);blob[24]=rng.randrange(2)
  uc.mem_write(other,bytes(blob));pair(copy,(other,));pair(assignment,(other,))
 setters={'set_id':'G','set_arch_id':'I','set_count':'H','set_owner':'H','set_status':'M','set_equipped':'_N','set_temporary':'_N'}
 for _ in range(100):
  for name,typ in setters.items():
   value=rng.randrange(2) if typ=='_N' else rng.randrange(65536) if typ=='G' else rng.randrange(2**32)
   pair(f'?{name}@EquipDesc@@QAEX{typ}@Z',(value,))
  h.write_word(other,rng.randrange(2**32));pair('?set_hardpoint@EquipDesc@@QAEXABUCacheString@@@Z',(other,))
  for name,typ,mask in [('get_id','G',65535),('get_arch_id','I',None),('get_count','H',None),('get_owner','H',None),('is_equipped','_N',255),('get_temporary','_N',255),('is_internal','_N',255)]:pair(f'?{name}@EquipDesc@@QBE{typ}XZ',mask=mask)
  pair('?get_hardpoint@EquipDesc@@QBEABUCacheString@@XZ')
  for op in ['8','9','M','O']:pair(f'??{op}EquipDesc@@QBE_NABU0@@Z',(other,),mask=255)
  pair('?make_internal@EquipDesc@@QAEXXZ')
 # Finite floating status getter; compare exact x87 return value, not host doubles.
 for bits in [0,0x80000000,0x3f800000,0xbf800000,1,0x7f7fffff]:
  h.write_word(o+16,bits);h.write_word(r+16,bits);pair('?get_status@EquipDesc@@QBEMXZ',floating=True)
 cargo='?get_cargo_space_occupied@EquipDesc@@QBEMXZ';differences=[]
 for index in range(200):
  internal=index%3!=0;arch=0 if index%5==0 else index+1;items=rng.randrange(-2**31,2**31)
  volume=struct.unpack('<f',struct.pack('<f',rng.uniform(-1000,1000)))[0]
  for ptr,bay in [(o,original_bay),(r,rebuilt_bay)]:
   h.write_word(ptr+8,bay if internal else 0);h.write_word(ptr+4,arch);h.write_word(ptr+20,items)
  uc.mem_write(equipment+0x5c,struct.pack('<f',volume));before=len(calls)
  a=h.invoke(orig[cargo],this=o,float_result=True);b=h.invoke(new[cargo],this=r,float_result=True)
  assert len(calls)-before==(2 if internal and arch else 0),'Archetype lookup branch mismatch'
  if a!=b:differences.append(dict(count=items,volume=volume,original_x87=a.hex(),compiled_x87=b.hex()))
  tested.add(cargo)
 assert not differences, 'Extended x87 return fidelity remains unresolved'
 report=dict(status='passed_with_x87_abi_shim',original_sha256=HASH,compiled_dll_sha256=digest(build/'equip_desc.dll'),
             source_hashes={p:digest(ROOT/p) for p in ['src/equip_desc.cpp','src/equip_desc.hpp','src/string_cache.cpp','src/string_cache.hpp','src/common_constants.cpp','tests/fixtures/equip_desc_x86_runtime.cpp','tests/fixtures/string_cache_x86_runtime.cpp']},
             passing_calls=count,covered_method_symbols=sorted(tested),cargo_cases=200,cargo_extended_precision_differences=len(differences),
             differences=differences,commands=commands,
             crt_initializers_executed=crt_callbacks,mocks=['operator new succeeds','ASCII stricmp','Archetype::GetEquipment returns controlled equipment'],
             not_verified=['Exact code matching','Real archetype database','Production interning and lookup bindings'])
 (ROOT/'analysis/equipdesc-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f'{count} exact ABI/state calls pass across {len(tested)} methods; 200 full-x87 cargo return/lookup cases pass (temporary ABI assembly shim).')
if __name__=='__main__':main()
