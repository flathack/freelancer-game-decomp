#!/usr/bin/env python3
"""FLA-263 remaining original/rebuilt lifetime, reader, failure and x87 gates.
The existing independent oracle predates implementation. Allocation/clients/INI
and array iteration are service models; no modeled copying/destruction results.
"""
import collections
import hashlib
import itertools
import json
import pathlib
import struct
from unicorn import UcError
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESP
from verify_archetype_ownership_x86 import (
    ROOT, HASH, U, Machine as OwnershipMachine, build, assert_pair,
    DEFAULTS, COPIES, DELETING, KINDS, SIZES, LVT, OVT, ASSIGN,
    ROOT_WORDS, EQ_WORDS, EQ_BYTES, CLASS_FIELDS, field_oracle)
from verify_archetype_metadata_x86 import READERS, GETEQ, GETID, binary80
from verify_archetype_metadata_coupled_x86 import make_tree


class Machine(OwnershipMachine):
    def __init__(self, dll, rebuilt):
        self.abi_returns=collections.Counter()
        super().__init__(dll, rebuilt)
        # Original CreateID keeps a persistent CFLIDMaker in its private first
        # 4K heap region; per-case Root allocations begin strictly after it.
        self.hash_service_region=bytes(self.u.mem_read(self.heap,0x1000))

    def reset_case(self, seed=17, poison=False, cw=0x37f, older=False):
        super().reset_case(seed, poison)
        self.u.mem_write(self.heap,self.hash_service_region)
        self.failed_allocation = None
        self.null_page_unmapped = False
        self.allocation_number = 0
        self.failed_client_slot = None
        self.live_query = False
        self.allocation_records = []
        self.free_records = []
        self.array_shape = None
        self.cache_metadata_kind = None
        self.h.write_word(self.control, cw)
        self.h.invoke(self.h.stop+0x120)
        if older:
            self.h.invoke(self.h.stop+0x160)
        self.u.mem_write(self.h.stop+0x4a0, b'\xa1'+U(0x25000000)+b'\xc3')

    def hook(self, u, a, size, user):
        if not hasattr(self, 'new') or not hasattr(self, 'allocation_number'):
            return super().hook(u, a, size, user)
        h = self.h
        sp = u.reg_read(UC_X86_REG_ESP)
        if a in (0x6391abc, self.new['arch_runtime_allocate']):
            self.allocation_number += 1
            n = h.word(sp+4)
            if self.failed_allocation == self.allocation_number:
                self.events.append(('allocate-null', n))
                # Permit the original modeled FS:[0] SEH prologue, then remove
                # the null page exactly when this allocator returns NULL.
                self.u.mem_unmap(0,4096)
                self.null_page_unmapped=True
                self.ret(0)
                return
            p = self.cursor
            self.allocation_records.append((p, n))
            self.alloc_sizes[p] = n
        if a in (0x6391a7a, self.new['arch_runtime_free']):
            self.free_records.append(h.word(sp+4))
        if self.failed_client_slot is not None:
            slots = {h.stop+0x400:0, h.stop+0x420:4, h.stop+0x440:28}
            if slots.get(a) == self.failed_client_slot:
                self.events.append(('client-fault', self.failed_client_slot))
                u.reg_write(UC_X86_REG_EIP, h.stop+0x4a0)
                return
        if a == 0x63015d0 and self.live_query:
            assert not self.rebuilt, 'FORBIDDEN ORIGINAL REAL QUERY FALLBACK'
            self.events.append(('real-query', h.word(h.word(sp+8))))
            return
        if a == self.new.get('arch_inherit_node') and self.live_query:
            self.events.append(('real-query', h.word(sp+4)))
            return
        return super().hook(u, a, size, user)

    def snapshot(self):
        result=list(super().snapshot())
        # Only the unrelated published CreateID's persistent service storage is
        # outside this Root-owned heap comparison; ALL new allocations >=+1000.
        result[2]=result[2][0x1000:]
        if self.cache_metadata_kind is not None:
            for idx,pointer in ((0,self.obj),(1,self.source)):
                raw=bytearray(result[idx])
                for off in ([12,128] if self.cache_metadata_kind==2 else [12]):
                    value=self.h.word(pointer+off)
                    if self.arena<=value<self.arena+0x180000:
                        raw[16+off:20+off]=U(0x70000000+value-self.arena)
                result[idx]=bytes(raw)
        if self.array_shape:
            stride,count=self.array_shape
            raw=bytearray(result[0])
            for i in range(1,count):
                off=16+i*stride
                if off+4<=len(raw):
                    raw[off:off+4]=U(self.vkind(self.h.word(self.obj+i*stride)))
            result[0]=bytes(raw)
        return tuple(result)

    def call(self,original,symbol,args=(),this=True,ret_pointer=True):
        value=super().call(original,symbol,args,this,ret_pointer)
        # Increment only AFTER the actual normal return and ABI assertions.
        self.abi_returns[symbol]+=1
        return value

    def call_at(self, pointer, original, symbol, args=(), ret_pointer=True):
        previous = self.obj
        self.obj = pointer
        try:
            return self.call(original, symbol, args, ret_pointer=ret_pointer)
        finally:
            self.obj = previous

    def clients(self, destination, source):
        return [0, self.client, self.client2][destination], [0, self.client, self.client2][source]

    def external_payloads(self, nodes, base):
        for i, node in enumerate(nodes):
            handle = base+i*32+4
            self.h.write_word(handle-4, base+i*32+16)
            self.h.write_word(node+20, handle)

    def guarded_fault(self, entry, symbol, args):
        self.fault = None
        try:
            self.call(entry, symbol, args)
        except UcError:
            assert self.fault is not None, 'fault must have an actual invalid memory access'
        else:
            raise AssertionError('unchecked failure became a successful return')
        finally:
            if self.null_page_unmapped:
                self.u.mem_map(0,4096)
                self.null_page_unmapped=False
        return self.fault, self.snapshot()


