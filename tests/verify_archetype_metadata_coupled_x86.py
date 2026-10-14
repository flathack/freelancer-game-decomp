#!/usr/bin/env python3
"""Additional P2 sequential ownership/ABI and metadata -> lookup -> P1 tests.
No prefilled metadata; no CRC32. Both sides retain arena objects through teardown.
"""
import collections,hashlib,itertools,json,pathlib,random,struct
from unicorn import UcError
from unicorn.x86_const import UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP
from verify_archetype_metadata_x86 import ROOT,HASH,BASE,FILES,VT,OVT,SIZES,READERS,TARGETS,GETEQ,GETID,SCN,U,Machine,build,digest,oracle

def normalize(m,raw,kind,cache_offsets=()):
    out=bytearray(raw);out[16:20]=U(kind)
    for off in cache_offsets:
        p=struct.unpack_from('<I',out,16+off)[0]
        if m.arena<=p<m.arena+0x180000:out[16+off:20+off]=U(0x70000000+p-m.arena)
    return bytes(out)
def make_tree(m,key,payload):
    h=m.h;u=m.u;head=m.treehead;nil=m.nil;node=m.treenode
    u.mem_write(m.tree,b'\0'*0x400)
    for off,val in ((4,head),(8,nil),(16,1)):h.write_word(m.tree+off,val)
    for off,val in ((0,node),(4,node),(8,node)):h.write_word(head+off,val)
    for off,val in ((0,nil),(4,head),(8,nil),(12,key),(16,payload)):h.write_word(node+off,val)
    target=m.new['EquipmentArchetypeTree'] if m.rebuilt else 0x63fbad4
    u.mem_write(target,bytes(u.mem_read(m.tree,20)))
    return bytes(u.mem_read(m.tree,0x400))

