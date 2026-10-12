#!/usr/bin/env python3
"""Verify FileMap memory/BINI reader methods against their original x86 exports."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 methods=['??0FileMap@@QAE@XZ','?open_memory@FileMap@@QAE_NPBXI@Z','?get_file_name@FileMap@@QBEPBDXZ','?get_file_length@FileMap@@QBEIXZ','?eof@FileMap@@QBE_NXZ','?tell@FileMap@@QBEIXZ','?seek@FileMap@@QAEXI@Z','?request_pointer@FileMap@@QAEPAXAAI@Z','?read@FileMap@@QAEIPAXI@Z']
 methods+=['?read_ptr@FileMap@@QAE_NAAPAUBINI_'+name+'@@@Z' for name in ['Header','Block','Value']]
 commands=[];build=ROOT/'build'
 for source,out in [('src/file_map.cpp','file_map.obj'),('tests/fixtures/file_map_x86_runtime.cpp','file_map_runtime.obj')]:
  cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/source),'-o',str(build/out)];subprocess.run(cmd,check=True);commands.append(cmd)
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x13000000',f'/out:{build}/file_map.dll',str(build/'file_map.obj'),str(build/'file_map_runtime.obj')]+['/export:'+n for n in methods]
 subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(build/'file_map.dll');uc=h.uc
 uc.mem_map(0x21000000,0x100000);heap=0x21000000;uc.mem_map(0x22000000,4096)
 # Both images use this controlled CRT malloc entry; no host allocator is executed.
 h.write_word(0x6399328,h.stop+64);h.write_word(0x63991d0,h.scratch+0x4000)
 def hook(uc,addr,size,user):
  nonlocal heap
  if addr==h.stop+64:
   n=h.word(uc.reg_read(UC_X86_REG_ESP)+4);assert 0<n<=256
   ptr=heap;heap+=(n+15)&~15;h.return_stub(ptr)
 uc.hook_add(UC_HOOK_CODE,hook)
 o=h.scratch;r=o+64;input_=o+0x100;odest=o+0x1000;rdest=o+0x2000;oa=o+0x3000;ra=oa+4
 count=0;rng=random.Random(2003);seen=set();truncated=0
 def normalize_result(value,obj):
  ptr=h.word(obj+24)
  return ('data',value-ptr) if ptr and ptr<=value<=ptr+256 else ('raw',value)
 def state(obj):
  b=bytes(uc.mem_read(obj+4,32));return b[:20]+b'\0'*4+b[24:]
 def pair(index,args_o=(),args_r=None,pointer=False,void=False):
  nonlocal count
  if args_r is None:args_r=args_o
  symbol=methods[index];a=h.invoke(orig[symbol],args_o,o);b=h.invoke(new[symbol],args_r,r)
  if symbol.startswith('??0'):assert a==o and b==r
  elif not void:
   if index in [1,4,9,10,11]:a&=255;b&=255
   assert (normalize_result(a,o) if pointer else a)==(normalize_result(b,r) if pointer else b),(symbol,a,b)
  assert state(o)==state(r),(symbol,state(o).hex(),state(r).hex())
  if h.word(o+24):assert bytes(uc.mem_read(h.word(o+24),h.word(o+28)))==bytes(uc.mem_read(h.word(r+24),h.word(r+28)))
  count+=1;seen.add(symbol)
 for size in [0,1,2,3,4,5,11,12,13,31,64,255,256]:
  uc.mem_write(o,b'\xaa'*36);uc.mem_write(r,b'\xaa'*36);pair(0)
  pair(2);pair(3);pair(4);pair(5);pair(6,(0xffffffff,),void=True)
  pair(1,(0,5));pair(1,(input_,0))
  if size:
   blob=bytes(rng.randrange(256) for _ in range(size));uc.mem_write(input_,blob);pair(1,(input_,size))
  for _ in range(60):
   operation=rng.randrange(6);requested=rng.choice([0,1,2,3,4,12,256,0xffffffff])
   if operation==0:pair(6,(rng.choice([0,size//2,size,size+1,0xffffffff]),),void=True)
   elif operation==1:
    h.write_word(oa,requested);h.write_word(ra,requested);pair(7,(oa,),(ra,),pointer=True);assert h.word(oa)==h.word(ra)
   elif operation==2:
    uc.mem_write(odest,b'\xcc'*256);uc.mem_write(rdest,b'\xcc'*256);pair(8,(odest,requested),(rdest,requested));assert bytes(uc.mem_read(odest,256))==bytes(uc.mem_read(rdest,256))
   else:
    h.write_word(oa,0xdeadbeef);h.write_word(ra,0xdeadbeef);pair(operation+6,(oa,),(ra,));assert normalize_result(h.word(oa),o)==normalize_result(h.word(ra),r)
    if not h.word(oa):truncated+=1
   pair(3);pair(4);pair(5)
 # Reopening memory must preserve existing handles/name fields and old allocation.
 pair(0);uc.mem_write(input_,b'old-data');pair(1,(input_,8))
 old_original=h.word(o+24);old_rebuilt=h.word(r+24)
 for obj in [o,r]:h.write_word(obj+16,0x11111111);h.write_word(obj+20,0x22222222)
 uc.mem_write(input_,b'NEW');pair(1,(input_,3))
 assert bytes(uc.mem_read(old_original,8))==bytes(uc.mem_read(old_rebuilt,8))==b'old-data'
 assert h.word(o+16)==h.word(r+16)==0x11111111 and h.word(o+20)==h.word(r+20)==0x22222222
 before=state(o);pair(1,(0,99));pair(1,(input_,0));assert state(o)==before
 # Explicit tail-shortage cases ensure failed typed reads still consume the tail.
 for method,needed in [(9,12),(10,4),(11,3)]:
  for size in range(1,needed+1):
   pair(0);uc.mem_write(input_,b'\x77'*size);pair(1,(input_,size));pair(method,(oa,),(ra,))
   assert h.word(o+32)==h.word(r+32)==size
   assert bool(h.word(oa))==(size==needed)
 report=dict(status='passed',original_sha256=HASH,compiled_dll_sha256=digest(build/'file_map.dll'),
             source_hashes={p:digest(ROOT/p) for p in ['src/file_map.cpp','src/file_map.hpp','tests/fixtures/file_map_x86_runtime.cpp']},
             differential_calls=count,methods=sorted(seen),typed_short_read_cases=16,reopen_preserves_handles_and_old_allocation=True,invalid_open_preserves_state=True,random_truncated_reads=truncated,commands=commands,
             mocks=['malloc succeeds','CRT empty string'],
             not_verified=['Filename MSVC6 COW string operations','OS-backed open/close/handoff','Copy constructor/assignment/destructor','Malloc failure','Overlapping copy buffers','Exact instruction matching'])
 (ROOT/'analysis/filemap-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} differential calls across {len(seen)} FileMap memory/BINI methods')
if __name__=='__main__':main()
