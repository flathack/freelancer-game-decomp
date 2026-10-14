#!/usr/bin/env python3
"""Additional FLA-263 N03/N05/N07/N08/N11/N14 acceptance discriminators.
Expectations come from the unchanged FLA-255 spans and frozen ownership notes.
The original query's output-parameter ABI and rebuilt pointer-return API differ
intentionally; each is checked independently. No modeled copy/query body.
"""
import collections
import hashlib
import itertools
import json
from verify_archetype_lifecycle_x86 import Machine, build
from unicorn.x86_const import (UC_X86_REG_GDTR, UC_X86_REG_FS, UC_X86_REG_CS,
                               UC_X86_REG_DS, UC_X86_REG_ES, UC_X86_REG_SS)
import struct
from verify_archetype_ownership_x86 import (
    ROOT, HASH, U, REGS, VALUES, ASSIGN, COPIES, KINDS, CLASS_FIELDS,
    EQ_WORDS, EQ_BYTES, assert_pair, field_oracle)


def subtype_vectors(ms, counts):
    for seed,cls,n,(old,cap),alias in itertools.product(
            (17,91,451),(14,17),(0,1,2,7),((0,0),(0,8),(2,2),(2,8),(8,8)),(False,True)):
        off=0xa8 if cls==14 else 0xbc
        for m in ms:
            m.reset_case(seed,poison=True)
            m.tree_fixture(m.obj,2,m.heap+0x30000,m.client)
            m.tree_fixture(m.source,7,m.heap+0x40000,m.client2)
            m.classes={m.obj:cls,m.source:cls}
            m.vector_fixture(m.obj+off,old,cap,m.heap+0x20000,null=cap==0)
            m.vector_fixture(m.source+off,n,n,m.heap+0x21000,null=n==0)
            src=m.obj if alias else m.source
            before,source=m.snapshot()[:2]
            source_heap=bytes(m.u.mem_read(m.heap+0x40000,0x6000))
            expected_elements=bytes(m.u.mem_read(m.h.word(src+off+4),4*(old if alias else n))) if (old if alias else n) else b''
            old_begin=m.h.word(m.obj+off+4)
            m.call(0x62f3e20,'arch_inherit_dispatch',(m.obj,src),this=False,ret_pointer=False)
            after=m.snapshot()[0]
            # Only vector pointer metadata is handled by the separate ownership
            # oracle. Every other subtype field and guard has an exact write set.
            normalized=bytearray(after)
            normalized[16+off+4:16+off+16]=before[16+off+4:16+off+16]
            ew,eb=CLASS_FIELDS[cls]
            field_oracle(before,bytes(normalized),before if alias else source,EQ_WORDS+ew,EQ_BYTES+eb,True)
            begin=m.h.word(m.obj+off+4)
            length=old if alias else n
            assert m.h.word(m.obj+off+8)==begin+length*4,'vector end'
            assert bytes(m.u.mem_read(begin,length*4))==expected_elements if length else True
            if alias:
                assert after==before,'self subtype assignment must preserve all object bytes'
            else:
                assert m.snapshot()[1]==source,'source object unchanged'
                assert bytes(m.u.mem_read(m.heap+0x40000,0x6000))==source_heap,'source owned nodes unchanged'
                if n>cap:
                    assert begin not in (old_begin,m.h.word(m.source+off+4)),'independent new vector allocation'
                    assert m.free_records.count(old_begin)==1,'old vector freed exactly once'
                else:
                    assert begin==old_begin,'capacity-reuse path'
        assert_pair(ms)
        counts['subtype_vector_populated_root_pairs']+=1


def unsigned_query(ms,counts):
    keys=(0,0x80000000,0xffffffff)
    for seed,key in itertools.product((17,91,451),(0,1,0x7fffffff,0x80000000,0x80000001,0xfffffffe,0xffffffff)):
        results=[]
        for m in ms:
            m.reset_case(seed)
            h=m.h; head=m.treehead; nil=m.nil; nodes=[m.treenode+i*0x40 for i in range(3)]
            root=nodes[1]
            for off,val in ((4,head),(8,nil)):
                h.write_word(m.tree+off,val)
            h.write_word(head+4,root)
            m.u.mem_write(nil+0x15,b'\1')
            for i,p in enumerate(nodes):
                for off,val in ((0,nodes[0] if i==1 else nil),(4,head if i==1 else root),(8,nodes[2] if i==1 else nil),(12,keys[i]),(16,m.source+i*4)):
                    h.write_word(p+off,val)
                m.u.mem_write(p+0x15,b'\0')
            actual_tree=m.new['EquipmentArchetypeTree'] if m.rebuilt else 0x63fbad4
            m.u.mem_write(actual_tree,bytes(m.u.mem_read(m.tree,20)))
            before=bytes(m.u.mem_read(m.tree,0x500))
            m.live_query=True
            for r,v in zip(REGS,VALUES):m.u.reg_write(r,v)
            if m.rebuilt:
                got=h.invoke(m.new['arch_inherit_node'],(key,))
            else:
                out=m.h.scratch+0x7400; arg=out+4
                h.write_word(out,0xdeadbeef);h.write_word(arg,key)
                returned=h.invoke(0x63015d0,(out,arg),actual_tree)
                assert returned==out,'original RET8 returns output parameter'
                assert h.word(arg)==key,'query input key unchanged'
                got=h.word(out)
            assert all(m.u.reg_read(r)==v for r,v in zip(REGS,VALUES)),'query nonvolatile ABI'
            expected=nodes[keys.index(key)] if key in keys else head
            assert got==expected,'unsigned exact-match lower bound'
            assert bytes(m.u.mem_read(m.tree,0x500))==before,'query changed tree'
            results.append(got)
        assert results[0]==results[1]
        counts['unsigned_real_query_boundary_pairs']+=1


