#!/usr/bin/env python3
"""Loadout line state/order comparison with controlled INI and interning inputs."""
import hashlib,itertools,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/loadout_lines.cpp','tests/fixtures/loadout_lines_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-mno-sse','-mno-sse2','-c',str(ROOT/f),'-o',str(obj)],check=True)
 symbols=['?ReadEquipLine@Loadout@@YA_NAAVINI_Reader@@AAUEquipDesc@@@Z','?ReadCargoLine@Loadout@@YA_NAAVINI_Reader@@AAUEquipDesc@@@Z'];dll=ROOT/'build/loadout_lines.dll'
 subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1a000000',f'/out:{dll}']+objects+['/export:'+n for n in symbols],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;reader=h.scratch;item=reader+0x2000;base=reader+0x4000;fp=base+0x1000
 h.write_word(0x63fbf0c,0x20507000);h.write_word(0x6399248,h.stop+0x200);h.write_word(0x63992f0,h.stop+0x220);uc.mem_write(h.stop+0x240,b'\xdd\x05'+struct.pack('<I',fp)+b'\xc3')
 uc.mem_write(h.stop+0x260,b'\xdd\x05'+struct.pack('<I',fp)+b'\xc2\x04\x00')
 events=[];empty=[];number=0;floating=0.;boolean=0;atoi_value=0;atof_value=0.
 def ret(value,cleanup=0):
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EAX,value&0xffffffff);uc.reg_write(UC_X86_REG_EIP,h.word(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
 def text(p):
  out=b''
  while uc.mem_read(p,1)[0]:out+=bytes(uc.mem_read(p,1));p+=1
  return out
 def hook(uc,address,size,user):
  sp=uc.reg_read(UC_X86_REG_ESP)
  if address in [0x6310ac0,0x63105f0,0x6310980,0x6310850,0x6310640]:
   index=h.word(sp+4);events.append((hex(address),index))
   if address==0x6310980:
    uc.mem_write(fp,struct.pack('<d',floating));uc.reg_write(UC_X86_REG_EIP,h.stop+0x260)
   else:ret(base+index*64 if address==0x6310ac0 else int(empty[index]) if address==0x63105f0 else number if address==0x6310850 else boolean,4)
  elif address in [h.stop+0x200,h.stop+0x220,0x630d470,0x6333bd0]:
   arg=h.word(sp+4);events.append((hex(address),text(arg)))
   if address==h.stop+0x220:uc.mem_write(fp,struct.pack('<d',atof_value));uc.reg_write(UC_X86_REG_EIP,h.stop+0x240)
   else:
    if address==0x6333bd0:assert h.word(sp+8)==0
    ret(atoi_value if address==h.stop+0x200 else 0x98765432 if address==0x630d470 else base+0x300)
 uc.hook_add(UC_HOOK_CODE,hook);rng=random.Random(2003);count=0
 for i in range(5):uc.mem_write(base+i*64,f'value{i}'.encode()+b'\0')
 for symbol in symbols:
  for empty in itertools.product([False,True],repeat=5):
   for atoi_value,atof_value in itertools.product([0,123,-1],[0.,-0.,1.,-2.,float('nan')]):
    number=rng.randrange(2**32);floating=rng.choice([0.,-0.,1.,1e40,-1e-40,float('inf'),float('nan')]);boolean=rng.randrange(256);seed=rng.randbytes(32);results=[]
    for exports in [orig,new]:
     events.clear();uc.mem_write(item,seed);returned=h.invoke(exports[symbol],(reader,item))&255;results.append((returned,bytes(uc.mem_read(item,32)),list(events)))
    assert results[0]==results[1],(symbol,empty,atoi_value,atof_value,results)
    count+=1
 report=dict(status='passed',differential_calls=count,source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['tests/verify_loadout_lines_x86.py']},reader_dependency='Controlled API return values; reconstructed reader integration pending',not_verified=['Actual CreateID and StringAlloc integration','Native CRT and reader execution','Exact instruction matching'])
 (ROOT/'analysis/loadout-lines-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {count} equipment/cargo lines, complete descriptor and call order')
if __name__=='__main__':main()
