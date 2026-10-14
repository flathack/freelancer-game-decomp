#!/usr/bin/env python3
"""FLA-263 ownership differential probes; no modeled copying/lifetime bodies.
Independent write sets: analysis/fla263/ownership-expectations.md, frozen first.
"""
import argparse
import collections
import itertools
import hashlib
import json
import pathlib
import random
import struct
import subprocess
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
from verify_archetype_metadata_x86 import Machine as ReaderMachine, SCN, GETEQ, GETID, READERS, VT
from x86_harness import X86Harness

ROOT=pathlib.Path(__file__).resolve().parents[1]
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
U=lambda n:struct.pack('<I',n&0xffffffff)
REGS=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
VALUES=[0x12345678,0x23456789,0x3456789a,0x456789ab]
DEFAULTS=[0x62eff70,0x62f3db0,0x62f5290]
COPIES=[0x62f0170,0x626d530,0x626e000]
DELETING=[0x62f0040,0x626d5e0,0x626e0f0]
KINDS=['root','equipment','attached']
SIZES=[0x5c,0x70,0x88]
LVT=['archetype_lifetime_'+k+'_slots' for k in KINDS]
OVT=[0x63a11c0,0x6399860,0x6399af4]
ASSIGN={0x62f0340:'archetype_root_assign',0x626ddb0:'archetype_equipment_assign',0x626e070:'archetype_attached_assign',0x626eaf0:'archetype_assign_0626eaf0',0x626dbb0:'archetype_assign_0626dbb0',0x626e2c0:'archetype_assign_0626e2c0',0x626f660:'archetype_assign_0626f660',0x626f870:'archetype_assign_0626f870',0x626fa10:'archetype_assign_0626fa10'}
ROOT_WORDS=[8,12,16,20,24,28,32,36,40,44,48,52,60,64,68]
EQ_WORDS=ROOT_WORDS+[0x5c,0x64,0x68]
EQ_BYTES=[0x38,0x39,0x60,0x6c]
# Independent frozen class field sets, not read from reconstructed switch.
CLASS_FIELDS={
8:([],[]),9:(list(range(0x70,0x88,4)),[]),10:([0x70,0x74,0x78],[]),
11:([0x70,0x74,0x78,0x7c],[]),12:([0x70,0x74,0x78,0x7c,0x80,0x88],[0x84]),
13:(list(range(0x70,0x88,4)),[]),14:(list(range(0x70,0xa8,4)),[]),
15:(list(range(0x70,0x90,4)),[]),16:(list(range(0x70,0xa0,4)),[]),
17:(list(range(0x70,0xb8,4))+[0xd0],[0xb8,0xb9,0xba,0xcc]),
18:(list(range(0x70,0xa0,4)),[]),19:(list(range(0x70,0xa4,4)),[]),
20:([0x70,0x74,0x78],[]),21:([],[0x70,0x71]),22:([0x70,0x74],[]),23:([],[]),
24:([0x70],[]),25:([0x70],[]),26:([0x70],[]),27:([0x70],[]),
28:(list(range(0x70,0x9c,4)),[]),29:([],[]),
31:([0x70,0x74]+list(range(0x7c,0xac,4)),[0x78,0x79,0xac]),
32:([0x70,0x74]+list(range(0x7c,0x94,4)),[0x78,0x79]),
33:([0x70,0x74]+list(range(0x7c,0x8c,4)),[0x78,0x79])}