def main():
    dll,commands=build(ROOT/'src/archetype_metadata.cpp','archetype_metadata_coupled');machines=[Machine(dll,False),Machine(dll,True)];rng=random.Random(246771)
    types=dict((t,v) for t,v in json.loads((ROOT/'analysis/archetype-metadata-x86-behavior.json').read_text())['object_type_table'])
    vectors=json.loads((ROOT/'analysis/createid-behavior.json').read_text())['vectors'];ids={(bytes.fromhex(v['input_hex']).decode('ascii') if v['input_hex'] is not None else None):int(v['result'],16) for v in vectors}
    sequences=sequence_calls=0
    # Repeat overwrite/private allocation vs case-insensitive intern alias;
    # then arbitrary mixed-line order with live clients and seeded guards.
    for index in range(30):
        kind=2;seed=bytearray(rng.randbytes(SIZES[kind]+32));cache_offsets={12,128}
        specs=[dict(key='DA_archetype',text='FirstMixed'),dict(key='attachment_archetype',text='LastMixed'),dict(key='DA_archetype',text='LastMixed'),dict(key='HP_child',text='HpChild'),dict(key='HP_child',text='hpchild',expected_cached_text='HpChild'),dict(key='HP_child',text=''),dict(key='ids_name',integer=0x80000000),dict(key='ids_name',integer=0xffffffff)]
        choices=[dict(key='ids_info',integer=0),dict(key='nickname',text='LI01'),dict(key='lootable',integer=0xff),dict(key='use_count',integer=0x80),dict(key='mission_property'),dict(key='unknown-client',client=True,callback=0x80),dict(key='rotation_inertia'),dict(key='volume'),dict(key='toughness',integer=-2147483648)]
        specs += [rng.choice(choices) for _ in range(12)]
        outputs=[]
        for m in machines:
            m.reset(0x37f,index%2);current=bytes(seed);snapshots=[];private_handles=[];intern_handles=[]
            for i,spec in enumerate(specs):
                r=m.invoke_reader(kind,spec,current,virtual=i%2==0,reset=False);oracle(r,kind,spec,0x37f,ids,types)
                current=r['raw'];snapshots.append((normalize(m,current,kind,cache_offsets),r['al'],r['trace'],r['fpu'],r['counters']))
                if i<3:private_handles.append(m.h.word(m.obj+12))
                if i in (3,4):intern_handles.append(m.h.word(m.obj+128))
            assert len(set(private_handles))==3,'private copies were incorrectly interned';assert intern_handles[0]==intern_handles[1],'case-insensitive HP interning lost'
            assert m.text(private_handles[0])=='FirstMixed' and m.text(private_handles[1])=='LastMixed','old handles released/overwritten'
            assert m.h.word(m.obj+0x14)==0xffffffff,'last-write-wins lost';assert not any(e[0]=='free' for snap in snapshots for e in snap[2])
            outputs.append(snapshots)
        assert outputs[0]==outputs[1];sequences+=1;sequence_calls+=len(specs)
    coupled=[];abi=destructors=0;lookup_boundaries=[]
    for key,payload_null,missing in itertools.product((0,0x80000000,0xffffffff),(False,True),(False,True)):
        observations=[]
        for m in machines:
            m.reset();h=m.h;u=m.u;make_tree(m,key,0 if payload_null else m.obj);snapshot=bytes(u.mem_read(m.tree,0x400));m.events.clear()
            query=(key+1)&0xffffffff if missing else key
            got=h.invoke(m.new[GETEQ] if m.rebuilt else 0x62f9370,(query,));assert got==(0 if missing or payload_null else m.obj)
            assert sum(e[0]=='diagnostic' for e in m.events)==int(missing);assert bytes(u.mem_read(m.tree,0x400))==snapshot
            observations.append((got,tuple(m.events)))
        assert observations[0]==observations[1];lookup_boundaries.append({'key':hex(key),'null_payload':payload_null,'missing':missing})
    for kind,category,explicit_name,explicit_info,own_strings,empty_meta in itertools.product((1,2),(0,1,2,3),(False,True),(False,True),(False,True),(False,True)):
        results=[];shared_seed=rng.randbytes(SIZES[kind]+32);shared_goodseed=rng.randbytes(0xc0+32)
        for m in machines:
            m.reset();h=m.h;u=m.u;seed=bytearray(shared_seed)
            # Exact prohibited prepopulation fields begin at zero; reader must produce them.
            for off in (8,12,0x14,0x18):seed[16+off:20+off]=U(0)
            if kind==2:seed[16+128:20+128]=U(0)
            metadata=[dict(key='nickname',text='li01'),dict(key='ids_name',integer=0x80000000),dict(key='ids_info',integer=0xffffffff),dict(key='DA_archetype',text='' if empty_meta else 'MixedMesh')]
            if kind==2:metadata.append(dict(key='HP_child',text='' if empty_meta else 'HpMixed'))
            assert all(struct.unpack_from('<I',seed,16+off)[0]==0 for off in (0x14,0x18,12))
            for spec in metadata:
                r=m.invoke_reader(kind,spec,bytes(seed),virtual=True,reset=False);oracle(r,kind,spec,0x37f,ids,types);seed=bytearray(r['raw'])
            key=h.word(m.obj+8);assert key==ids['li01'];tree_before=make_tree(m,key,m.obj)
            # Accessor aliases are actual recovered dword accessor; lookup executes its body.
            keyptr=m.tree+0x80;h.write_word(keyptr,key)
            assert h.invoke(m.new[GETID] if m.rebuilt else 0x62f11d0,(keyptr,))==key
            assert h.invoke(m.new[GETEQ] if m.rebuilt else 0x62f9370,(key,))==m.obj
            assert bytes(u.mem_read(m.tree,0x400))==tree_before[:0x80]+U(key)+tree_before[0x84:]
            # Prepare only GoodInfo storage and synthetic empty list heads.
            goodseed=bytearray(shared_goodseed);goodstart=m.good-16
            words={0:h.stop+0x2000,4:0,0x48:0,0x4c:category,0x50:0xdeadbeef,0x54:0,0x58:0,0x5c:0,0x60:0,0x64:0,0x68:0,0x6c:50,0x88:42 if explicit_name else 0,0x8c:43 if explicit_info else 0,0x90:0,0xb8:0,0xbc:0}
            for off in (0x74,0x78,0x7c,0x80,0x84):words[off]=m.text_ptr('OwnString' if own_strings and off in (0x74,0x80,0x84) else '')
            heads=[m.heap+0x8000+i*48 for i in range(3)]
            for off,head in zip((0x98,0xa4,0xb0),heads):words[off]=head;words[off+4]=0;h.write_word(head,head);h.write_word(head+4,head)
            for off,val in words.items():goodseed[16+off:20+off]=U(val)
            goodseed[16+0x70]=0;u.mem_write(goodstart,bytes(goodseed));m.block=True;m.operations=[('equipment',['li01'])];m.position=-1;m.events.clear();m.fault=None
            # Null page unmaps for actual P1 execution. No hidden safe-null mapping.
            u.mem_unmap(0,4096)
            regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP];vals=[0x11223344,0x55667788,0x99aabbcc,0x12345678]
            for reg,val in zip(regs,vals):u.reg_write(reg,val)
            entry=m.new['good_info_read_block'] if m.rebuilt else 0x62708c0
            h.invoke(entry,(m.reader,m.good),m.listing);assert all(u.reg_read(reg)==val for reg,val in zip(regs,vals));abi+=1
            after=bytes(u.mem_read(goodstart,len(goodseed)));trace=tuple(m.events);want=bytearray(goodseed)
            def put(off,val):want[16+off:20+off]=U(val)
            put(0x50,key if category in (0,1) else 0)
            if category in (0,1):
                if not explicit_name:put(0x88,0x80000000)
                if not explicit_info:put(0x8c,0xffffffff)
                if kind==2 and not own_strings and not empty_meta:
                    put(0x84,h.word(m.obj+12));put(0x80,h.word(m.obj+128));put(0x74,h.word(m.obj+12))
            assert after==bytes(want),'independent P1 finalization/guard expectation'
            # normalize exact known GoodInfo pointer slots, not random dwords.
            norm=bytearray(after)
            for off in (0x74,0x78,0x7c,0x80,0x84):
                ptr=h.word(m.good+off)
                if m.arena<=ptr<m.arena+0x180000:norm[16+off:20+off]=U(0x70000000+ptr-m.arena)
            if category in (0,1) and kind==2 and not own_strings and not empty_meta:
                assert h.word(m.good+0x84)==h.word(m.obj+12) and h.word(m.good+0x80)==h.word(m.obj+128),'P1 alias not preserved'
            meta_strings=[(off,h.word(m.obj+off),m.text(h.word(m.obj+off))) for off in ([12,128] if kind==2 else [12])]
            u.mem_map(0,4096);m.events.clear();h.invoke(m.new['??1GoodInfo@@QAE@XZ'] if m.rebuilt else m.orig['??1GoodInfo@@QAE@XZ'],(),m.good);destructors+=1
            assert [e[1] for e in m.events if e[0]=='free']==list(reversed(heads));assert all(m.text(ptr)==text for off,ptr,text in meta_strings),'arena metadata expired before teardown'
            assert bytes(u.mem_read(m.tree,0x400))==tree_before[:0x80]+U(key)+tree_before[0x84:]
            results.append((bytes(norm),trace,m.fpu()))
        assert results[0]==results[1],('coupled comparison',kind,category,explicit_name,explicit_info,own_strings,empty_meta)
        coupled.append({'kind':kind,'category':category,'own_name':explicit_name,'own_info':explicit_info,'own_strings':own_strings,'empty_metadata_strings':empty_meta})
    # Additional missing-reference fault matrix. Faults are NOT successful ABI returns.
    faults=[]
    for name,info,hull in [(n,i,False) for n,i in itertools.product((0,42),(0,43))]+[(0,0,True)]:
        observed=[]
        for m in machines:
            m.reset();h=m.h;u=m.u;make_tree(m,0x80000000,m.obj);u.mem_write(m.good,b'\0'*0xc0);h.write_word(m.good+0x4c,1);h.write_word(m.good+0x88,name);h.write_word(m.good+0x8c,info)
            for off in (0x74,0x78,0x7c,0x80,0x84):h.write_word(m.good+off,m.text_ptr(''))
            m.block=True;m.position=-1;m.operations=[('hull',['li01'])] if hull else [];m.events.clear();m.fault=None;u.mem_unmap(0,4096)
            try:h.invoke(m.new['good_info_read_block'] if m.rebuilt else 0x62708c0,(m.reader,m.good),m.listing)
            except UcError:assert m.fault is not None
            else:raise AssertionError('missing reference was incorrectly safe')
            finally:u.mem_map(0,4096)
            expected=0x48 if hull else 0x14 if not name else 0x18 if not info else 0
            assert m.fault[1]==expected;observed.append((m.fault,tuple(m.events)))
        assert observed[0]==observed[1];faults.append({'name':name,'info':info,'hull_missing':hull,'low_address':hex(expected)})
    # Exercise the fallback guard against all five original P2 entries.
    denied=[];m=machines[1]
    for address,end in TARGETS:
        try:m.h.invoke(address,(m.reader,) if address in [a for a,b in TARGETS[:3]] else (),m.obj)
        except AssertionError as e:assert 'FORBIDDEN ORIGINAL P2 FALLBACK' in str(e);denied.append(hex(address))
        else:raise AssertionError('fallback guard did not abort')
    report={'status':'passed','base_commit':BASE,'original_sha256':HASH,'mixed_sequences':sequences,'lookup_boundary_pairs':len(lookup_boundaries),'lookup_boundary_cases':lookup_boundaries,'matched_fault_pairs':len(faults),'matched_fault_cases':faults,'sequence_reader_pairs':sequence_calls,'coupled_pairs':len(coupled),'coupled_abi_calls':abi,'coupled_destructor_calls':destructors,'fallback_entries_actually_denied':denied,'coupled_cases':coupled,'source_hashes':{f:digest(ROOT/f) for f in FILES+['tests/verify_archetype_metadata_coupled_x86.py']},'dll_sha256':digest(dll),'commands':commands,'real_loader_or_database_cases':0,'controls':['synthetic prepared storage/tree','INI current line/traversal','successful allocator','ASCII CRT','inherit dispatcher/client bodies'],'implemented_services_exercised':['CreateID','StringCache clear/alloc/intern tree','ID accessor','unsigned Equipment lookup','new readers','new is_attached slots','unchanged P1 reader and destructor'],'limitations':['no native Windows/CRT','no production DB/file loading','inherit remains controlled','GoodInfo callback remains open','malformed sentinel remains open']}
    (ROOT/'analysis/archetype-metadata-coupled-x86-behavior.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','mixed_sequences','sequence_reader_pairs','coupled_pairs','coupled_abi_calls','coupled_destructor_calls','fallback_entries_actually_denied','real_loader_or_database_cases')},indent=2))
if __name__=='__main__':main()
