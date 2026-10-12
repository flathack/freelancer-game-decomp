#!/usr/bin/env python3
"""Compare original INI_Reader BINI navigation/state with reconstructed x86 code."""
import hashlib,json,pathlib,random,struct,subprocess,sys
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def make_bini(sections):
 table=bytearray();offsets={}
 def name(s):
  if s not in offsets:offsets[s]=len(table);table.extend(s+b'\0')
  return offsets[s]
 records=bytearray()
 for section,values in sections:
  records.extend(struct.pack('<HH',name(section),len(values)))
  for key,parameters in values:
   records.extend(struct.pack('<HB',name(key),len(parameters)))
   for tag,bits in parameters:records.extend(struct.pack('<BI',tag,bits))
 return struct.pack('<III',0x494e4942,1,12+len(records))+records+table

def main():
 assert digest(SOURCE)==HASH
 methods={
 'header':'?read_header@INI_Reader@@QAE_NXZ','value':'?read_value@INI_Reader@@QAE_NXZ','find':'?find_header@INI_Reader@@QAE_NPBD@Z',
 'header_name':'?get_header_ptr@INI_Reader@@QAEPBDXZ','value_name':'?get_name_ptr@INI_Reader@@QAEPBDXZ','count':'?get_num_parameters@INI_Reader@@QBEIXZ',
 'empty':'?is_value_empty@INI_Reader@@QAE_NI@Z','is_header':'?is_header@INI_Reader@@QAE_NPBD@Z','is_value':'?is_value@INI_Reader@@QAE_NPBD@Z',
 'end':'?is_end@INI_Reader@@QBE_NXZ','seek':'?seek@INI_Reader@@QAEXI@Z','tell':'?tell@INI_Reader@@QBEIXZ','reset':'?reset@INI_Reader@@QAEXXZ',
 'get_state':'?get_state@INI_Reader@@QBEXAAUState@1@@Z','set_state':'?set_state@INI_Reader@@QAEXABUState@1@@Z'}
 commands=[];build=ROOT/'build';objects=[]
 for source in ['src/ini_reader.cpp','src/file_map.cpp','tests/fixtures/file_map_x86_runtime.cpp','tests/fixtures/ini_reader_x86_runtime.cpp']:
  out=build/(pathlib.Path(source).stem+'-bini.obj');objects.append(str(out))
  cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/source),'-o',str(out)];subprocess.run(cmd,check=True);commands.append(cmd)
 helper='?initialize_binary@INI_Reader@@QAE_NXZ';dll=build/'bini_reader.dll'
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x16000000',f'/out:{dll}']+objects+['/export:'+n for n in list(methods.values())+[helper]];subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(dll);uc=h.uc
 uc.mem_map(0x23000000,0x400000);data=0x23000000;o=h.scratch;r=o+0x2000;os=o+0x5000;rs=o+0x6000;input_name=o+0x8000
 def text(p):
  result=bytearray()
  for i in range(65536):
   b=uc.mem_read(p+i,1)[0]
   if not b:return bytes(result)
   result.append(b)
  raise AssertionError('Unterminated name')
 def hook(uc,address,size,user):
  if address==h.stop+64:
   sp=uc.reg_read(UC_X86_REG_ESP);a=text(h.word(sp+4)).lower();b=text(h.word(sp+8)).lower();h.return_stub(((a>b)-(a<b))&0xffffffff)
 uc.hook_add(UC_HOOK_CODE,hook);h.write_word(0x639902c,h.stop+64)
 calls=0;visited_headers=0;visited_values=0;seen=set();corpus=[];current_label='none'
 checkpoint_path=ROOT/'analysis/bini-corpus-checkpoint.json'
 guard_paths=['src/ini_reader.cpp','src/ini_reader.hpp','src/file_map.cpp','src/file_map.hpp','tests/fixtures/ini_reader_x86_runtime.cpp','tests/fixtures/file_map_x86_runtime.cpp','tests/verify_bini_reader_x86.py','tests/x86_harness.py']
 guard={p:digest(ROOT/p) for p in guard_paths}
 checkpoint=json.loads(checkpoint_path.read_text()) if checkpoint_path.exists() else {}
 cached=checkpoint.get('files',{}) if checkpoint.get('guard')==guard else {}
 def save_checkpoint():
  temp=checkpoint_path.with_suffix('.tmp');temp.write_text(json.dumps(dict(guard=guard,files=cached),indent=2)+'\n');temp.replace(checkpoint_path)
 def snapshot(obj):return bytes(uc.mem_read(obj+0x1428,0x3c))+bytes(uc.mem_read(obj+0x1564,1))
 def pair(key,args=(),new_args=None):
  nonlocal calls
  if new_args is None:new_args=args
  try:
   a=h.invoke(orig[methods[key]],args,o,max_instructions=20000000);b=h.invoke(new[methods[key]],new_args,r,max_instructions=20000000)
  except Exception as e:raise RuntimeError(f'{current_label}: {key}') from e
  if key not in ['seek','reset','get_state','set_state']:
   if key in ['header','value','find','empty','is_header','is_value','end']:a&=255;b&=255
   assert a==b,(key,a,b)
  assert snapshot(o)==snapshot(r),(key,snapshot(o).hex(),snapshot(r).hex())
  calls+=1;seen.add(methods[key]);return a
 def setup(blob):
  uc.mem_write(data,blob)
  for obj in [o,r]:
   uc.mem_write(obj,b'\0'*0x1568);h.write_word(obj+0x1440,data);h.write_word(obj+0x1444,len(blob));uc.mem_write(obj+0x1564,b'\1')
  a=h.invoke(0x630fc60,this=o+0x1428)&255;b=h.invoke(new[helper],this=r)&255
  assert a==b and snapshot(o)==snapshot(r)
  return bool(a)
 def walk(blob,label):
  nonlocal visited_headers,visited_values,calls,current_label
  current_label=label;checksum=hashlib.sha256(blob).hexdigest()
  previous=cached.get(label)
  if previous and previous['sha256']==checksum:
   corpus.append(previous);calls+=previous.get('calls',0);visited_headers+=previous.get('headers',0);visited_values+=previous.get('values',0);seen.update(previous.get('methods',[]));return
  before_calls=calls
  accepted=setup(blob)
  if not accepted:
   assert label.startswith('original/'), 'Synthetic valid BINI unexpectedly rejected'
   row=dict(label=label,sha256=checksum,bytes=len(blob),recognition='rejected_by_original_and_reconstruction',calls=0,methods=[])
   corpus.append(row);cached[label]=row;save_checkpoint();return
  headers=[];values=0
  pair('reset')
  while pair('header'):
   visited_headers+=1;header=text(pair('header_name'));headers.append(header)
   uc.mem_write(input_name,header.swapcase()+b'\0');assert pair('is_header',(input_name,))
   # State round-trip must restore offset pointers and preserve unwritten State bytes.
   uc.mem_write(os,b'\xaa'*0xc08);uc.mem_write(rs,b'\xaa'*0xc08);pair('get_state',(os,),(rs,));assert bytes(uc.mem_read(os,0xc08))==bytes(uc.mem_read(rs,0xc08))
   pair('seek',(0xffffffff,));pair('set_state',(os,),(rs,))
   while pair('value'):
    visited_values+=1;values+=1;key=text(pair('value_name'));uc.mem_write(input_name,key.swapcase()+b'\0');assert pair('is_value',(input_name,))
    n=pair('count');pair('empty',(n,));assert pair('empty',(n+1,))
    if n:assert not pair('empty',(0,))
    pair('tell');pair('end')
   # The last value pointer remains unchanged when read_value reports count exhaustion.
  assert pair('end')
  if headers:
   uc.mem_write(input_name,headers[-1].swapcase()+b'\0');assert pair('find',(input_name,))
  uc.mem_write(input_name,b'__not_a_real_section__\0');assert not pair('find',(input_name,))
  row=dict(label=label,sha256=checksum,bytes=len(blob),headers=len(headers),values=values,calls=calls-before_calls,methods=sorted(seen))
  corpus.append(row);cached[label]=row;save_checkpoint()
 rng=random.Random(2003)
 for i in range(40):
  sections=[]
  for j in range(rng.randrange(1,5)):
   values=[]
   for k in range(rng.randrange(5)):
    parameters=[(rng.randrange(4),rng.randrange(2**32)) for _ in range(rng.randrange(5))]
    values.append((f'key{k}'.encode(),parameters))
   sections.append((f'Section{j}'.encode(),values))
  walk(make_bini(sections),f'synthetic-{i}')
 # Real game BINI corpus: complete navigation of the 20 smallest encoded INI files.
 candidates=[]
 for path in (ROOT/'original/_FL Fresh Install-deutsch/DATA').rglob('*'):
  if path.is_file() and path.suffix.lower()=='.ini':
   with path.open('rb') as f:magic=f.read(4)
   if magic==b'BINI':candidates.append(path)
 selected=sorted(candidates,key=lambda p:(p.stat().st_size,str(p)))
 if '--all-files' not in sys.argv:selected=selected[:20]
 for index,path in enumerate(selected):
  walk(path.read_bytes(),str(path.relative_to(ROOT)))
  if (index+1)%100==0:print(f'CORPUS {index+1}/{len(selected)} files; {calls} differential calls',flush=True)
 # Recognition checks: version is not validated by this original helper.
 recognition=0
 good=make_bini([(b'A',[])])
 for blob,expected in [(b'x',False),(b'NOT!'+good[4:],False),(good[:8]+struct.pack('<I',len(good))+good[12:],False),(good[:4]+struct.pack('<I',999)+good[8:],True)]:
  assert setup(blob)==expected;recognition+=1
 report=dict(status='passed_binary_navigation',original_sha256=HASH,compiled_dll_sha256=digest(dll),
             source_hashes={p:digest(ROOT/p) for p in ['src/ini_reader.cpp','src/ini_reader.hpp','src/file_map.cpp','src/file_map.hpp','tests/fixtures/ini_reader_x86_runtime.cpp','tests/fixtures/file_map_x86_runtime.cpp']},
             differential_calls=calls,covered_original_methods=sorted(seen),headers_visited=visited_headers,values_visited=visited_values,recognition_cases=recognition,instruction_budget_per_call=20000000,checkpoint_guard=guard,selected_real_files=len(selected),total_real_bini_files=len(candidates),corpus=corpus,commands=commands,
             mocks=['ASCII stricmp'],not_verified=['Text read_header/read_value paths (explicit pending traps)','Typed numeric/string parameter getters','INI open/close and constructor lifecycle','Malformed record trust boundaries','Non-ASCII comparison','Exact instruction matching'])
 (ROOT/'analysis/bini-reader-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS BINI: {calls} calls / {len(seen)} methods; {visited_headers} sections and {visited_values} entries across {len(corpus)} synthetic/real files')
if __name__=='__main__':main()