def build(source=None,label='ownership'):
    dest=ROOT/'build/fla263-ownership';dest.mkdir(parents=True,exist_ok=True)
    fixture=dest/'metadata-runtime-real-inherit.cpp'
    content=(ROOT/'tests/fixtures/archetype_metadata_runtime.cpp').read_text()
    for needle in [
        'extern "C" __declspec(naked) void arch_inherit_dispatch(void*,void*) { JUMP(062f3e20h) }',
        'extern "C" void* arch_inherit_node(ArchWord id) {\n    void* result;\n    using Query=void*(__thiscall*)(void*,void**,const ArchWord*);\n    reinterpret_cast<Query>(0x063015d0)(reinterpret_cast<void*>(0x063fbad4),&result,&id);\n    return result;\n}',
        'extern "C" void* arch_inherit_sentinel() { return *reinterpret_cast<void**>(0x063fbad8); }',
    ]:
        assert content.count(needle)==1
        content=content.replace(needle,'// Real ownership/query body linked from archetype_ownership.cpp.')
    fixture.write_text(content)
    good_fixture=dest/'good-block-runtime-real-comm.cpp'
    good_content=(ROOT/'tests/fixtures/good_block_reader_runtime.cpp').read_text()
    old_vtable='extern "C" unsigned int good_info_runtime_vtable(bool) { return 0x063993e8; }'
    assert good_content.count(old_vtable)==1
    good_fixture.write_text(good_content.replace(old_vtable,'// Real GoodInfo/CommReferrable production vtable binding linked.'))
    files=[source or ROOT/'src/archetype_ownership.cpp',ROOT/'src/archetype_metadata.cpp',ROOT/'src/good_info_comm.cpp',ROOT/'src/good_info_initialize.cpp',fixture,good_fixture]
    files += [ROOT/f for f in ['tests/fixtures/archetype_ownership_runtime.cpp','src/create_id.cpp','src/string_cache.cpp','src/archetype_id.cpp','src/archetype_equipment_lookup.cpp','src/good_block_reader.cpp','src/good_info_price.cpp','src/good_info_destroy.cpp','tests/fixtures/flid_x86_runtime.cpp','tests/fixtures/string_cache_x86_runtime.cpp','tests/fixtures/archetype_lookup_runtime.cpp']]
    commands=[];objects=[]
    for f in files:
        obj=dest/(f.stem+'-'+label+'.obj');objects.append(str(obj))
        cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-Wall','-Wextra','-Werror','-I'+str(ROOT/'src'),'-c',str(f),'-o',str(obj)]
        subprocess.run(cmd,check=True);commands.append({'argv':cmd,'exit_code':0})
    symbols=READERS+['archetype_equipment_is_attached','archetype_attached_is_attached','arch_virtual_read','arch_virtual_attached','arch_diagnostic','arch_hash','arch_cache_clear','arch_string_alloc','create_id_reconstructed','?CreateID@@YAIPBD@Z',GETEQ,GETID,'good_info_read_block','good_block_find_good','good_block_find_hull','good_block_unknown_category','??1GoodInfo@@QAE@XZ']+SCN[:2]+list(ASSIGN.values())
    symbols += ['archetype_'+k+'_'+op for k in KINDS for op in ['default','copy','deleting']]+['archetype_root_destroy','archetype_pointer_vector_assign','arch_inherit_dispatch','arch_inherit_node','arch_inherit_sentinel','arch_runtime_allocate','arch_runtime_free','arch_runtime_payload_heap_free','arch_runtime_array_destroy','good_info_read_comm']
    symbols += ['??0GoodInfo@@QAE@XZ','good_info_runtime_vtable']
    data=VT+LVT+SCN[2:]+['EquipmentArchetypeTree','good_info_comm_slots','good_info_comm_base_slots']
    dll=dest/(label+'.dll')
    cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x15000000','/out:'+str(dll)]+objects+['/export:'+s for s in symbols]+['/export:'+s+',DATA' for s in data]
    subprocess.run(cmd,check=True);commands.append({'argv':cmd,'exit_code':0})
    return dll,commands