def alignment_cases(ms, counts):
    for seed, kind, alignment in itertools.product((17,91,451), range(3), range(4)):
        for m in ms:
            m.reset_case(seed)
            m.obj += alignment
            m.call(DEFAULTS[kind], 'archetype_'+KINDS[kind]+'_default', (m.client,))
        assert_pair(ms)
        for m in ms:
            m.obj -= alignment
        counts['unaligned_constructor_pairs'] += 1


def copy_cases(ms, counts):
    for seed,kind,n,clients in itertools.product((17,91,451), range(3), (0,1,2,7), ((0,0),(1,0),(0,1),(1,1),(1,2))):
        for m in ms:
            m.reset_case(seed)
            dc,sc = m.clients(*clients)
            nodes = m.tree_fixture(m.source,n,m.heap+0x40000,sc)
            m.external_payloads(nodes,m.heap+0x45000)
            m.h.write_word(m.obj+4,dc)
            source_before = m.snapshot()[1]
            m.call(COPIES[kind], 'archetype_'+KINDS[kind]+'_copy', (m.source,))
            assert m.snapshot()[1] == source_before, 'copy changed source'
            assert m.h.word(m.obj+0x4c) != m.h.word(m.source+0x4c)
            assert m.h.word(m.obj+0x50) != m.h.word(m.source+0x50)
            assert m.h.word(m.obj+0x58)==n
            assert m.observed_vptr == list(range(kind+1)), 'base-to-derived vptr sequence'
            events=[e for e in m.events if e[0]=='client']
            assert [(e[1],e[2]) for e in events] == ([(4,dc)] if dc else [])+([(0,sc)] if sc else [])
            assert all(m.h.word(m.obj+off)==m.h.word(m.source+off) for off in ROOT_WORDS)
        assert_pair(ms)
        counts['copy_constructor_pairs'] += 1


def self_cases(ms, counts):
    for seed,entry,client in itertools.product((17,91,451), ASSIGN, (0,1)):
        for m in ms:
            m.reset_case(seed)
            cp = m.client if client else 0
            m.tree_fixture(m.obj,3,m.heap+0x30000,cp)
            before=m.snapshot()
            m.call(entry,ASSIGN[entry],(m.obj,))
            assert m.snapshot()[:3]==before[:3], 'self assignment wrote payload or allocated'
            assert [(e[1],e[2]) for e in m.events if e[0]=='client'] == ([(4,cp),(0,cp)] if cp else [])
        assert_pair(ms)
        counts['self_assignment_pairs'] += 1