def failure_edges(ms,counts):
    records=[]
    # Null allocations: constructor-owned sentinel/head, clone nodes and their
    # owned pointer-vector allocations are all genuine original dependencies.
    for kind,nth in itertools.product(range(3),range(1,9)):
        results=[]
        for m in ms:
            m.reset_case(91)
            m.tree_fixture(m.source,3,m.heap+0x40000,m.client2)
            m.h.write_word(m.obj+4,m.client)
            m.failed_allocation=nth
            if nth in (4,6):
                # Frozen payload-copy contract: length 1 skips its NULL first
                # element; length 0 performs no write. These original paths
                # really return, leaving raw NULL/advanced pointer metadata.
                try:
                    m.call(COPIES[kind],'archetype_'+KINDS[kind]+'_copy',(m.source,))
                    assert m.fault is None
                    results.append((None,m.snapshot()))
                finally:
                    if m.null_page_unmapped:
                        m.u.mem_map(0,4096);m.null_page_unmapped=False
            else:
                results.append(m.guarded_fault(COPIES[kind],'archetype_'+KINDS[kind]+'_copy',(m.source,)))
        assert results[0][0]==results[1][0],('copy allocation fault',kind,nth,results[0][0],results[1][0])
        assert_pair(ms)
        records.append({'kind':KINDS[kind],'copy_null_allocation':nth,'fault':results[0][0],
                        'actual_return':nth in (4,6)})
        counts['copy_null_allocation_return_pairs' if nth in (4,6) else 'copy_allocator_fault_pairs']+=1
    for seed,slot,mode in itertools.product((17,91,451),(0,4,28),('inherit','destroy')):
        if mode=='destroy' and slot!=4:continue
        results=[]
        for m in ms:
            m.reset_case(seed)
            m.tree_fixture(m.obj,3,m.heap+0x30000,m.client)
            m.tree_fixture(m.source,7,m.heap+0x40000,m.client2)
            m.classes={m.obj:8,m.source:8}
            m.failed_client_slot=slot
            if mode=='inherit':
                # Explicit cdecl fault run: fault is not a normal ABI return.
                m.fault=None
                from unicorn import UcError
                try:m.call(0x62f3e20,'arch_inherit_dispatch',(m.obj,m.source),this=False,ret_pointer=False)
                except UcError:assert m.fault is not None
                else:raise AssertionError('external client failure returned success')
                results.append(m.fault)
            else:
                results.append(m.guarded_fault(0x62f0230,'archetype_root_destroy',())[0])
        assert results[0]==results[1]
        assert_pair(ms)
        records.append({'seed':seed,'client_slot':slot,'operation':mode,'fault':results[0]})
        counts['inherit_destroy_client_fault_pairs']+=1
    return records


def main():
    dll,commands=build(label='edges')
    ms=[Machine(dll,False),Machine(dll,True)]
    # A separate modeled Windows TEB/FS page keeps actual NULL accesses distinct
    # from the original FS:[0] SEH registration/restore. No throw/unwind model.
    for m in ms:
        gdt=0x24000000; base=0x24600000; limit=0xfffff
        m.u.mem_map(gdt,4096); m.u.mem_map(base,4096)
        for selector,segment,access in ((8,0,0x9b),(16,0,0x93),(24,base,0x93)):
            descriptor=((limit&0xffff)|((segment&0xffff)<<16)|(((segment>>16)&255)<<32)
                        |(access<<40)|(((limit>>16)&15)<<48)|(0xc<<52)|(((segment>>24)&255)<<56))
            m.u.mem_write(gdt+selector,struct.pack('<Q',descriptor))
        m.u.reg_write(UC_X86_REG_GDTR,(0,gdt,4095,0))
        m.u.reg_write(UC_X86_REG_CS,8)
        for reg in (UC_X86_REG_DS,UC_X86_REG_ES,UC_X86_REG_SS):m.u.reg_write(reg,16)
        m.u.reg_write(UC_X86_REG_FS,24)
    counts=collections.Counter()
    for action in (subtype_vectors,unsigned_query):
        action(ms,counts); print(action.__name__,dict(counts),flush=True)
    faults=failure_edges(ms,counts)
    report={'issue':'FLA-263','original_sha256':HASH,'counts':dict(counts),
            'fault_details':faults,'faults_counted_as_returns':0,'commands':commands,
            'source_sha256':hashlib.sha256((ROOT/'src/archetype_ownership.cpp').read_bytes()).hexdigest(),
            'native_runs':0,'limits':['External allocator/client faults are modeled service failures, not native SEH throws.',
                                    'Synthetic unsigned lookup tree is not a real file-loaded DB.']}
    path=ROOT/'analysis/fla263/ownership-edges.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'report':str(path),'counts':dict(counts)}))

if __name__=='__main__':main()
