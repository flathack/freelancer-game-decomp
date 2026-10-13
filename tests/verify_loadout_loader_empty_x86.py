#!/usr/bin/env python3
"""Differential INI file opening, ownership, recognition and error callbacks."""
import hashlib,json,pathlib,struct,subprocess,sys
import pefile
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 sys.path.insert(0,str(ROOT/'tools'))
 from build_ini_fixture import main as build_fixture
 build_fixture(include_loadout=True,include_hash=True,include_cache=True,include_loader=True)
 methods=['?Load@Loadout@@YAHPBD_N@Z'];test_dll=ROOT/'build/loadout-loader-fixture/freelancer-ini-fixture.dll'
 h=X86Harness();orig=h.load(SOURCE);new=h.load(test_dll);uc=h.uc;uc.mem_map(0,4096);uc.mem_map(0x21000000,0x200000)
 heap=0x21000000;empty=h.scratch+0x5000;h.write_word(0x63991d0,empty);h.write_word(0x63991c0,empty+4);h.write_word(empty+4,0xffffffff)
 imports={0x63991a8:('assign_object',12),0x6399198:('erase',8),0x63991d4:('grow',8),0x63991bc:('split',0),0x63991b8:('tidy',4),0x63991a4:('assign',8),0x63991b0:('copy',4),0x6399330:('memmove',12),0x639932c:('free',4),0x6399328:('malloc',4),0x63990d4:('open',28),0x6399144:('mapping',24),0x639913c:('size',8),0x6399138:('map',20),0x6399130:('unmap',4),0x6399140:('close_handle',4)}
 dispatch={0x63114d0:('refresh',0)};events=[];allocations={};stage=0;file_bytes=b'controlled-file-data';view=h.scratch+0x7000;uc.mem_write(view,file_bytes)
 for index,(iat,(name,bytes_)) in enumerate(imports.items()):
  address=h.stop+0x200+16*index;dispatch[address]=(name,bytes_);h.write_word(iat,address)
 fatal=h.stop+0x600;h.write_word(0x6399058,empty+8);h.write_word(empty+8,fatal);dispatch[fatal]=('fatal',8)
 logger=h.stop+0x640;h.write_word(0x6399028,empty+12);h.write_word(empty+12,logger);dispatch[logger]=('log',20)
 comparator=h.stop+0x660;h.write_word(0x639902c,comparator);dispatch[comparator]=('compare',8)
 def text(p,n=None):
  if n is not None:return bytes(uc.mem_read(p,n))
  out=bytearray()
  while True:
   b=uc.mem_read(p,1)[0]
   if not b:return bytes(out)
   out.append(b);p+=1
 def allocate(n,kind):
  nonlocal heap
  p=heap;heap+=(n+15)&~15;allocations[p]=(kind,n);uc.mem_write(p,b'\x00'*n);return p
 def refs(p):return uc.mem_read(p-1,1)[0]
 def release(p):
  if p:
   r=refs(p)
   if r in [0,255]:events.append(('string_free',text(p)));allocations.pop(p-1,None)
   else:uc.mem_write(p-1,bytes([r-1]))
 def tidy(obj,release_old=True):
  if release_old:release(h.word(obj+4))
  for offset in [4,8,12]:h.write_word(obj+offset,0)
 def grow(obj,n,trim):
  p=h.word(obj+4);length=h.word(obj+8);capacity=h.word(obj+12)
  if not n:
   if trim:tidy(obj)
   elif p:h.write_word(obj+8,0);uc.mem_write(p,b'\0')
   return 0
  if p and refs(p) in [0,255] and capacity>=n and not (trim and capacity>n):return 1
  old=text(p,min(length,n)) if p else b''
  fresh=allocate(n+2,'string');uc.mem_write(fresh+1,old+b'\0');release(p)
  h.write_word(obj+4,fresh+1);h.write_word(obj+8,min(length,n));h.write_word(obj+12,n);return 1
 def split(obj):
  p=h.word(obj+4)
  if p and refs(p) not in [0,255]:
   n=h.word(obj+8);old=text(p,n);fresh=allocate(n+2,'string');uc.mem_write(fresh+1,old+b'\0');release(p)
   h.write_word(obj+4,fresh+1);h.write_word(obj+12,n)
 def ret(value,cleanup):
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EAX,value&0xffffffff);uc.reg_write(UC_X86_REG_ESP,sp+4+cleanup);uc.reg_write(UC_X86_REG_EIP,h.word(sp))
 def hook(uc,address,size,user):
  if address==0x6391a7a:
   p=h.word(uc.reg_read(UC_X86_REG_ESP)+4);events.append(('string_free',text(p+1)));allocations.pop(p,None);ret(0,0);return
  if address not in dispatch:return
  name,bytes_=dispatch[address];sp=uc.reg_read(UC_X86_REG_ESP);obj=uc.reg_read(UC_X86_REG_ECX)
  args=[h.word(sp+4+i) for i in range(0,bytes_,4)];result=0
  if name=='log':events.append(('load_error',args[0],text(args[1]),text(args[2]),args[3],text(args[4])))
  elif name=='compare':
   a=text(args[0]).lower();b=text(args[1]).lower();result=(a>b)-(a<b)
  elif name=='refresh':events.append(('refresh',))
  elif name=='fatal':assert args[0]==200;events.append(('fatal',text(args[1])))
  elif name=='assign_object':
   src,start,n=args;assert start==0 and n==0xffffffff
   if src==obj:split(obj);result=obj
   else:
    length=h.word(src+8);p=h.word(src+4)
    if length and refs(p)<254:
     tidy(obj);h.write_word(obj+4,p);h.write_word(obj+8,length);h.write_word(obj+12,h.word(src+12));uc.mem_write(p-1,bytes([refs(p)+1]))
    else:
     data=text(p,length) if p else b''
     if grow(obj,length,True):uc.mem_write(h.word(obj+4),data+b'\0');h.write_word(obj+8,length)
    result=obj
  elif name=='erase':
   start,n=args;split(obj)
   length=h.word(obj+8)
   if n and start<length:
    assert start==0 and n==0xffffffff;grow(obj,0,False)
   result=obj
  elif name=='grow':result=grow(obj,args[0],bool(args[1]))
  elif name=='split':split(obj)
  elif name=='tidy':tidy(obj,bool(args[0]))
  elif name=='assign':
   source,n=args;data=text(source,n)
   if grow(obj,n,True):uc.mem_write(h.word(obj+4),data+b'\0');h.write_word(obj+8,n)
   result=obj
  elif name=='copy':
   old=text(h.word(obj+4),min(h.word(obj+8),args[0]));grow(obj,args[0],True);uc.mem_write(h.word(obj+4),old+b'\0')
  elif name=='memmove':
   dst,src,n=args
   if n:uc.mem_write(dst,text(src,n))
   result=dst
  elif name=='free':
   p=args[0];kind,n=allocations.pop(p,('unknown',0));events.append(('free',kind,n));result=0
  elif name=='malloc':result=allocate(args[0],'data')
  elif name=='open':
   assert args[1:]==[0x80000000,1,0,3,0,0];events.append(('open',text(args[0])));result=0xffffffff if stage==1 else 0x11111111
  elif name=='mapping':
   assert args==[0x11111111,0,2,0,0,0];events.append(('mapping',));result=0 if stage==2 else 0x22222222
  elif name=='size':assert args==[0x11111111,0];events.append(('size',));result=len(file_bytes)
  elif name=='map':assert args==[0x22222222,4,0,0,len(file_bytes)];events.append(('map',));result=0 if stage==3 else view
  elif name=='unmap':assert args[0]==view;events.append(('unmap',));result=1
  elif name=='close_handle':events.append(('close_handle',args[0]));result=1
  cleanup=bytes_ if name in ['assign_object','erase','grow','split','tidy','assign','copy','open','mapping','size','map','unmap','close_handle'] else 0
  ret(result,cleanup)
 uc.hook_add(UC_HOOK_CODE,hook)
 obj=h.scratch;nameptr=obj+0x8000;uc.mem_write(nameptr,b'controlled.ini\0');count=0;symbol=methods[0]
 payloads=[b'',b'[Other]\nignored=1',b'BINI'+struct.pack('<II',1,12),b'BINI'+struct.pack('<II',1,12)+b'\0']
 real_files=[]
 for file_bytes in payloads:
  uc.mem_write(view,file_bytes or b'\0')
  for mode in [0,1]:
   for stage in [0,1,2,3]:
    for fatal_arg in [0,1]:
     snapshots=[]
     for exports in [orig,new]:
      heap=0x21000000;allocations.clear();events.clear();uc.mem_write(obj,b'\xa5'*0x1568);uc.mem_write(obj+0x1564,bytes([mode]))
      for off in [0,0x1428]:
       for i,v in enumerate([0x12345678,0,0,0,0x777,0x888,view,19,3]):h.write_word(obj+off+i*4,v)
      returned=h.invoke(exports[symbol],(nameptr,fatal_arg));assert returned==0
      snapshots.append((returned,bytes(uc.mem_read(obj,0x1568)),bytes(uc.mem_read(0x21000000,heap-0x21000000)),list(events),dict(allocations)))
     assert snapshots[0]==snapshots[1],(len(file_bytes),mode,stage,fatal_arg,snapshots)
     count+=1
 report=dict(status='passed',original_sha256=HASH,compiled_dll_sha256=digest(test_dll),differential_calls=count,real_files=real_files,methods=methods,source_hashes={p:digest(ROOT/p) for p in ['src/loadout_load.cpp','tests/fixtures/loadout_loader_runtime.cpp','tools/build_ini_fixture.py','tests/verify_loadout_loader_empty_x86.py']},external_dependencies='MSVCP60 COW, Win32 mapping, fatal handler and progress callback modeled',not_verified=['Native OS/CRT','Non-returning fatal handler','Allocation or exception failure','Exact instruction matching'])
 (ROOT/'analysis/loadout-loader-empty-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} empty/other-header Loadout loads, file failure stages, exact heap/resource/diagnostic effects')
if __name__=='__main__':main()