class Machine(ReaderMachine):
    def __init__(self,dll,rebuilt):
        self.owned=[]
        manifest=json.loads((ROOT/'analysis/fla255/original-evidence.json').read_text())
        # Only exact new-kernel spans, not the explicitly reused service leaves.
        entries=set(DEFAULTS+COPIES+DELETING+list(ASSIGN)+[0x62f0230,0x626ddf0,0x62f3e20,0x62fb660,0x62fc530,0x62fd350,0x6319960,0x62fc150,0x6319400,0x6280e50,0x62fd090,0x62fd110,0x6280660,0x6343d40,0x6343d80,0x632e6a0,0x63015d0])
        # Manifest schema is checked below; never silently drop forbidden spans.
        for f in manifest['functions']:
            if int(f['entry_va'],16) in entries:
                for span in f['half_open_spans']:
                    self.owned.append((int(span['start_va'],16),int(span['end_va_exclusive'],16)))
        assert len(self.owned)>=len(entries)-1, 'missing original denial spans'
        self.observed_vptr=[];self.classes={};self.poison=False
        super().__init__(dll,rebuilt)
        self.client2=self.client+0x20
        self.customvt=self.h.scratch+0x7000
        for c in [self.client,self.client2]:self.h.write_word(c,self.clientvt)
        for slot,target in [(0,0x400),(4,0x420),(8,0x960),(28,0x440)]:self.h.write_word(self.clientvt+slot,self.h.stop+target)
        self.h.write_word(self.customvt+16,self.h.stop+0x460)
        self.h.write_word(0x639932c,self.h.stop+0x480)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.memwrite)
    def memwrite(self,u,access,address,size,value,user):
        if address==self.obj and size==4 and value in OVT+[self.new[n] for n in LVT]:
            self.observed_vptr.append(self.vkind(value))
    def vkind(self,p):
        for i,(o,n) in enumerate(zip(OVT,LVT)):
            if p in (o,self.new[n]):return i
        return p
    def hook(self,u,a,size,user):
        if self.rebuilt and any(lo<=a<hi for lo,hi in self.owned):raise AssertionError('FORBIDDEN ORIGINAL OWNERSHIP FALLBACK '+hex(a))
        if not hasattr(self,'new'):return
        h=self.h;sp=u.reg_read(UC_X86_REG_ESP);ecx=u.reg_read(UC_X86_REG_ECX)
        if a in (0x6391abc,self.new['arch_runtime_allocate']):
            n=h.word(sp+4);p=self.cursor;self.cursor+=max(16,(n+31)&~15);self.events.append(('allocate',n,p));self.ret(p);return
        if a in (0x6391a7a,self.new['arch_runtime_free']):
            p=h.word(sp+4);self.events.append(('free',p))
            if self.poison and self.heap<=p<self.heap+0x60000:
                length=self.alloc_sizes.get(p,0)
                if length:self.u.mem_write(p,b'\xdd'*length)
            self.ret(0xaabbccdd);return
        if a in (h.stop+0x480,self.new['arch_runtime_payload_heap_free']):
            self.events.append(('payload-heap-free',h.word(sp+4)));self.ret();return
        if a==0x6391b1c:
            self.events.append(('array-service',h.word(sp+4),h.word(sp+8),h.word(sp+12)))
            u.reg_write(UC_X86_REG_EIP,self.new['arch_runtime_array_destroy']);return
        if a==self.new['arch_runtime_array_destroy']:
            if self.rebuilt:self.events.append(('array-service',h.word(sp+4),h.word(sp+8),h.word(sp+12)))
            return
        if a in (h.stop+0x400,h.stop+0x420,h.stop+0x440):
            slot={h.stop+0x400:0,h.stop+0x420:4,h.stop+0x440:28}[a]
            self.events.append(('client',slot,ecx,h.word(sp+4) if slot==28 else None,h.word(self.obj+4),h.word(self.obj+8)))
            self.ret(0,4 if slot==28 else 0);return
        if a==h.stop+0x460:
            self.events.append(('class',ecx,self.classes[ecx]));self.ret(self.classes[ecx]);return
        if a==h.stop+0x960:
            self.events.append(('reader-client',ecx,h.word(sp+4)));self.ret(0,4);return
        if a in (0x62f3e20,self.new['arch_inherit_dispatch']):
            self.events.append(('real-inherit',h.word(sp+4),h.word(sp+8)));return
        if a==self.clear_entry:return # Execute actual existing CacheString::clear.
        super().hook(u,a,size,user)
    def reset_case(self,seed=17,poison=False):
        super().reset();self.rng=random.Random(seed);self.events=[];self.observed_vptr=[];self.poison=poison;self.alloc_sizes={}
        self.cursor=self.heap+0x1000
        self.u.mem_write(self.heap,self.rng.randbytes(0x60000))
        for p in (self.obj,self.source):self.u.mem_write(p-16,self.rng.randbytes(0x120))
    def tree_fixture(self,obj,count,base,client=0,subvectors=2):
        h=self.h;u=self.u;nil=base;head=base+0x80
        for off in (0,4,8):h.write_word(nil+off,0)
        u.mem_write(nil+0x40,b'\1\1');u.mem_write(head+0x40,b'\0\0')
        nodes=[base+0x100+i*0x80 for i in range(count)]
        def make(indices,parent):
            if not indices:return nil
            k=len(indices)//2;p=nodes[indices[k]]
            left=make(indices[:k],p);right=make(indices[k+1:],p)
            for off,value in [(0,left),(4,parent),(8,right),(12,indices[k]+123),(20,0)]:h.write_word(p+off,value)
            u.mem_write(p+0x40,b'\1\0')
            v=base+0x1000+indices[k]*0x40;length=indices[k]%3 if subvectors else 0
            h.write_word(p+0x34,v);h.write_word(p+0x38,v+length*4);h.write_word(p+0x3c,v+12)
            self.alloc_sizes[p]=0x44;self.alloc_sizes[v]=12
            return p
        root=make(list(range(count)),head)
        for off,val in [(0,nodes[0] if count else head),(4,root),(8,nodes[-1] if count else head)]:h.write_word(head+off,val)
        for off,val in [(0,self.customvt),(4,client),(0x4c,head),(0x50,nil),(0x58,count)]:h.write_word(obj+off,val)
        self.alloc_sizes[nil]=0x44;self.alloc_sizes[head]=0x44
        return nodes
    def vector_fixture(self,p,length,capacity,base,null=False):
        self.h.write_word(p+4,0 if null else base);self.h.write_word(p+8,0 if null else base+4*length);self.h.write_word(p+12,0 if null else base+4*capacity)
        self.alloc_sizes[base]=4*capacity
    def snapshot(self):
        def obj(p):
            raw=bytearray(self.u.mem_read(p-16,0x120));raw[16:20]=U(self.vkind(self.h.word(p)))
            for off in (12,128):
                val=self.h.word(p+off)
                if val in (0x6409810,self.arena):raw[16+off:20+off]=U(0x70000000)
            return bytes(raw)
        return (obj(self.obj),obj(self.source),bytes(self.u.mem_read(self.heap,0x60000)),tuple(self.events),tuple(self.observed_vptr),self.cursor)
    def call(self,original,symbol,args=(),this=True,ret_pointer=True):
        for r,v in zip(REGS,VALUES):self.u.reg_write(r,v)
        value=self.h.invoke(self.new[symbol] if self.rebuilt else original,args,self.obj if this else None)
        assert all(self.u.reg_read(r)==v for r,v in zip(REGS,VALUES)), 'nonvolatile registers'
        if ret_pointer:assert value==self.obj,'returned this pointer'
        return value