def destroy_cases(ms, counts):
    for seed,kind,n,order in itertools.product((17,91,451),range(3),(0,1,2,7),(False,True)):
        for m in ms:
            m.reset_case(seed,poison=True)
            m.tree_fixture(m.source,n,m.heap+0x40000,m.client)
            m.h.write_word(m.obj+4,0)
            m.call(COPIES[kind],'archetype_'+KINDS[kind]+'_copy',(m.source,))
            allocated=[p for p,size in m.allocation_records]
            owned_source=[m.h.word(m.source+0x4c),m.h.word(m.source+0x50)]
            sources=m.tree_fixture if False else None # no additional construction
            before_source=bytes(m.u.mem_read(m.source, SIZES[kind]))
            pointers=(m.source,m.obj) if order else (m.obj,m.source)
            for pointer in pointers:
                m.call_at(pointer,0x62f0230,'archetype_root_destroy',ret_pointer=False)
                assert m.h.word(pointer+0x4c)==0 and m.h.word(pointer+0x50)==0 and m.h.word(pointer+0x58)==0
            assert len(m.free_records)==len(set(m.free_records)), 'owned allocation freed twice'
            assert all(m.free_records.count(p)==1 for p in allocated+owned_source)
            assert m.h.word(m.source+4)==struct.unpack_from('<I',before_source,4)[0]
        assert_pair(ms)
        counts['copy_destroy_order_pairs'] += 1
    for seed,kind,flags,count in itertools.product((17,91,451),range(3),(0,1,2,3,0x100,0x103),(0,1,3)):
        for m in ms:
            m.reset_case(seed,poison=True)
            m.h.write_word(m.obj-4,count)
            array=bool(flags&2)
            objects=count if array else 1
            m.array_shape=(SIZES[kind],objects)
            for i in range(objects):
                pointer=m.obj+i*SIZES[kind]
                m.tree_fixture(pointer,1,m.heap+0x30000+i*0x2000,m.client)
            returned=m.call(DELETING[kind],'archetype_'+KINDS[kind]+'_deleting',(flags,),ret_pointer=False)
            assert returned==m.obj-4 if array else returned==m.obj
            assert [e[1:4] for e in m.events if e[0]=='array-service'] == ([(m.obj,SIZES[kind],count)] if array else [])
            assert m.free_records.count(returned)==int(bool(flags&1))
            for i in range(objects):
                pointer=m.obj+i*SIZES[kind]
                assert m.h.word(pointer+0x4c)==0 and m.h.word(pointer+0x50)==0
        assert_pair(ms)
        counts['deleting_ret4_pairs'] += 1


def reader_cases(ms,counts):
    for seed,kind,state,subtype in itertools.product((17,91,451),(1,2),('missing','null','valid'),(False,True)):
        for m in ms:
            m.reset_case(seed)
            m.call(DEFAULTS[kind],'archetype_'+KINDS[kind]+'_default',(0,))
            m.tree_fixture(m.source,3,m.heap+0x40000,0)
            m.h.write_word(m.source,OVT[kind] if not m.rebuilt else m.new[LVT[kind]])
            m.h.write_word(m.obj+8,0x10203040)
            if subtype:
                m.h.write_word(m.obj,m.customvt);m.h.write_word(m.source,m.customvt)
                m.classes={m.obj:kind+7,m.source:kind+7}
            key=m.h.invoke(m.hash_entry,(m.text_ptr('li01'),))
            make_tree(m,key,0 if state=='null' else m.source)
            if state=='missing':
                m.h.write_word(m.treenode+12,(key+1)&0xffffffff)
            original_tree = 0x63fbad4
            if not m.rebuilt:
                m.u.mem_write(original_tree,bytes(m.u.mem_read(m.tree,20)))
            m.live_query=True
            m.spec={'key':'inherit','text':'li01'}
            m.events=[]
            returned=m.call((0x62f41e0 if kind==1 else 0x62f5330),READERS[kind],(m.reader,),ret_pointer=False)&255
            assert returned==1
            assert [e[1] for e in m.events if e[0]=='diagnostic'] == ([1,2] if state=='missing' else [2] if state=='null' else [])
            assert sum(e[0]=='real-inherit' for e in m.events)==int(state=='valid')
            assert sum(e[0]=='real-query' for e in m.events)==1
            assert m.h.word(m.obj+8)==0x10203040
            if state=='valid' and subtype:
                assert m.h.word(m.obj+0x64)==m.h.word(m.source+0x64), (m.rebuilt,kind,state,m.events)
                assert m.h.word(m.obj+0x58)==3
            elif state=='valid':
                assert m.h.word(m.obj+0x64)==1 and m.h.word(m.obj+0x58)==0
        assert_pair(ms)
        counts['real_reader_query_inherit_pairs']+=1


