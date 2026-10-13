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
 imports={0x6399248:('atoi',4),0x6399350:('strlower',4),0x6399300:('search',8),0x63992f4:('lower',4),0x63992f0:('atof',4),0x63991a8:('assign_object',12),0x6399198:('erase',8),0x63991d4:('grow',8),0x63991bc:('split',0),0x63991b8:('tidy',4),0x63991a4:('assign',8),0x63991b0:('copy',4),0x6399330:('memmove',12),0x639932c:('free',4),0x6399328:('malloc',4),0x63990d4:('open',28),0x6399144:('mapping',24),0x639913c:('size',8),0x6399138:('map',20),0x6399130:('unmap',4),0x6399140:('close_handle',4)}
 dispatch={0x63114d0:('refresh',0)};events=[];allocations={};stage=0;file_bytes=b'controlled-file-data';view=h.scratch+0x7000;uc.mem_write(view,file_bytes)
 for index,(iat,(name,bytes_)) in enumerate(imports.items()):
  address=h.stop+0x200+16*index;dispatch[address]=(name,bytes_);h.write_word(iat,address)
 fatal=h.stop+0x600;h.write_word(0x6399058,empty+8);h.write_word(empty+8,fatal);dispatch[fatal]=('fatal',8)
 logger=h.stop+0x640;h.write_word(0x6399028,empty+12);h.write_word(empty+12,logger);dispatch[logger]=('log',20)
 comparator=h.stop+0x660;h.write_word(0x639902c,comparator);dispatch[comparator]=('compare',8)
 dispatch[0x6391abc]=('operator_new',4);dispatch[0x6391a7a]=('operator_free',4)
 fp=h.scratch+0xa000;stub=h.stop+0x680;uc.mem_write(stub,b'\xdd\x05'+struct.pack('<I',fp)+b'\xc3')
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
  if name=='operator_new':result=allocate(max(args[0],1),'new')
  elif name=='operator_free':allocations.pop(args[0],None)
  elif name=='strlower':uc.mem_write(args[0],text(args[0]).lower()+b'\0');result=args[0]
  elif name=='lower':result=args[0]+32 if 65<=args[0]<=90 else args[0]
  elif name=='search':
   blob=text(args[0])+b'\0';index=blob.find(bytes([args[1]&255]));result=args[0]+index if index>=0 else 0
  elif name=='atof':
   import re
   match=re.match(rb'\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)',text(args[0]));number=float(match.group(1)) if match else 0.;uc.mem_write(fp,struct.pack('<d',number));uc.reg_write(UC_X86_REG_EIP,stub);return
  elif name=='atoi':
   import re
   match=re.match(rb'\s*([+-]?\d+)',text(args[0]));result=int(match.group(1)) if match else 0
  elif name=='log':events.append(('load_error',args[0],text(args[1]),text(args[2]),args[3],text(args[4])))
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
 payloads=[]
 for first,second in [('0.25','0.5'),('0.75','0.5'),('1','0.25'),('0.25','1')]:
  payloads.append(f'[Loadout]\nnickname=combined\ncargo=456,2,,{first},true\ncargo=456,3,,{second},true\n'.encode())
 payloads.append(b'[Loadout]\nnickname=external\ncargo=456,2,HpCargo,0.25,true\ncargo=456,3,HpCargo,0.5,true\n')
 payloads.append(b'[Loadout]\nnickname=equipped\nequip=123,HpWeapon,1\ncargo=456,2,,0.25,true\ncargo=456,3,,0.5,true\n')
 cases=[(p,g) for p in payloads for g in [0,1,255]]
 def maps(tree,arena):
  head=h.word(tree+4);nil=h.word(tree+8)
  def visit(node):
   if node==nil:return []
   begin=h.word(node+24);end=h.word(node+28);items=[]
   for ptr in range(begin,end,32):
    items.append((uc.mem_read(ptr,1)[0],struct.unpack('<H',uc.mem_read(ptr+2,2))[0],h.word(ptr+4),text(h.word(ptr+8)),uc.mem_read(ptr+12,1)[0],h.word(ptr+16),h.word(ptr+20),uc.mem_read(ptr+24,1)[0],h.word(ptr+28)))
   return visit(h.word(node))+[(h.word(node+12),h.word(node+16),struct.unpack('<H',uc.mem_read(node+36,2))[0],items)]+visit(h.word(node+8))
  return visit(h.word(head+4))
 uc.mem_write(obj+0x9000,b'BAY\0');uc.mem_write(obj+0x9100,b'\0\0')
 for file_bytes,goods_flag in cases:
  uc.mem_write(view,file_bytes)
  for flag in [0,1]:
   snapshots=[]
   for exports in [orig,new]:
    heap=0x21000000;allocations.clear();events.clear();stage=0
    baseline=exports is orig;tree=0x63fc2a8 if baseline else new['LoadoutLookupTree'];goods_tree=0x63fab94 if baseline else new['GoodArchetypeTree']
    init=0x6311de0 if baseline else new['loadout_tree_initialize']
    for t in [tree,goods_tree]:h.invoke(init,(obj+0x9100,obj+0x9101),t)
    head=h.word(goods_tree+4);nil=h.word(goods_tree+8);node=allocate(24,'goods_node');record=allocate(128,'goods_record')
    uc.mem_write(node,struct.pack('<IIIII',nil,head,nil,456,record));uc.mem_write(record+112,bytes([goods_flag]))
    h.write_word(head,node);h.write_word(head+4,node);h.write_word(head+8,node);h.write_word(goods_tree+16,1)
    counters=[0x63ecb6c,0x63ecb70,0x63ecb74,0x6589810,0x6589814] if baseline else [new[n] for n in ['?StringCacheFront@@3IA','?StringCacheBack@@3IA','?StringCacheInternedCount@@3IA','?StringCachePrivateCount@@3IA','?StringCacheIndex@@3PAUStringCacheTree@@A']]
    for p,v in zip(counters,[1,0x180000,1,0,0]):h.write_word(p,v)
    singleton=orig['?m_pTheMaker@CFLIDMaker@@2PAV1@A'] if baseline else new['?m_pTheMaker@CFLIDMaker@@2PAV1@A'];h.write_word(singleton,0)
    if baseline:bay=h.invoke(orig['?StringAlloc@@YAPADPBD_N@Z'],(obj+0x9000,0));h.write_word(0x63fbf0c,bay)
    else:h.initialize_crt(test_dll)
    results=[]
    for repeat in range(2):
     returned=h.invoke(exports[symbol],(nameptr,flag),max_instructions=20000000)
     results.append((returned,maps(tree,0)))
    snapshots.append(results)
   assert snapshots[0]==snapshots[1],(file_bytes,flag,snapshots)
   count+=2
   records=snapshots[0][0][1];items=records[0][3]
   if b'nickname=external' in file_bytes or goods_flag==0:assert len(items)==(3 if b'nickname=equipped' in file_bytes else 2)
   else:
    assert len(items)==(2 if b'nickname=equipped' in file_bytes else 1)
    merged=items[-1];assert merged[1]==(0x23 if b'nickname=equipped' in file_bytes else 0x22)
    expected_status=0.75 if b'2,,0.25,true\ncargo=456,3,,0.5' in file_bytes else 0.25
    assert merged[5]==struct.unpack('<I',struct.pack('<f',expected_status))[0]
    assert merged[6]==(4 if expected_status==0.75 else 5)

 real_files=[]
 report=dict(status='passed',original_sha256=HASH,compiled_dll_sha256=digest(test_dll),differential_calls=count,real_files=real_files,methods=methods,source_hashes={p:digest(ROOT/p) for p in ['src/loadout_load.cpp','tests/fixtures/loadout_loader_runtime.cpp','tools/build_ini_fixture.py','tests/verify_loadout_loader_goods_x86.py']},external_dependencies='MSVCP60 COW, Win32 mapping, fatal handler and progress callback modeled',comparison_scope='Semantic Map/Equipment fields, not raw heap/padding or allocation trace',synthetic_text_files=len(payloads),goods_flag_values=[0,1,255],goods_database='Controlled real lookup node and Goods flag record',not_verified=['Real Loadout corpus','Raw heap/padding/allocation trace','Native OS/CRT','Non-returning fatal handler','Allocation or exception failure','Exact instruction matching'])
 (ROOT/'analysis/loadout-loader-goods-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} Goods-driven Cargo loader comparisons, semantic Maps/Equipment/IDs and replacement')
if __name__=='__main__':main()
