#!/usr/bin/env python3
"""Differential binary bool/int conversion, including raw bool bytes and x87 _ftol."""
import sys,hashlib,json,pathlib,random,re,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 sys.path.insert(0,str(ROOT/'tools'))
 from build_ini_fixture import main as build_fixture
 build_fixture(include_loadout=True,include_hash=True);dll=ROOT/'build/loadout-hash-fixture/freelancer-ini-fixture.dll'
 commands=[];sources=['src/loadout_lines.cpp','tests/fixtures/loadout_reader_hash_runtime.cpp','tests/fixtures/loadout_reader_runtime.cpp','src/create_id.cpp']
 h=X86Harness();orig=h.load(SOURCE);new=h.load(dll);uc=h.uc;uc.mem_map(0x23000000,0x10000)
 o=h.scratch;r=o+0x2000;block=0x23000000;entry=block+0x10;parameter=block+0x20;strings=block+0x100;fp=block+0x2000
 uc.mem_write(strings,b'Header\0Value\0');uc.mem_write(block,struct.pack('<HH',0,1));uc.mem_write(entry,struct.pack('<HB',7,1))
 for obj in [o,r]:
  uc.mem_write(obj,b'\0'*0x1568);h.write_word(obj+0x1450,strings);h.write_word(obj+0x1454,block);h.write_word(obj+0x145c,entry);h.write_word(obj+0x1460,parameter);uc.mem_write(obj+0x1564,b'\1')
 compare=h.stop+0x200;atoi=h.stop+0x220;sprintf=h.stop+0x240;message=h.stop+0x260;ftol=h.stop+0x280
 for iat,address in [(0x639902c,compare),(0x6399248,atoi),(0x639931c,sprintf),(0x6399378,message),(0x6399320,ftol)]:h.write_word(iat,address)
 # Execute FSTP m80 in the emulator, then convert the exact representation in the hook.
 uc.mem_write(ftol,b'\xdb\x3d'+struct.pack('<I',fp)+b'\x90')
 search=h.stop+0x300;log=h.stop+0x320;slot=h.stop+0x500
 h.write_word(0x6399300,search);h.write_word(0x6399028,slot);h.write_word(slot,log)
 uc.mem_write(strings+512,b'fixture.ini\0')
 for obj in [o,r]:h.write_word(obj+4,strings+512)
 logs=[]
 def text(ptr):
  out=bytearray()
  for i in range(256):
   b=uc.mem_read(ptr+i,1)[0]
   if not b:return bytes(out)
   out.append(b)
  raise AssertionError('Long test string')
 def hook(uc,address,size,user):
  nonlocal heap_cursor
  sp=uc.reg_read(UC_X86_REG_ESP)
  if address==0x6391abc:
   size=h.word(sp+4);assert size in [8,0x41c];result=heap_cursor;heap_cursor+=(size+15)&~15;h.return_stub(result)
  elif address==strlower:
   ptr=h.word(sp+4)
   for i,b in enumerate(text(ptr)):
    if 65<=b<=90:uc.mem_write(ptr+i,bytes([b+32]))
   h.return_stub(ptr)
  elif address==atof:
   value=text(h.word(sp+4));m=re.match(rb'\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)',value)
   number=float(m.group(1)) if m else float('nan') if value.lower()==b'nan' else 0.
   uc.mem_write(fp+32,struct.pack('<d',number))
  elif address==lower:
   value=h.word(sp+4);h.return_stub(value+32 if 65<=value<=90 else value)
  elif address==0x6333bd0:
   value=text(h.word(sp+4));logs.append(('intern',value))
   if address==0x6333bd0:assert h.word(sp+8)==0
   h.return_stub(0x12345678 if address==0x630d470 else strings+1024)
  elif address==search:
   ptr=h.word(sp+4);ch=h.word(sp+8)&255;result=0
   for i in range(1024):
    b=uc.mem_read(ptr+i,1)[0]
    if b==ch:result=ptr+i;break
    if not b:break
   h.return_stub(result)
  elif address==log:
   assert h.word(sp+4)==0x100001 and h.word(sp+16)==0x126
   assert text(h.word(sp+8))==b'%s(%d) : *** ERROR: Invalid bool value %s in .ini file %s\n'
   assert text(h.word(sp+12))==b'E:\\FL\\Scratch\\Source\\Common\\Ini.cpp'
   logs.append(('invalid_text_bool',text(h.word(sp+20)),text(h.word(sp+24))));h.return_stub(0)
  elif address==compare:
   a=text(h.word(sp+4)).lower();b=text(h.word(sp+8)).lower();h.return_stub(((a>b)-(a<b))&0xffffffff)
  elif address==atoi:
   value=text(h.word(sp+4));m=re.match(rb'\s*([+-]?\d+)',value);number=int(m.group(1)) if m else 0;h.return_stub(number&0xffffffff)
  elif address==sprintf:
   dst=h.word(sp+4);fmt=text(h.word(sp+8))
   if fmt==b'%d':value=h.word(sp+12);output=str(value if value<2**31 else value-2**32).encode()
   elif fmt==b'%g':output=format(struct.unpack('<d',bytes(uc.mem_read(sp+12,8)))[0],'.6g').encode()
   else:
    assert fmt==b'header [%s] value %s missing parameter %u';output=b'header ['+text(h.word(sp+12))+b'] value '+text(h.word(sp+16))+b' missing parameter '+str(h.word(sp+20)).encode()
   uc.mem_write(dst,output+b'\0');h.return_stub(len(output))
  elif address==message:
   assert h.word(sp+4)==0 and text(h.word(sp+12))==b'ERROR' and h.word(sp+16)==0
   logs.append(text(h.word(sp+8)));h.return_stub(1);uc.reg_write(UC_X86_REG_ESP,sp+20)
  elif address==ftol+6:
   bits=bytes(uc.mem_read(fp,10));mantissa,signexp=struct.unpack('<QH',bits);exponent=signexp&0x7fff
   shift=exponent-16383-63
   magnitude=mantissa<<shift if shift>=0 else mantissa>>(-shift)
   value=-magnitude if signexp&0x8000 else magnitude
   if exponent==0x7fff or not -2**63<=value<2**63:value=-2**63
   h.return_stub(value&0xffffffff);uc.reg_write(UC_X86_REG_EDX,(value>>32)&0xffffffff)
 atof=h.stop+0x380;h.write_word(0x63992f0,atof)
 uc.mem_write(atof,b'\xdd\x05'+struct.pack('<I',fp+32)+b'\xc3')
 lower=h.stop+0x3a0;h.write_word(0x63992f4,lower)
 strlower=h.stop+0x3c0;h.write_word(0x6399350,strlower);uc.mem_map(0x25000000,0x10000);heap_cursor=0x25000000
 h.write_word(0x63fbf0c,0x20507000)
 uc.hook_add(UC_HOOK_CODE,hook)
 rng=random.Random(2003);item=h.scratch+0x6000;calls=0;symbols=['?ReadEquipLine@Loadout@@YA_NAAVINI_Reader@@AAUEquipDesc@@@Z','?ReadCargoLine@Loadout@@YA_NAAVINI_Reader@@AAUEquipDesc@@@Z']
 def pair(symbol):
  nonlocal calls
  seed=rng.randbytes(32);outputs=[]
  for exports,obj in [(orig,o),(new,r)]:
   logs.clear();uc.mem_write(item,seed);ret=h.invoke(exports[symbol],(obj,item))&255
   outputs.append((ret,bytes(uc.mem_read(item,32)),list(logs)))
  assert outputs[0]==outputs[1],(symbol,outputs)
  assert bytes(uc.mem_read(o,0x1568))==bytes(uc.mem_read(r,0x1568))
  calls+=1
 text_inputs=[b'gun,HpWeapon01,0.75',b'123,,',b'0',b'-42,2,0,0.25,true',b'gun,5,1,0.9,false',b'cargo,2,HpCargo,1,TRUE',b'cargo,2,nan,0.5,1',b'cargo,2,,0.5,255',b'gun,1,0,0.1,garbage']
 for payload in text_inputs:
  for obj in [o,r]:uc.mem_write(obj+0x1564,b'\0');uc.mem_write(obj+0x828,payload+b'\0')
  for symbol in symbols:pair(symbol)
 for _ in range(300):
  count=rng.randrange(6);values=[]
  for i in range(count):
   tag=rng.randrange(4);bits=rng.randrange(256) if tag==0 else rng.randrange(2**32) if tag==1 else struct.unpack('<I',struct.pack('<f',rng.choice([0.,-0.,0.5,1.,-2.,float('nan')])))[0] if tag==2 else 32+32*i
   if tag==3:uc.mem_write(strings+bits,rng.choice([b'gun',b'0',b'123',b'HpWeapon',b'1.5',b'true',b'false',b'nan'])+b'\0')
   uc.mem_write(parameter+5*i,struct.pack('<BI',tag,bits))
  uc.mem_write(entry,struct.pack('<HB',7,count))
  for obj in [o,r]:uc.mem_write(obj+0x1564,b'\1');h.write_word(obj+0x145c,entry)
  for symbol in symbols:pair(symbol)
 corpus_base=0x24000000;uc.mem_map(corpus_base,0x100000);corpus_files=[];navigation_calls=0;corpus_start=calls
 header_symbol='?read_header@INI_Reader@@QAE_NXZ';value_symbol='?read_value@INI_Reader@@QAE_NXZ';name_symbol='?get_name_ptr@INI_Reader@@QAEPBDXZ'
 def navigation(symbol):
  nonlocal navigation_calls
  a=h.invoke(orig[symbol],(),o);b=h.invoke(new[symbol],(),r)
  if symbol!=name_symbol:a&=255;b&=255
  assert a==b and bytes(uc.mem_read(o,0x1568))==bytes(uc.mem_read(r,0x1568)),symbol
  navigation_calls+=1;return a
 for path in sorted((ROOT/'original/_FL Fresh Install-deutsch').rglob('loadout*.ini')):
  blob=path.read_bytes();assert blob[:4]==b'BINI';table=struct.unpack_from('<I',blob,8)[0];uc.mem_write(corpus_base,blob)
  for obj in [o,r]:
   uc.mem_write(obj,b'\0'*0x1568);h.write_word(obj+4,strings+512);h.write_word(obj+0x1440,corpus_base);h.write_word(obj+0x1444,len(blob));h.write_word(obj+0x1448,12);h.write_word(obj+0x144c,corpus_base);h.write_word(obj+0x1450,corpus_base+table);uc.mem_write(obj+0x1564,b'\1')
  sections=0;entries=0;equipment=0;cargo=0
  while navigation(header_symbol)&255:
   sections+=1
   while navigation(value_symbol)&255:
    entries+=1;ptr=navigation(name_symbol);key=text(ptr).lower()
    if key==b'equip':pair(symbols[0]);equipment+=1
    elif key==b'cargo':pair(symbols[1]);cargo+=1
  corpus_files.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path),bytes=len(blob),sections=sections,entries=entries,equipment=equipment,cargo=cargo))
 report=dict(status='passed',differential_calls=calls,corpus_loadout_calls=calls-corpus_start,navigation_calls=navigation_calls,corpus_files=corpus_files,text_inputs=len(text_inputs),binary_inputs=300,source_hashes={p:digest(ROOT/p) for p in ['tests/verify_loadout_hash_x86.py','src/loadout_lines.cpp','tests/fixtures/loadout_reader_hash_runtime.cpp','tests/fixtures/loadout_reader_runtime.cpp','src/create_id.cpp']},fixture_sha256=digest(dll),fixture_build_sha256=digest(ROOT/'analysis/loadout-hash-fixture-build.json'),reader_reconstructed=True,hash_reconstructed=True,interning_modeled=True,not_verified=['Reconstructed cache integration','Native CRT/OS','Exact instruction matching'])
 (ROOT/'analysis/loadout-hash-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {calls-corpus_start} real Loadout calls, {navigation_calls} navigation calls across {len(corpus_files)} files, plus {corpus_start} synthetic calls')
if __name__=='__main__':main()
