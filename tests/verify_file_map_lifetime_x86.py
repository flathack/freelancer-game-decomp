#!/usr/bin/env python3
"""Differential FileMap OS/COW paths with explicitly modeled external imports."""
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
 methods=[s.name.decode() for s in pefile.PE(str(SOURCE)).DIRECTORY_ENTRY_EXPORT.symbols if s.name and b'FileMap@@' in s.name]
 commands=[];build=ROOT/'build'
 for source,out in [('src/file_map.cpp','file_map_lifetime.obj'),('tests/fixtures/file_map_x86_runtime.cpp','file_map_lifetime_runtime.obj')]:
  cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/source),'-o',str(build/out)];subprocess.run(cmd,check=True);commands.append(cmd)
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x14000000',f'/out:{build}/file_map_lifetime.dll',str(build/'file_map_lifetime.obj'),str(build/'file_map_lifetime_runtime.obj')]+['/export:'+n for n in methods]
 subprocess.run(cmd,check=True);commands.append(cmd)
 production='--production-bindings' in sys.argv
 test_dll=build/'file_map_lifetime.dll'
 if production:
  subprocess.run(['python3',str(ROOT/'tools/build_filemap_windows.py')],check=True)
  test_dll=build/'filemap-windows/freelancer-filemap.dll'
 h=X86Harness();orig=h.load(SOURCE);new=h.load(test_dll);uc=h.uc;uc.mem_map(0,4096);uc.mem_map(0x21000000,0x200000)
 heap=0x21000000;empty=h.scratch+0x5000;h.write_word(0x63991d0,empty);h.write_word(0x63991c0,empty+4);h.write_word(empty+4,0xffffffff)
 imports={0x63991d4:('grow',8),0x63991bc:('split',0),0x63991b8:('tidy',4),0x63991a4:('assign',8),0x63991b0:('copy',4),0x6399330:('memmove',12),0x639932c:('free',4),0x6399328:('malloc',4),0x63990d4:('open',28),0x6399144:('mapping',24),0x639913c:('size',8),0x6399138:('map',20),0x6399130:('unmap',4),0x6399140:('close_handle',4)}
 dispatch={};events=[];allocations={};stage=0;file_bytes=b'controlled-file-data';view=h.scratch+0x7000;uc.mem_write(view,file_bytes)
 for index,(iat,(name,bytes_)) in enumerate(imports.items()):
  address=h.stop+0x200+16*index;dispatch[address]=(name,bytes_);h.write_word(iat,address)
 if production:
  original_imports={s.name.decode():s.address for e in pefile.PE(str(SOURCE)).DIRECTORY_ENTRY_IMPORT for s in e.imports if s.name}
  for descriptor in pefile.PE(str(test_dll)).DIRECTORY_ENTRY_IMPORT:
   for symbol in descriptor.imports:
    if symbol.name.decode().startswith('?_C@'):target=empty
    else:target=h.word(original_imports[symbol.name.decode()])
    h.write_word(symbol.address,target)
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
  if name=='grow':result=grow(obj,args[0],bool(args[1]))
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
  cleanup=bytes_ if name in ['grow','split','tidy','assign','copy','open','mapping','size','map','unmap','close_handle'] else 0
  ret(result,cleanup)
 uc.hook_add(UC_HOOK_CODE,hook)
 o=h.scratch;r=o+0x100;od=o+0x200;rd=o+0x300;nameptr=o+0x600;data_ptr=o+0x800
 names={'ctor':'??0FileMap@@QAE@XZ','copy':'??0FileMap@@QAE@ABU0@@Z','assign':'??4FileMap@@QAEAAU0@ABU0@@Z','dtor':'??1FileMap@@QAE@XZ','open':'?open@FileMap@@QAE_NPBD@Z','close':'?close@FileMap@@QAEXXZ','handoff':'?handoff_to@FileMap@@QAEXAAU1@@Z','memory':'?open_memory@FileMap@@QAE_NPBXI@Z'}
 count=0;seen=set()
 def snapshot(obj):
  p=h.word(obj+4);data=h.word(obj+24);length=h.word(obj+28)
  return (text(p) if p else None,refs(p) if p else None,h.word(obj+8),h.word(obj+12),h.word(obj+16),h.word(obj+20),text(data,length) if data and length else None,length,h.word(obj+32))
 def pair(key,objects=(o,r),args_o=(),args_r=None):
  nonlocal count
  if args_r is None:args_r=args_o
  traces=[];results=[]
  for exports,obj,args in [(orig,objects[0],args_o),(new,objects[1],args_r)]:
   start=len(events);value=h.invoke(exports[names[key]],args,obj);traces.append(events[start:]);results.append(value)
  assert traces[0]==traces[1],(key,traces)
  assert snapshot(objects[0])==snapshot(objects[1]),(key,snapshot(objects[0]),snapshot(objects[1]))
  if key in ['ctor','copy','assign']:assert results==list(objects)
  elif key in ['open','memory']:assert (results[0]&255)==(results[1]&255)
  count+=1;seen.add(names[key]);return results[0]&255
 # OS success and each acquisition failure stage, including retained length after failed map.
 for stage_ in [0,1,2,3]:
  stage=stage_;pair('ctor');uc.mem_write(nameptr,b'alpha.ini\0');success=pair('open',args_o=(nameptr,));assert success==(stage==0)
  if stage==3:assert h.word(o+28)==h.word(r+28)==len(file_bytes)
  pair('close');pair('close');pair('dtor')
 stage=0
 # Copy/handoff/assignment preserves observed shared string and raw resource aliasing.
 for key in ['copy','assign','handoff']:
  pair('ctor');pair('ctor',(od,rd));uc.mem_write(nameptr,b'shared.ini\0');pair('open',args_o=(nameptr,))
  if key=='copy':pair(key,(od,rd),(o,),(r,))
  elif key=='assign':pair(key,(od,rd),(o,),(r,))
  else:pair(key,args_o=(od,),args_r=(rd,))
  assert h.word(o+4)==h.word(od+4) and h.word(r+4)==h.word(rd+4)
  assert snapshot(o)==snapshot(r) and snapshot(od)==snapshot(rd)
  pair('close',(od,rd));pair('close');pair('dtor',(od,rd));pair('dtor')
 # Receiver's existing resource is overwritten, rather than implicitly closed.
 pair('ctor');pair('ctor',(od,rd));uc.mem_write(nameptr,b'owner.ini\0');pair('open',args_o=(nameptr,));uc.mem_write(data_ptr,b'old')
 pair('memory',(od,rd),(data_ptr,3));before=len(events);pair('handoff',args_o=(od,),args_r=(rd,));assert not events[before:]
 pair('close',(od,rd));pair('dtor');pair('dtor',(od,rd))
 # Self-assignment detaches a shared filename; self-handoff clears own handles/data only.
 pair('ctor');pair('ctor',(od,rd));uc.mem_write(nameptr,b'self.ini\0');pair('open',args_o=(nameptr,));pair('copy',(od,rd),(o,),(r,))
 pair('assign',args_o=(o,),args_r=(r,));assert h.word(o+4)!=h.word(od+4) and h.word(r+4)!=h.word(rd+4)
 old_length=h.word(o+28);pair('handoff',args_o=(o,),args_r=(r,));assert not h.word(o+24) and h.word(o+28)==old_length
 pair('close',(od,rd));pair('dtor');pair('dtor',(od,rd))
 # Refcount boundary: <254 shares; 254/255 forces a separately grown buffer.
 for refcount in [0,1,253,254,255]:
  pair('ctor');pair('ctor',(od,rd));uc.mem_write(nameptr,b'boundary.ini\0');pair('open',args_o=(nameptr,))
  for obj in [o,r]:uc.mem_write(h.word(obj+4)-1,bytes([refcount]))
  pair('copy',(od,rd),(o,),(r,));assert (h.word(o+4)==h.word(od+4))==(refcount<254)
  pair('close',(od,rd));pair('close');pair('dtor',(od,rd));pair('dtor')
 report=dict(status='passed_under_modeled_external_imports',original_sha256=HASH,compiled_dll_sha256=digest(test_dll),
             source_hashes={p:digest(ROOT/p) for p in ['src/file_map.cpp','src/file_map.hpp']+(['src/runtime/file_map_windows.cpp','tools/build_filemap_windows.py'] if production else ['tests/fixtures/file_map_x86_runtime.cpp'])},
             binding_mode='real_named_imports' if production else 'fixture_fixed_image_addresses',lifetime_calls=count,covered_methods=sorted(seen),compiled_exported_methods=len(methods),commands=commands,
             checks=['OS open success and three failure stages','Win32 argument and call-order comparison','close/destructor','copy/assignment/handoff','shared filename detach','self-assignment/self-handoff','refcount 253/254/255','overwriting receiver ownership without cleanup'],
             mocks=['MSVCP60 Grow/Split/Tidy/Assign/Copy semantics model (not real CRT)','successful allocator/free/memmove','controlled Win32 file/mapping APIs'],
             not_verified=['Real MSVCP60 allocation/capacity/SEH behavior','Real OS file mappings','Allocator failure','Invalid/null path strings','Exact instruction matching'])
 (ROOT/('analysis/filemap-production-abi-behavior.json' if production else 'analysis/filemap-lifetime-x86-behavior.json')).write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} FileMap lifetime/OS/COW comparisons; all {len(methods)} exports compile; external CRT/OS models remain explicit')
if __name__=='__main__':main()
