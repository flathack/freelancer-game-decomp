#!/usr/bin/env python3
"""Compare original x86 CFLIDMaker methods with newly compiled x86 C++ methods.
Runtime allocator/deallocator and ASCII _strlwr are emulated substitutes.
"""
import hashlib,json,pathlib,random,struct,subprocess
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_ECX
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
EXPECTED='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
SYMS={
 'CreateID':'?CreateID@@YAIPBD@Z',
 'Initialize':'?Initialize@CFLIDMaker@@QAEHXZ',
 'CreateStaticID':'?CreateStaticID@CFLIDMaker@@QAEIPBD@Z',
 'GetInstance':'?GetInstance@CFLIDMaker@@SAPAV1@XZ',
 'Shutdown':'?Shutdown@CFLIDMaker@@SAXXZ',
 'AllocateObjectID':'?AllocateObjectID@CFLIDMaker@@QAEIXZ',
 'singleton':'?m_pTheMaker@CFLIDMaker@@2PAV1@A',
 'assignment':'??4CFLIDMaker@@QAEAAV0@ABV0@@Z',
 'constructor':'??0CFLIDMaker@@IAE@XZ',
 'destructor':'??1CFLIDMaker@@IAE@XZ',
 'Update':'?Update@FLIDCRCState@@QAEXE@Z',
}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==EXPECTED
 build=ROOT/'build';build.mkdir(exist_ok=True)
 commands=[]
 for source,out in [('src/create_id.cpp','cfl_id_maker.obj'),('tests/fixtures/flid_x86_runtime.cpp','flid_x86_runtime.obj')]:
  cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-c',str(ROOT/source),'-o',str(build/out)]
  commands.append(cmd);subprocess.run(cmd,check=True)
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x10000000',f'/out:{build}/cfl_id_maker.dll',str(build/'cfl_id_maker.obj'),str(build/'flid_x86_runtime.obj')]
 cmd += ['/export:'+s+(',DATA' if key=='singleton' else '') for key,s in SYMS.items()]
 commands.append(cmd);subprocess.run(cmd,check=True)
 uc=Uc(UC_ARCH_X86,UC_MODE_32);pe=pefile.PE(str(SOURCE));newpe=pefile.PE(str(build/'cfl_id_maker.dll'))
 def load(p):
  base=p.OPTIONAL_HEADER.ImageBase;uc.mem_map(base,(p.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);uc.mem_write(base,p.get_memory_mapped_image())
  return {s.name.decode():base+s.address for s in p.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
 orig=load(pe);rebuilt=load(newpe)
 stack,inputs,heap,stop,lower=0x20100000,0x20200000,0x20300000,0x20400000,0x20400010
 for addr in (stack,inputs,heap,stop):uc.mem_map(addr,0x10000)
 uc.mem_write(0x6399350,struct.pack('<I',lower))
 allocated=[];freed=[];cursor=heap;fail_next=False
 def word(addr):return struct.unpack('<I',uc.mem_read(addr,4))[0]
 def put(addr,value):uc.mem_write(addr,struct.pack('<I',value))
 def ret(value):
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EAX,value);uc.reg_write(UC_X86_REG_EIP,word(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
 def hook(uc,addr,size,user):
  nonlocal cursor,fail_next
  sp=uc.reg_read(UC_X86_REG_ESP)
  if addr==0x6391abc:
   n=word(sp+4);assert n in [8,0x41c]
   if fail_next:fail_next=False;ret(0);return
   p=cursor;cursor+=(n+15)&~15;allocated.append((p,n));ret(p)
  elif addr==0x6391a7a:freed.append(word(sp+4));ret(0)
  elif addr==lower:
   p=word(sp+4)
   for i in range(256):
    b=uc.mem_read(p+i,1)[0]
    if not b:break
    assert b<128
    if 65<=b<=90:uc.mem_write(p+i,bytes([b+32]))
   else:raise AssertionError('Unterminated input')
   ret(p)
 uc.hook_add(UC_HOOK_CODE,hook)
 def invoke(address,args=(),this=None):
  sp=stack+0x8000;uc.mem_write(sp,struct.pack('<'+'I'*(1+len(args)),stop,*args));uc.reg_write(UC_X86_REG_ESP,sp)
  if this is not None:uc.reg_write(UC_X86_REG_ECX,this)
  uc.emu_start(address,stop,count=1000000)
  assert uc.reg_read(UC_X86_REG_EIP)==stop,'Did not return'
  assert uc.reg_read(UC_X86_REG_ESP)==sp+4+(4*len(args) if this is not None else 0),'Calling convention mismatch'
  return uc.reg_read(UC_X86_REG_EAX)
 def call(table,key,args=(),this=None):return invoke(table[SYMS[key]],args,this)
 o=call(orig,'GetInstance');r=call(rebuilt,'GetInstance')
 assert bytes(uc.mem_read(o,8))==bytes(uc.mem_read(r,8))==struct.pack('<II',0,1)
 rng=random.Random(2003)
 vectors=[None,b'',b'LI01',b'li01_01_base',b'A'*255]+[bytes(rng.randrange(1,128) for _ in range(rng.randrange(256))) for _ in range(500)]
 for value in vectors:
  p=0
  if value is not None:uc.mem_write(inputs,value+b'\0');p=inputs
  assert call(orig,'CreateID',(p,))==call(rebuilt,'CreateID',(p,))
  a=bytes(uc.mem_read(word(o),0x41c));b=bytes(uc.mem_read(word(r),0x41c))
  assert a[:0x416]==b[:0x416] and a[0x418:]==b[0x418:],'CRC state mismatch'
 assert len(allocated)==4,'Singleton or Initialize did not cache allocation'
 before=len(allocated)
 assert call(orig,'Initialize',this=o)==call(rebuilt,'Initialize',this=r)==1
 assert len(allocated)==before
 counter_cases=0
 for seed in [0,1,0x3ffffffe,0x3fffffff,0x7fffffff,0xfffffffe,0xffffffff]:
  put(o+4,seed);put(r+4,seed)
  for _ in range(4):
   assert call(orig,'AllocateObjectID',this=o)==call(rebuilt,'AllocateObjectID',this=r)
   assert word(o+4)==word(r+4);counter_cases+=1
 # Invoke all four byte-update branches with controlled configuration/state.
 update_cases=0
 for reflected in [0,1]:
  for direct in [0,1]:
   for _ in range(100):
    width=rng.randrange(8,33);remainder=rng.randrange(2**32);byte=rng.randrange(256)
    for ptr in [word(o),word(r)]:
     put(ptr+0x404,width);put(ptr+0x418,remainder);uc.mem_write(ptr+0x414,bytes([reflected,direct]))
    invoke(0x630d3b0,(byte,),word(o));call(rebuilt,'Update',(byte,),word(r))
    assert word(word(o)+0x418)==word(word(r)+0x418);update_cases+=1
 # Constructor, shallow assignment and protected destructor at their real x86 ABI.
 temporary=inputs+0x1000
 for table,offset in [(orig,0),(rebuilt,32)]:
  destination=temporary+offset;source=destination+16
  uc.mem_write(destination,b'\xff'*8)
  assert call(table,'constructor',this=destination)==destination
  assert bytes(uc.mem_read(destination,8))==struct.pack('<II',0,1)
  uc.mem_write(source,struct.pack('<II',0,0xffffffff))
  assert call(table,'assignment',(source,),destination)==destination
  assert bytes(uc.mem_read(destination,8))==bytes(uc.mem_read(source,8))
  # Allocation failure in Initialize leaves the state null and returns false.
  fail_next=True
  assert call(table,'Initialize',this=destination)==0
  assert word(destination)==0
  assert call(table,'Initialize',this=destination)==1
  ptr=word(destination);before=len(freed)
  call(table,'destructor',this=destination)
  assert freed[before:]==[ptr]
 original_state,rebuilt_state=word(o),word(r)
 before=len(freed);call(orig,'Shutdown');call(rebuilt,'Shutdown')
 assert freed[before:]==[original_state,o,rebuilt_state,r]
 assert word(orig[SYMS['singleton']])==word(rebuilt[SYMS['singleton']])==0
 before=len(freed);call(orig,'Shutdown');call(rebuilt,'Shutdown');assert len(freed)==before
 for table in [orig,rebuilt]:
  fail_next=True;assert call(table,'GetInstance')==0;assert word(table[SYMS['singleton']])==0
  p=call(table,'GetInstance');assert bytes(uc.mem_read(p,8))==struct.pack('<II',0,1)
  call(table,'Shutdown')
 report=dict(status='passed',original_sha256=EXPECTED,compiled_dll_sha256=digest(build/'cfl_id_maker.dll'),
             source_hashes={p:digest(ROOT/p) for p in ['src/create_id.cpp','src/cfl_id_maker.hpp','tests/fixtures/flid_x86_runtime.cpp']},
             hash_and_full_crc_state_cases=len(vectors),object_counter_cases=counter_cases,byte_update_cases=update_cases,
             lifetime_checks=['constructor','shallow assignment','cached Initialize','Initialize allocation failure and retry','destructor','Shutdown free order','idempotent Shutdown','GetInstance allocation failure and retry'],
             commands=commands,mocks=['Allocator/deallocator','ASCII _strlwr'],
             not_verified=['Exact instruction matching','CRT non-ASCII/locale behavior','CreateID allocation-failure logging','Complete game linking/runtime'])
 (ROOT/'analysis/flid-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f'PASS x86: {len(vectors)} hash/state cases, {counter_cases} counter cases, {update_cases} byte-update cases, lifetime/failure checks')
if __name__=='__main__':main()
