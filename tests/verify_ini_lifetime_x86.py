#!/usr/bin/env python3
"""Mode-selective close and metadata against original x86 instructions."""
import hashlib,itertools,json,pathlib,random,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 source=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
 assert hashlib.sha256(source.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/ini_reader_lifetime.cpp','src/file_map.cpp','tests/fixtures/file_map_x86_runtime.cpp','tests/fixtures/ini_lifetime_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/('ini-life-'+pathlib.Path(f).stem+'.obj');objects.append(str(obj))
  subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbols=['?close@INI_Reader@@QAEXXZ','?get_file_name@INI_Reader@@QBEPBDXZ','?get_line_num@INI_Reader@@QBEHXZ'];dll=ROOT/'build/ini_lifetime.dll'
 subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1d000000',f'/out:{dll}']+objects+['/export:'+s for s in symbols],check=True)
 h=X86Harness();orig=h.load(source);new=h.load(dll);uc=h.uc;events=[]
 empty=h.scratch+0x6000;name=empty+0x100;data=empty+0x200;obj=h.scratch
 h.write_word(0x63991d0,empty);h.write_word(0x63991c0,empty+4);h.write_word(empty+4,0xffffffff)
 hooks={0x63991d4:('grow',8),0x6399330:('move',12),0x639932c:('free',4),0x6399130:('unmap',4),0x6399140:('handle',4)}
 dispatch={}
 for i,(iat,info) in enumerate(hooks.items()):
  addr=h.stop+0x200+i*16;h.write_word(iat,addr);dispatch[addr]=info
 logger=h.stop+0x400;h.write_word(0x6399028,empty+8);h.write_word(empty+8,logger);dispatch[logger]=('warning',20)
 def text(p):
  out=b''
  while uc.mem_read(p,1)[0]:out+=bytes(uc.mem_read(p,1));p+=1
  return out.decode()
 def hook(uc,address,size,user):
  if address not in dispatch:return
  kind,n=dispatch[address];sp=uc.reg_read(UC_X86_REG_ESP);args=[h.word(sp+4+i) for i in range(0,n,4)];result=0
  if kind=='grow':
   target=uc.reg_read(UC_X86_REG_ECX);assert args==[0,0];p=h.word(target+4)
   if p:uc.mem_write(p,b'\0');h.write_word(target+8,0)
  elif kind=='move':
   dst,src,count=args
   if count:uc.mem_write(dst,bytes(uc.mem_read(src,count)))
   result=dst
  elif kind=='warning':events.append((kind,args[0],text(args[1]),text(args[2]),args[3],text(args[4])))
  else:events.append((kind,*args))
  uc.reg_write(UC_X86_REG_EAX,result);uc.reg_write(UC_X86_REG_ESP,sp+4+(n if kind in ['grow','unmap','handle'] else 0));uc.reg_write(UC_X86_REG_EIP,h.word(sp))
 uc.hook_add(UC_HOOK_CODE,hook);rng=random.Random(2003);calls=0
 for mode,handle,mapping,has_data,has_name in itertools.product([0,1],[0xffffffff,0,0x111],[0,0x222],[False,True],[False,True]):
  seed=bytearray(rng.randbytes(0x1568));seed[0x1564]=mode
  for offset in [0,0x1428]:
   values=[0,name if has_name else 0,4 if has_name else 0,32,handle,mapping,data if has_data else 0,31,7]
   for i,v in enumerate(values):seed[offset+i*4:offset+i*4+4]=v.to_bytes(4,'little')
  for symbol in symbols:
   results=[]
   for exports in [orig,new]:
    uc.mem_write(obj,bytes(seed));uc.mem_write(name-1,b'\0test\0');events.clear()
    ret=h.invoke(exports[symbol],(),obj)
    # void return registers are unspecified.
    results.append((ret if symbol!=symbols[0] else None,bytes(uc.mem_read(obj,0x1568)),bytes(uc.mem_read(name-1,6)),list(events)))
   assert results[0]==results[1],(mode,handle,mapping,has_data,has_name,symbol,results)
   calls+=1
 report=dict(status='passed',differential_calls=calls,methods=symbols,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},not_verified=['Shared COW names: covered by underlying FileMap tests, not this reader test','Native Windows CRT/OS','Exact instruction matching'])
 (ROOT/'analysis/ini-lifetime-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {calls} reader lifecycle/metadata calls, complete object and external effects')
if __name__=='__main__':main()
