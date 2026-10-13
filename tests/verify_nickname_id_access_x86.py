#!/usr/bin/env python3
"""Goods nickname/Loadout ID access with actual reconstructed CreateID and lookup."""
import hashlib,json,pathlib,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP
from x86_harness import X86Harness
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert hashlib.sha256(original.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 files=['src/nickname_id_access.cpp','src/good_id_lookup.cpp','src/good_archetype_lookup.cpp','src/create_id.cpp','tests/fixtures/flid_x86_runtime.cpp'];objects=[]
 for f in files:
  obj=ROOT/'build'/(pathlib.Path(f).stem+'-nickname.obj');objects.append(str(obj));subprocess.run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/f),'-o',str(obj)],check=True)
 find='?find_by_nickname@GoodList@@YAPBUGoodInfo@@PBD@Z';getid='?GetID@Loadout@@YAIPBD@Z';dll=ROOT/'build/nickname_id_access.dll';subprocess.run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x1d000000',f'/out:{dll}']+objects+['/export:'+find,'/export:'+getid,'/export:GoodIDTree,DATA'],check=True)
 h=X86Harness();orig=h.load(original);new=h.load(dll);uc=h.uc;heap=0x23000000;uc.mem_map(heap,0x40000);cursor=heap+0x20000;lower=h.stop+256;h.write_word(0x6399350,lower);nameptr=h.scratch;calls=0;rng=random.Random(2003)
 def text(p):
  out=b''
  while uc.mem_read(p,1)[0]:out+=bytes(uc.mem_read(p,1));p+=1
  return out
 def hook(uc,address,size,user):
  nonlocal cursor
  sp=uc.reg_read(UC_X86_REG_ESP)
  if address==0x6391abc:
   n=h.word(sp+4);assert n in [8,0x41c];p=cursor;cursor+=(n+15)&~15;uc.mem_write(p,b'\0'*n);h.return_stub(p)
  elif address==lower:p=h.word(sp+4);uc.mem_write(p,text(p).lower()+b'\0');h.return_stub(p)
 uc.hook_add(UC_HOOK_CODE,hook)
 names=[None,b'',b'gun',b'GUN',b'cargo',b'commodity',b'A'*255]+[bytes(rng.choice(b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-') for _ in range(rng.randrange(1,80))) for _ in range(500)]
 keys={};values={};ids=[]
 for name in names:
  if name is not None:uc.mem_write(nameptr,name+b'\0')
  arg=0 if name is None else nameptr;a=h.invoke(orig[getid],(arg,));b=h.invoke(new[getid],(arg,));assert a==b;calls+=1;ids.append(a)
  if a not in keys:keys[a]=len(keys)
 head=heap;nil=heap+64;ordered=sorted(keys);nodes={key:heap+128+i*32 for i,key in enumerate(ordered)}
 def build(lo,hi,parent):
  if lo==hi:return nil
  mid=(lo+hi)//2;key=ordered[mid];node=nodes[key];left=build(lo,mid,node);right=build(mid+1,hi,node);good=heap+0x8000+mid*128 if mid%5 else 0;values[key]=good;uc.mem_write(node,struct.pack('<IIIII',left,parent,right,key,good));return node
 root=build(0,len(ordered),head);uc.mem_write(head,struct.pack('<IIII',nil,root,nil,0));uc.mem_write(nil,struct.pack('<IIII',nil,nil,nil,0))
 for tree in [0x63fab80,new['GoodIDTree']]:uc.mem_write(tree,struct.pack('<III',0,head,nil))
 for name,key in zip(names,ids):
  if name is not None:uc.mem_write(nameptr,name+b'\0')
  arg=0 if name is None else nameptr;a=h.invoke(orig[find],(arg,));b=h.invoke(new[find],(arg,));assert a==b==values[key];calls+=1
 for name in [b'absent-nickname',b'__missing__',b'no-such-good']:
  uc.mem_write(nameptr,name+b'\0');a=h.invoke(orig[find],(nameptr,));b=h.invoke(new[find],(nameptr,));assert a==b==0;calls+=1
 report=dict(status='passed',differential_calls=calls,names=len(names),source_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['src/cfl_id_maker.hpp','src/loadout_tree.hpp','tests/verify_nickname_id_access_x86.py']},hash_and_lookup_reconstructed=True,not_verified=['Real Goods database loading','Allocation failure logging','Native CRT non-ASCII locale','Exact instruction matching'])
 (ROOT/'analysis/nickname-id-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {calls} nickname/Loadout ID accesses, actual hashes and exact Goods pointers')
if __name__=='__main__':main()