def x87_cases(ms,counts):
    for cw,entry in itertools.product([0x7f|pc|rc for pc in (0,0x200,0x300) for rc in (0,0x400,0x800,0xc00)],ASSIGN):
        for m in ms:
            m.reset_case(451,cw=cw,older=True)
            m.tree_fixture(m.obj,2,m.heap+0x30000,0)
            m.tree_fixture(m.source,3,m.heap+0x40000,0)
            patterns=[0x80000000,0x7fc12345,0x7f812345,0xff800000]
            for off,val in zip((0x1c,0x20,0x28,0x5c),patterns):m.h.write_word(m.source+off,val)
            before=m.fpu()
            # FNSAVE in the published snapshot helper resets the FPU; restore
            # the actual captured environment before executing the copy body.
            m.u.mem_write(m.h.stop+0x4c0,b'\xdd\x25'+U(m.state)+b'\xc3')
            m.h.invoke(m.h.stop+0x4c0)
            m.call(entry,ASSIGN[entry],(m.source,))
            assert m.fpu()==before,'integer copy changed live binary80/CW/SW/tag'
            assert all(m.h.word(m.obj+off)==val for off,val in zip((0x1c,0x20,0x28),patterns))
        assert_pair(ms)
        counts['live_x87_raw_copy_pairs']+=1


def failure_cases(ms,counts):
    details=[]
    for kind,nth in itertools.product(range(3),(1,2)):
        results=[]
        for m in ms:
            m.reset_case(91)
            m.failed_allocation=nth
            results.append(m.guarded_fault(DEFAULTS[kind],'archetype_'+KINDS[kind]+'_default',(0,)))
        assert results[0][0]==results[1][0],('allocator fault location',kind,nth,results[0][0],results[1][0])
        assert_pair(ms)
        details.append({'kind':KINDS[kind],'null_allocation':nth,'fault':results[0][0]})
        counts['allocator_fault_pairs']+=1
    for slot,entry in itertools.product((0,4), (0x62f0340,0x626ddb0,0x626e070)):
        results=[]
        for m in ms:
            m.reset_case(17)
            m.tree_fixture(m.obj,3,m.heap+0x30000,m.client)
            m.tree_fixture(m.source,3,m.heap+0x40000,m.client2)
            m.failed_client_slot=slot
            results.append(m.guarded_fault(entry,ASSIGN[entry],(m.source,)))
        assert results[0][0]==results[1][0]
        assert_pair(ms)
        counts['client_fault_pairs']+=1
    return details


def populate_constructed_root(m):
    """Seed a valid three-node INPUT tree without replacing constructed heads.
    Allocations are real modeled allocator calls, never copied-result fixtures;
    factory/insert semantics are deliberately not claimed by this input builder.
    """
    h=m.h; head=h.word(m.obj+0x4c); nil=h.word(m.obj+0x50)
    allocate=m.new['arch_runtime_allocate'] if m.rebuilt else 0x6391abc
    nodes=[h.invoke(allocate,(0x44,)) for _ in range(3)]
    for i,p in enumerate(nodes):
        for off,value in ((0,nodes[0] if i==1 else nil),(4,head if i==1 else nodes[1]),
                          (8,nodes[2] if i==1 else nil),(12,123+i),(20,0)):
            h.write_word(p+off,value)
        m.u.mem_write(p+0x40,b'\1\0')
        buf=h.invoke(allocate,(8,))
        for off,value in ((0x34,buf),(0x38,buf+8),(0x3c,buf+8)):
            h.write_word(p+off,value)
        h.write_word(buf,0x12340000+i);h.write_word(buf+4,0x80000000+i)
    for off,value in ((0,nodes[0]),(4,nodes[1]),(8,nodes[2])):h.write_word(head+off,value)
    h.write_word(m.obj+0x58,3)
    assert h.word(m.obj+0x4c)==head and h.word(m.obj+0x50)==nil


