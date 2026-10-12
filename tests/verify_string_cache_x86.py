#!/usr/bin/env python3
"""Differential arena allocation, case-insensitive interning and RB-tree layout."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert digest(SOURCE)==HASH
 build=ROOT/'build';commands=[]
 for source,out in [('src/string_cache.cpp','string_cache.obj'),('tests/fixtures/string_cache_x86_runtime.cpp','string_cache_runtime.obj')]:
  cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/source),'-o',str(build/out)];subprocess.run(cmd,check=True);commands.append(cmd)
 names=['?StringAlloc@@YAPADPBD_N@Z','?clear@CacheString@@QAEXXZ','?StringCacheArena@@3PADA','?StringCacheFront@@3IA','?StringCacheBack@@3IA','?StringCacheInternedCount@@3IA','?StringCachePrivateCount@@3IA','?StringCacheIndex@@3PAUStringCacheTree@@A']
 cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x12000000',f'/out:{build}/string_cache.dll',str(build/'string_cache.obj'),str(build/'string_cache_runtime.obj')]+['/export:'+n+(',DATA' if n not in names[:2] else '') for n in names]+['/export:?StringShutdown@@YAXXZ']
 subprocess.run(cmd,check=True);commands.append(cmd)
 h=X86Harness();orig=h.load(SOURCE);new=h.load(build/'string_cache.dll');uc=h.uc;uc.mem_map(0,4096);uc.mem_map(0x21000000,0x40000)
 heap=0x21000000;allocations=[];logs=[];freed=[]
 def text(p):
  out=bytearray()
  for i in range(4096):
   b=uc.mem_read(p+i,1)[0]
   if not b:return bytes(out)
   out.append(b)
  raise AssertionError('Unterminated string')
 def hook(uc,addr,size,user):
  nonlocal heap
  sp=uc.reg_read(UC_X86_REG_ESP)
  if addr==0x6391abc:
   n=h.word(sp+4);assert n in [20,24];p=heap;heap+=(n+15)&~15;allocations.append(n);h.return_stub(p)
  elif addr==0x6391a7a:
   freed.append(h.word(sp+4));h.return_stub(0)
  elif addr==h.stop+32:
   logs.append(('original',h.word(sp+16)));h.return_stub(0)
  elif addr==h.stop+48:
   logs.append(('compiled',h.word(sp+4)));h.return_stub(0)
  elif addr==h.stop+64:
   a=text(h.word(sp+4)).lower();b=text(h.word(sp+8)).lower();h.return_stub(((a>b)-(a<b))&0xffffffff)
 uc.hook_add(UC_HOOK_CODE,hook)
 h.write_word(0x639902c,h.stop+64);h.write_word(0x6399028,h.stop+0x100);h.write_word(h.stop+0x100,h.stop+32)
 oa=0x6409810;ra=new[names[2]]
 og=[0x63ecb6c,0x63ecb70,0x63ecb74,0x6589810,0x6589814];rg=[new[n] for n in names[3:]]
 def tree(index,arena):
  t=h.word(index)
  if not t:return None
  head=h.word(t+4);nil=h.word(t+8)
  def node(p):
   if p==nil:return None
   return (text(h.word(p+12)).hex(),h.word(p+16)-arena,uc.mem_read(p+20,1)[0],node(h.word(p)),node(h.word(p+8)))
  def validate(p,parent):
   if p==nil:return
   assert h.word(p+4)==parent
   validate(h.word(p),p);validate(h.word(p+8),p)
  validate(h.word(head+4),head)
  return (h.word(t+16),node(h.word(head+4)),None if h.word(head)==head else text(h.word(h.word(head)+12)).hex(),None if h.word(head+8)==head else text(h.word(h.word(head+8)+12)).hex())
 rng=random.Random(2003);cases=[(None,False),(b'',False),(b'BAY',False),(b'bay',False),(b'BaY',False),(b'BAY',True),(b'bay',True)]
 for i in range(400):
  value=('HP_%04d'%rng.randrange(180)).encode();value=value.upper() if i%2 else value.lower();cases.append((value,i%7==0))
 for value,private in cases:
  ptr=0
  if value is not None:ptr=h.scratch;uc.mem_write(ptr,value+b'\0')
  a=h.invoke(orig[names[0]],(ptr,int(private)));b=h.invoke(new[names[0]],(ptr,int(private)))
  assert a-oa==b-ra,(value,private,a-oa,b-ra)
  assert text(a)==text(b)
  assert [h.word(x) for x in og[:4]]==[h.word(x) for x in rg[:4]],'Arena cursor/count mismatch'
  assert tree(og[4],oa)==tree(rg[4],ra),'RB tree shape/color/identity mismatch'
 # Boundary cases use the original writable cursor globals to constrain free space.
 boundary_cases=0
 for private in [False,True]:
  for remaining in [0,2,3,4]:
   front=0x4000+boundary_cases*64;back=front+remaining
   for globals_ in [og,rg]:h.write_word(globals_[0],front);h.write_word(globals_[1],back)
   uc.mem_write(h.scratch,b'ZZ\0')
   # Use new distinct strings for intern mode to avoid cached-hit short circuit.
   uc.mem_write(h.scratch,bytes([65+boundary_cases,90])+b'\0')
   before=len(logs);a=h.invoke(orig[names[0]],(h.scratch,int(private)));b=h.invoke(new[names[0]],(h.scratch,int(private)))
   assert a-oa==b-ra;assert text(a)==text(b)
   assert [h.word(x) for x in og[:4]]==[h.word(x) for x in rg[:4]]
   if remaining<3:assert logs[before:]==[('original',0xb9 if private else 0xa9),('compiled',0xb9 if private else 0xa9)]
   else:assert len(logs)==before
   boundary_cases+=1
 h.write_word(h.scratch,0x12345678);h.write_word(h.scratch+4,0x87654321)
 h.invoke(orig[names[1]],this=h.scratch);h.invoke(new[names[1]],this=h.scratch+4)
 assert h.word(h.scratch)==oa and h.word(h.scratch+4)==ra
 # Compare exact deallocation order by each node's identity and sentinel role.
 def identities(index,arena):
  t=h.word(index)
  if not t:return {}
  head=h.word(t+4);nil=h.word(t+8);result={t:('tree',),head:('head',),nil:('nil',)}
  def visit(ptr):
   if ptr==nil:return
   result[ptr]=('node',h.word(ptr+12)-arena)
   visit(h.word(ptr));visit(h.word(ptr+8))
  visit(h.word(head+4));return result
 def shutdown_pair():
  tables=[h.word(og[4]),h.word(rg[4])]
  before_counters=[[h.word(x) for x in g[:4]] for g in [og,rg]]
  orders=[]
  for exports,globals_,arena in [(orig,og,oa),(new,rg,ra)]:
   ids=identities(globals_[4],arena);start=len(freed)
   h.invoke(exports['?StringShutdown@@YAXXZ'])
   orders.append([ids[p] for p in freed[start:]])
   assert h.word(globals_[4])==0
  assert orders[0]==orders[1], 'Deallocation order mismatch'
  assert [[h.word(x) for x in g[:4]] for g in [og,rg]]==before_counters
  for t in tables:
   if t:assert h.word(t+4)==h.word(t+8)==h.word(t+16)==0
  return orders[0]
 first_order=shutdown_pair();assert first_order[-3:]==[('head',),('nil',),('tree',)]
 assert shutdown_pair()==[]
 # Re-initialize without rewinding the existing arena (normal StringShutdown semantics).
 for globals_ in [og,rg]:h.write_word(globals_[1],0x180000)
 prior_front=h.word(og[0]);uc.mem_write(h.scratch,b'BAY\0')
 a=h.invoke(orig[names[0]],(h.scratch,0));b=h.invoke(new[names[0]],(h.scratch,0))
 assert a-oa==b-ra==prior_front
 assert tree(og[4],oa)==tree(rg[4],ra)
 second_order=shutdown_pair();assert len(second_order)==4
 assert shutdown_pair()==[]
 report=dict(status='passed',original_sha256=HASH,compiled_dll_sha256=digest(build/'string_cache.dll'),
             source_hashes={p:digest(ROOT/p) for p in ['src/string_cache.cpp','src/string_cache.hpp','tests/fixtures/string_cache_x86_runtime.cpp']},
             sequence_cases=len(cases),capacity_boundary_cases=boundary_cases,tree_shape_checks=len(cases),clear_checked=True,shutdown_checks=['exact node/head/nil/tree free order','idempotent shutdown','arena/counters preserved','reinitialization at existing front cursor','freed tree fields nulled'],first_shutdown_allocations_freed=len(first_order),second_shutdown_allocations_freed=len(second_order),
             commands=commands,mocks=['operator new succeeds','ASCII case-insensitive stricmp','overflow logger records line'],
             not_verified=['Exact instruction matching','CRT locale/non-ASCII comparison','Allocation failure/SEH','Thread safety'])
 (ROOT/'analysis/stringcache-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f'PASS: {len(cases)} allocations/intern hits with exact RB-tree shapes, {boundary_cases} capacity cases, clear and shutdown/reinitialization')
if __name__=='__main__':main()
