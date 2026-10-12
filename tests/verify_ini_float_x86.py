#!/usr/bin/env python3
"""Differential INI float getter with complete 80-bit x87 return comparison."""
import hashlib,json,pathlib,random,re,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 build=ROOT/'build';objects=[];commands=[]
 sources=['src/ini_reader_float.cpp','tests/fixtures/ini_float_x86_runtime.cpp','src/ini_reader_values.cpp','src/ini_reader.cpp','src/file_map.cpp','tests/fixtures/ini_values_x86_runtime.cpp','tests/fixtures/ini_reader_x86_runtime.cpp','tests/fixtures/file_map_x86_runtime.cpp']
 for source in sources:
  out=build/(pathlib.Path(source).stem+'-values.obj');objects.append(str(out));cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-mno-sse','-mno-sse2','-c',str(ROOT/source),'-o',str(out)];subprocess.run(cmd,check=True);commands.append(cmd)
 float_symbol='?get_value_float@INI_Reader@@QAEMI@Z';dll=build/'ini_float.dll'
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x17000000',f'/out:{dll}']+objects+['/export:'+float_symbol];subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(dll);uc=h.uc;uc.mem_map(0x23000000,0x10000)
 o=h.scratch;r=o+0x2000;block=0x23000000;entry=block+0x10;parameter=block+0x20;strings=block+0x100;fp=block+0x2000
 uc.mem_write(strings,b'Header\0Value\0');uc.mem_write(block,struct.pack('<HH',0,1));uc.mem_write(entry,struct.pack('<HB',7,1))
 for obj in [o,r]:
  uc.mem_write(obj,b'\0'*0x1568);h.write_word(obj+0x1450,strings);h.write_word(obj+0x1454,block);h.write_word(obj+0x145c,entry);h.write_word(obj+0x1460,parameter);uc.mem_write(obj+0x1564,b'\1')
 sprintf=h.stop+0x240;message=h.stop+0x260
 for iat,address in [(0x639931c,sprintf),(0x6399378,message)]:h.write_word(iat,address)
 atof=h.stop+0x300;fp64=fp+16
 h.write_word(0x63992f0,atof);uc.mem_write(atof,b'\xdb\x2d'+struct.pack('<I',fp64)+b'\xc3')
 override_fp80=None
 logs=[]
 def text(ptr):
  out=bytearray()
  for i in range(256):
   b=uc.mem_read(ptr+i,1)[0]
   if not b:return bytes(out)
   out.append(b)
  raise AssertionError('Long test string')
 def hook(uc,address,size,user):
  sp=uc.reg_read(UC_X86_REG_ESP)
  if address==atof:
   value=text(h.word(sp+4));m=re.match(rb'\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)',value)
   number=float(m.group(1)) if m else 0.0
   word=struct.unpack('<Q',struct.pack('<d',number))[0];sign=(word>>63)<<15;exponent=(word>>52)&2047;fraction=word&((1<<52)-1)
   if exponent==2047:exp80=32767;sig80=(1<<63)|(fraction<<11)
   elif exponent:exp80=exponent-1023+16383;sig80=((1<<52)|fraction)<<11
   elif fraction:
    high=fraction.bit_length()-1;exp80=-1074+high+16383;sig80=fraction<<(63-high)
   else:exp80=0;sig80=0
   uc.mem_write(fp64,override_fp80 if override_fp80 is not None else struct.pack('<QH',sig80,sign|exp80))
  elif address==sprintf:
   dst=h.word(sp+4);fmt=text(h.word(sp+8));assert fmt==b'header [%s] value %s missing parameter %u'
   output=b'header ['+text(h.word(sp+12))+b'] value '+text(h.word(sp+16))+b' missing parameter '+str(h.word(sp+20)).encode();uc.mem_write(dst,output+b'\0');h.return_stub(len(output))
  elif address==message:
   assert h.word(sp+4)==0 and text(h.word(sp+12))==b'ERROR' and h.word(sp+16)==0
   logs.append(text(h.word(sp+8)));h.return_stub(1);uc.reg_write(UC_X86_REG_ESP,sp+20)
 uc.hook_add(UC_HOOK_CODE,hook)
 cases=[];rng=random.Random(2003)
 cases += [(0,i,None) for i in range(256)]
 cases += [(1,i,None) for i in [0,1,0xffffffff,0x80000000,0x7fffffff]+[rng.randrange(2**32) for _ in range(300)]]
 cases += [(2,i,None) for i in [0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x4f000000,0x4f800000,0x7f800000,0xff800000,0x7fc00000,0x7f800001]+[rng.randrange(2**32) for _ in range(300)]]
 cases += [(3,32,s) for s in [b'true',b'TRUE',b'false',b'FALSE',b'1',b'0',b'-42',b' 12.5',b'garbage',b'2147483647',b'-2147483648',b'0.1',b'1e40',b'-1e-300',b'1.0000000000000002']]
 cases += [(tag,0,None) for tag in range(4,256)]
 rows=[];calls=0
 def pair(symbol,index):
  nonlocal calls
  before=len(logs);a=h.invoke(orig[symbol],(index,),o,float_result=True);oldlogs=logs[before:];before=len(logs);b=h.invoke(new[symbol],(index,),r,float_result=True)
  assert a==b,(symbol,index,a,b)
  assert oldlogs==logs[before:]
  assert bytes(uc.mem_read(o+0x144c,0x18))==bytes(uc.mem_read(r+0x144c,0x18))
  calls+=1;return a
 for tag,bits,string in cases:
  uc.mem_write(parameter,struct.pack('<BI',tag,bits))
  if string is not None:uc.mem_write(strings+bits,string+b'\0')
  rows.append(dict(tag=tag,bits=hex(bits),string=string.decode() if string is not None else None,return_x87=pair(float_symbol,0).hex()))
 # The original passes atof's ST0 through without narrowing, even if an external
 # implementation leaves precision beyond binary64 in the register.
 extended_cases=0
 uc.mem_write(parameter,struct.pack('<BI',3,32));uc.mem_write(strings+32,b'1\0')
 for significand,signexp in [(0x8000000000000001,16383),(0x8000000000000401,16383),(0xffffffffffffffff,16382),(0x8000000000000001,0x8000|16383)]:
  override_fp80=struct.pack('<QH',significand,signexp);assert pair(float_symbol,0)==override_fp80;extended_cases+=1
 override_fp80=None
 for index in [1,255,0xffffffff]:pair(float_symbol,index)
 for obj in [o,r]:h.write_word(obj+0x145c,0)
 pair(float_symbol,0)
 report=dict(status='passed_binary_float_cpp_abi_view',original_sha256=HASH,compiled_dll_sha256=digest(dll),
             source_hashes={p:digest(ROOT/p) for p in sources+['src/ini_reader_values.hpp','src/ini_reader.hpp','src/file_map.hpp']},
             differential_calls=calls,parameter_cases=len(cases),complete_80bit_returns_compared=True,assembly_in_getter=False,abi_implementation_return_type='double under original float member symbol',extended_atof_passthrough_cases=extended_cases,rows=rows,commands=commands,
             mocks=['atof decimal-prefix model returning binary64 in ST0','sprintf/MessageBox diagnostic model'],
             not_verified=['Real CRT/Win32 execution','Text get_value_float path','FPU exception/control-word fidelity','Malformed parameter memory access','Other typed getters','Exact instruction matching'])
 (ROOT/'analysis/ini-float-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {calls} float calls, {len(cases)} parameter cases, full x87 return bytes and diagnostics')
if __name__=='__main__':main()