def lifecycle_cases(ms,counts):
    for seed,kind,cycle in itertools.product((17,91,451),(1,2),range(12)):
        for m in ms:
            m.reset_case(seed+cycle,poison=True,older=True)
            m.cache_metadata_kind=kind
            m.call(DEFAULTS[kind],'archetype_'+KINDS[kind]+'_default',(0,))
            for spec in ({'key':'nickname','text':'li01'},{'key':'ids_name','integer':0x80000000},
                         {'key':'ids_info','integer':0xffffffff},{'key':'DA_archetype','text':'MixedMesh'}):
                m.spec=spec
                m.call((0x62f41e0 if kind==1 else 0x62f5330),READERS[kind],(m.reader,),ret_pointer=False)
            populate_constructed_root(m)
            m.h.write_word(m.source+4,0)
            m.call_at(m.source,COPIES[kind],'archetype_'+KINDS[kind]+'_copy',(m.obj,))
            assert m.h.word(m.source+0x58)==3
            metadata_key=m.h.word(m.obj+8)
            make_tree(m,metadata_key,m.obj)
            assert m.h.invoke(m.new[GETEQ] if m.rebuilt else 0x62f9370,(metadata_key,))==m.obj
            # Existing reconstructed GoodInfo constructor supplies the real
            # production CommReferrable table through its vtable dependency.
            # No manually installed callback table or synthetic sentinel list.
            h=m.h;u=m.u
            u.mem_write(m.good-16,m.rng.randbytes(0xe0))
            u.mem_write(h.stack+0x8000-17,b'\x5b')
            m.call_at(m.good,0x62701e0,'??0GoodInfo@@QAE@XZ')
            assert h.word(m.good)==(m.new['good_info_comm_slots'] if m.rebuilt else 0x63993e8)
            if m.rebuilt:
                assert m.new['good_info_comm_base_slots']!=m.new['good_info_comm_slots']
            m.block=True;m.position=-1
            m.operations=[('category',['Equipment']),('equipment',['li01']),('not-a-key',['x']),('MsG_Id_PrEfIx',['X'*64]),('msg_id_prefix',['last'])]
            m.call_at(m.listing,0x62708c0,'good_info_read_block',(m.reader,m.good),ret_pointer=False)
            assert h.word(m.good+4)==4 and bytes(u.mem_read(m.good+8,5))==b'last\0'
            assert h.word(m.good+0x88)==0x80000000 and h.word(m.good+0x8c)==0xffffffff
            assert h.word(m.good+0x50)==metadata_key
            m.block=False
            for pointer in ((m.obj,m.source) if cycle%2 else (m.source,m.obj)):
                m.call_at(pointer,0x62f0230,'archetype_root_destroy',ret_pointer=False)
            m.call_at(m.good,0x6270330,'??1GoodInfo@@QAE@XZ',ret_pointer=False)
            assert len(m.free_records)==len(set(m.free_records))
            assert all(m.free_records.count(p)==1 for p,n in m.allocation_records),'lifecycle owned allocation leak'
        assert_pair(ms)
        # Normalize only real image-relative cache pointers and GoodInfo vptr.
        a,b=[bytearray(m.u.mem_read(m.good-16,0xe0)) for m in ms]
        a[16:20]=b[16:20]=U(0)
        for m,raw in zip(ms,(a,b)):
            for off in (0x74,0x78,0x7c,0x80,0x84):
                value=m.h.word(m.good+off)
                if m.arena<=value<m.arena+0x180000:
                    raw[16+off:20+off]=U(0x70000000+value-m.arena)
        assert a==b,'P1 callback/metadata lifecycle guarded object'
        counts['read_copy_lookup_P1_callback_destroy_cycles']+=1


def main():
    dll,commands=build(label='lifecycle')
    ms=[Machine(dll,False),Machine(dll,True)]
    counts=collections.Counter()
    for action in (alignment_cases,copy_cases,self_cases,destroy_cases,reader_cases,x87_cases,lifecycle_cases):
        action(ms,counts)
        print(action.__name__,dict(counts),flush=True)
    failures=failure_cases(ms,counts)
    denied=[]
    for start,end in ms[1].owned:
        try:
            ms[1].h.invoke(start,(),ms[1].obj)
        except AssertionError as exc:
            assert 'FORBIDDEN ORIGINAL' in str(exc)
            denied.append(hex(start))
        else:
            raise AssertionError('forbidden span guard did not fire: '+hex(start))
    report={'issue':'FLA-263','original_sha256':HASH,'counts':dict(counts),
            'fault_details':failures,'faults_counted_as_returns':0,
            'actual_entry_abi_returns_by_side':{'original':dict(ms[0].abi_returns),'rebuilt':dict(ms[1].abi_returns)},
            'destructor_return_convention':'Void Root/GoodInfo RET checked; deleting RET4 EAX equals scalar or cookie pointer. Nested CRT-iterator destructor calls are not entry-return counts.',
            'denial_spans_actually_probed':denied,'commands':commands,
            'modeled_services':['allocation/free with poisoning','external client references/faults',
                                'INI current-line getters','ASCII CRT','native CRT array iterator'],
            'native_runs':0,'milestone_complete':False,
            'limits':['Native SEH/exception unwind and unmasked x87 are excluded (W01).',
                      'No production DB/Factories/Goods file loader or arbitrary corruption safety.'],
            'source_sha256':hashlib.sha256((ROOT/'src/archetype_ownership.cpp').read_bytes()).hexdigest()}
    target=ROOT/'analysis/fla263/lifecycle-verification.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'report':str(target),'counts':dict(counts)}))

if __name__=='__main__':main()
