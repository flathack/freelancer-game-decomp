#!/usr/bin/env python3
"""Compare ParseNumber syntax, warnings and complete x87 return representation."""
import hashlib,json,pathlib,random,re,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 sources=['src/parse_number.cpp','src/parse_number_x87.cpp','tests/fixtures/parse_number_runtime.cpp','tests/fixtures/fp_runtime_marker.cpp'];objects=[];commands=[];build=ROOT/'build'
 for source in sources:
  obj=build/(pathlib.Path(source).stem+'.obj');objects.append(str(obj));cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-mno-sse','-mno-sse2','-c',str(ROOT/source),'-o',str(obj)];subprocess.run(cmd,check=True);commands.append(cmd)
 symbol='?ParseNumber@@YANPBD@Z';dll=build/'parse_number.dll';cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1d000000',f'/out:{dll}']+objects+['/export:'+symbol];subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(dll);uc=h.uc;input_=h.scratch;fp=h.scratch+0x7000;lower=h.stop+0x200;atof=h.stop+0x220;log=h.stop+0x240;slot=h.stop+0x500
 h.write_word(0x63992f4,lower);h.write_word(0x63992f0,atof);h.write_word(0x6399028,slot);h.write_word(slot,log)
 uc.mem_write(atof,b'\xdd\x05'+struct.pack('<I',fp)+b'\xc3');events=[]
 def text(p):
  out=bytearray()
  for i in range(1024):
   b=uc.mem_read(p+i,1)[0]
   if not b:return bytes(out)
   out.append(b)
  raise AssertionError('Unterminated input')
 def hook(uc,address,size,user):
  sp=uc.reg_read(UC_X86_REG_ESP)
  if address==lower:
   c=h.word(sp+4);c=c-2**32 if c>=2**31 else c;h.return_stub((c+32 if 65<=c<=90 else c)&0xffffffff)
  elif address==atof:
   s=text(h.word(sp+4));events.append(('atof',s));m=re.match(rb'\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)',s);value=float(m.group(1)) if m else 0.0;uc.mem_write(fp,struct.pack('<d',value))
  elif address==log:
   assert h.word(sp+4)==0x100002 and h.word(sp+16)==0x14e
   assert text(h.word(sp+8))==b"%s(%d) : *** WARNING: ParseNumber: illegal BASE-N digit(s) in argument! '%s'"
   assert text(h.word(sp+12))==b'E:\\FL\\Scratch\\Source\\Common\\Parse.cpp'
   events.append(('warning',text(h.word(sp+20))));h.return_stub(0)
 uc.hook_add(UC_HOOK_CODE,hook)
 inputs=[b'',b'0',b'000',b'-0',b'+-3',b'--3',b'0xFF',b'0x.8',b'-0xA.F',b'101b',b'102b',b'1h',b'1H',b'12h',b'ABh',b'123d',b'1e-3',b'1.25',b"'A'",b"-'A'",b'  -0x10',b'0xFFFFFFFFFFFFFFFF',b'0x123456789ABCDEF.12345']
 inputs += [b"'"+bytes([c])+b"'" for c in range(1,256)]
 inputs += [b'0x'+bytes([c])+b'.1' for c in range(1,256)]
 rng=random.Random(2003)
 inputs += [bytes(rng.choice(b'0123456789abcdefABCDEFxbhd.+-eE\t ') for _ in range(rng.randrange(30))) for _ in range(1000)]
 rows=[]
 for s in inputs:
  uc.mem_write(input_,s+b'\0');before=len(events);a=h.invoke(orig[symbol],(input_,),float_result=True);trace=events[before:];before=len(events);b=h.invoke(new[symbol],(input_,),float_result=True)
  assert a==b,(s,a.hex(),b.hex());assert trace==events[before:],(s,trace,events[before:])
  rows.append(dict(input_hex=s.hex(),return_x87=a.hex(),events=[(name,value.hex()) for name,value in trace]))
 report=dict(status='passed_with_x87_arithmetic_boundary',original_sha256=HASH,compiled_dll_sha256=digest(dll),source_hashes={p:digest(ROOT/p) for p in sources+['src/parse_number.hpp']},differential_calls=len(rows),rows=rows,commands=commands,mocks=['ASCII tolower','decimal-prefix binary64 atof','FDUMP warning capture'],not_verified=['Native CRT/locale','FPU flags/control words','Null/unbounded pointers','Runtime class-table edits','Exact instruction matching'])
 (ROOT/'analysis/parse-number-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {len(rows)} ParseNumber comparisons with full 80-bit returns, dispatch arguments and warnings')
if __name__=='__main__':main()
