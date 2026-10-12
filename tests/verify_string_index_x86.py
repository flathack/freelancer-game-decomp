#!/usr/bin/env python3
"""Original x86 StringIndex versus reconstructed comma/trim/scratch-buffer code."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 commands=[];build=ROOT/'build';obj=build/'string_index.obj';dll=build/'string_index.dll';symbol='?StringIndex@@YAPBDPBDI@Z';buffer='?StringIndexBuffer@@3PADA'
 cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/'src/string_index.cpp'),'-o',str(obj)];subprocess.run(cmd,check=True);commands.append(cmd)
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x19000000',f'/out:{dll}',str(obj),'/export:'+symbol,'/export:'+buffer+',DATA'];subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(dll);uc=h.uc;input_=h.scratch;search=h.stop+0x200;h.write_word(0x6399300,search)
 def text(p):
  out=bytearray()
  for i in range(2048):
   b=uc.mem_read(p+i,1)[0]
   if not b:return bytes(out)
   out.append(b)
  raise AssertionError('Unterminated output')
 def hook(uc,address,size,user):
  if address==search:
   sp=uc.reg_read(UC_X86_REG_ESP);ptr=h.word(sp+4);char=h.word(sp+8)&255;result=0
   for i in range(2048):
    byte=uc.mem_read(ptr+i,1)[0]
    if byte==char:result=ptr+i;break
    if not byte:break
   h.return_stub(result)
 uc.hook_add(UC_HOOK_CODE,hook)
 inputs=[b'',b',',b',,',b' a , b , ',b'"a,b",c',b'\vfirst\f,\t second\r\n',b'x'*1023]
 inputs += [bytes([ch])+b'X'+bytes([ch])+b',Y' for ch in range(1,256)]
 rng=random.Random(2003)
 inputs += [bytes(rng.randrange(1,256) for _ in range(rng.randrange(128))) for _ in range(500)]
 calls=0;rows=[]
 for value in inputs:
  uc.mem_write(input_,value+b'\0')
  for index in [0,1,2,5,0xffffffff]:
   a=h.invoke(orig[symbol],(input_,index));b=h.invoke(new[symbol],(input_,index))
   assert a==0x6400350 and b==new[buffer]
   expected=text(a);actual=text(b);assert expected==actual,(value,index,expected,actual)
   assert bytes(uc.mem_read(a,1024))==bytes(uc.mem_read(b,1024)), 'Scratch tail/write footprint mismatch'
   calls+=1
  rows.append(dict(input_hex=value.hex()))
 # Out-of-range lookup clears only byte zero; later callers reuse the same buffer.
 uc.mem_write(input_,b'alpha,beta\0');a=h.invoke(orig[symbol],(input_,0));b=h.invoke(new[symbol],(input_,0));assert text(a)==text(b)==b'alpha'
 assert h.invoke(orig[symbol],(input_,1))==a and h.invoke(new[symbol],(input_,1))==b;assert text(a)==text(b)==b'beta'
 report=dict(status='passed',original_sha256=HASH,compiled_dll_sha256=digest(dll),
             source_hashes={p:digest(ROOT/p) for p in ['src/string_index.cpp','src/string_index.hpp']},differential_calls=calls+2,input_cases=len(inputs),all_nonzero_byte_edges_checked=True,maximum_input_length=1023,
             whitespace_low7_codes=[9,10,13,32],commands=commands,inputs=rows,mocks=['strchr'],
             not_verified=['Runtime edits to character-class table','Input beyond scratch capacity','Overlapping input/scratch','Null input','Exact instruction matching'])
 (ROOT/'analysis/string-index-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {calls+2} StringIndex comparisons, {len(inputs)} inputs, all byte edges and full scratch footprints')
if __name__=='__main__':main()