def assert_pair(ms):
    a,b=[m.snapshot() for m in ms]
    for index,name in enumerate(['target','source','whole seeded heap','event order','vptr order','allocator cursor']):
        if a[index]!=b[index]:
            if isinstance(a[index],bytes):
                first=next(i for i,(x,y) in enumerate(zip(a[index],b[index])) if x!=y)
                raise AssertionError((name,hex(first),a[index][max(0,first-8):first+16].hex(),b[index][max(0,first-8):first+16].hex()))
            raise AssertionError((name,a[index],b[index]))


def field_oracle(before,after,source,words,octets,preserve_nickname=False,container=True):
    want=bytearray(before)
    for off in words:want[16+off:20+off]=source[16+off:20+off]
    for off in octets:want[16+off]=source[16+off]
    if container:
        # Independent object-level ownership pointers: retained, not source aliases.
        assert after[16+0x4c:16+0x54]==before[16+0x4c:16+0x54]
        want[16+0x49]=source[16+0x49];want[16+0x58:16+0x5c]=source[16+0x58:16+0x5c]
    if preserve_nickname:want[24:28]=before[24:28]
    # Client event oracle is separate; source client installed only for assignment.
    assert after==want,'independent subtype/metadata guarded write set'


def run(dll):
    ms=[Machine(dll,x) for x in (False,True)];counts=collections.Counter()
    for seed in (17,91,451):
        for kind in range(3):
            for low,alignment in itertools.product(range(256),range(4)):
                client=0x20502500+low if low else 0
                for m in ms:
                    m.reset_case(seed+low);m.obj+=alignment
                    m.u.mem_write(m.obj-16,m.rng.randbytes(0x120))
                    m.call(DEFAULTS[kind],'archetype_'+KINDS[kind]+'_default',(client,))
                    h=m.h;p=m.obj
                    assert h.word(p+0x1c)==(0x42c80000 if kind==0 else 0x3f800000)
                    assert h.word(p+0x20)==0x3f800000 and h.word(p+0x28)==0x3f800000
                    assert bytes(m.u.mem_read(p+0x48,2))==bytes([client&255])*2
                    assert h.word(p+0x4c)!=h.word(p+0x50)
                    assert [e[1] for e in m.events if e[0]=='allocate']==[0x44,0x44]
                    assert not [e for e in m.events if e[0]=='client']
                    assert m.observed_vptr==list(range(kind+1)),'independent base-to-derived vptr order'
                assert_pair(ms);counts['constructor_pairs']+=1
                for m in ms:m.obj-=alignment
        for source_count in (0,1,3,7):
            for dest_count in (0,1,3):
                for clients in ((0,0),(1,0),(0,1),(1,1),(1,2)):
                    for entry,symbol in ASSIGN.items():
                        cls={0x62f0340:None,0x626ddb0:8,0x626e070:9,0x626eaf0:18,0x626dbb0:24,0x626e2c0:28,0x626f660:31,0x626f870:32,0x626fa10:33}[entry]
                        for m in ms:
                            m.reset_case(seed);dc=[0,m.client,m.client2][clients[0]];sc=[0,m.client,m.client2][clients[1]]
                            m.tree_fixture(m.obj,dest_count,m.heap+0x30000,dc);m.tree_fixture(m.source,source_count,m.heap+0x40000,sc)
                            before,source=m.snapshot()[:2];m.events=[]
                            m.call(entry,symbol,(m.source,))
                            if cls is None:w,b=ROOT_WORDS,[0x38,0x39]
                            else:extra,bs=CLASS_FIELDS[cls];w,b=EQ_WORDS+extra,EQ_BYTES+bs
                            after=m.snapshot()[0]
                            # Assignment installs source client, unlike inherit.
                            w=w+[4]
                            field_oracle(before,after,source,w,b)
                            events=[e for e in m.events if e[0]=='client']
                            assert [(e[1],e[2]) for e in events]==([(4,dc)] if dc else [])+([(0,sc)] if sc else []),'release before addref'
                        assert_pair(ms);counts['assignment_pairs']+=1
        for cls in list(range(8,34))+[0,7,34,0xffffffff]:
            for clients in ((0,0),(1,0),(0,1),(1,1),(1,2)):
                for self_alias in (False,True):
                    for m in ms:
                        m.reset_case(seed);dc=[0,m.client,m.client2][clients[0]];sc=[0,m.client,m.client2][clients[1]]
                        m.tree_fixture(m.obj,3,m.heap+0x30000,dc);m.tree_fixture(m.source,7,m.heap+0x40000,sc)
                        src=m.obj if self_alias else m.source
                        m.classes={m.obj:cls,src:cls}
                        for off in ([0xa8] if cls==14 else [0xbc] if cls==17 else []):
                            m.vector_fixture(m.obj+off,2,4,m.heap+0x20000);m.vector_fixture(m.source+off,5,5,m.heap+0x21000)
                        before,source=m.snapshot()[:2]
                        if self_alias:source=before;sc=dc
                        m.call(0x62f3e20,'arch_inherit_dispatch',(m.obj,src),this=False,ret_pointer=False)
                        after=m.snapshot()[0]
                        if cls in CLASS_FIELDS:
                            ew,eb=CLASS_FIELDS[cls]
                            if cls not in (14,17):field_oracle(before,after,source,EQ_WORDS+ew,EQ_BYTES+eb,True)
                        else:assert after==before
                        events=[e for e in m.events if e[0]=='client']
                        expected=[]
                        if dc:expected += [(0,dc),(28,dc)]
                        if cls in CLASS_FIELDS:
                            if dc:expected += [(4,dc)]
                            if sc:expected += [(0,sc),(4,sc)]
                        elif dc:expected += [(4,dc)]
                        assert [(e[1],e[2]) for e in events]==expected,'inherit ref event order'
                    assert_pair(ms);counts['inherit_pairs']+=1
            for m in ms:
                m.reset_case(seed);m.tree_fixture(m.obj,1,m.heap+0x30000,m.client);m.tree_fixture(m.source,3,m.heap+0x40000,m.client2)
                m.classes={m.obj:cls,m.source:(cls+1)&0xffffffff};before=m.snapshot();m.call(0x62f3e20,'arch_inherit_dispatch',(m.obj,m.source),this=False,ret_pointer=False)
                after=m.snapshot();assert after[:3]==before[:3];assert [e[0] for e in m.events]==['real-inherit','class','class']
            assert_pair(ms);counts['class_mismatch_pairs']+=1
        for src_len in (0,1,3,7):
            for dest_len,cap in ((0,0),(0,8),(2,2),(2,8),(8,8)):
                for self_alias in (False,True):
                    for m in ms:
                        m.reset_case(seed);m.vector_fixture(m.obj,dest_len,cap,m.heap+0x20000,null=cap==0);m.vector_fixture(m.source,src_len,src_len,m.heap+0x21000,null=src_len==0)
                        before=bytes(m.u.mem_read(m.obj,16));source=bytes(m.u.mem_read(m.source,16));src=m.obj if self_alias else m.source
                        m.call(0x62fb660,'archetype_pointer_vector_assign',(src,))
                        assert bytes(m.u.mem_read(m.obj,4))==before[:4]
                        if self_alias:assert bytes(m.u.mem_read(m.obj,16))==before and not m.events
                        else:
                            assert (m.h.word(m.obj+8)-m.h.word(m.obj+4))//4==src_len
                            if src_len:assert bytes(m.u.mem_read(m.h.word(m.obj+4),4*src_len))==bytes(m.u.mem_read(m.h.word(m.source+4),4*src_len))
                            assert bytes(m.u.mem_read(m.source,16))==source
                    assert_pair(ms);counts['pointer_vector_pairs']+=1
    return dict(counts)


def main():
    p=argparse.ArgumentParser();p.add_argument('--report',default='analysis/fla263/ownership-verification.json');args=p.parse_args()
    original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
    assert hashlib.sha256(original.read_bytes()).hexdigest()==HASH
    dll,commands=build();counts=run(dll)
    report={'issue':'FLA-263','original_sha256':HASH,'counts':counts,'commands':commands,'modeled_services':['allocation/free','payload external heap release','client slots','INI reader leaves','native CRT array iterator'], 'native_runs':0,'milestone_complete':False,'limits':['Copy/default/destruction lifecycle/fault/x87/full regression gates not all executed by this initial suite.','No real DB/file loader or native Windows/SEH.']}
    dest=ROOT/args.report;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'counts':counts,'report':str(dest)}))

if __name__=='__main__':main()
