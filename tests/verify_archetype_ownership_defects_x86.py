#!/usr/bin/env python3
"""Compile actual faulty ownership bodies and reject them with original oracles."""
import collections
import hashlib
import json
from unicorn import UcError
from verify_archetype_lifecycle_x86 import (ROOT, Machine, build, alignment_cases,
    copy_cases, self_cases, destroy_cases, reader_cases, x87_cases, failure_cases)
from verify_archetype_ownership_x86 import assert_pair, CLASS_FIELDS, EQ_WORDS, EQ_BYTES, field_oracle


def subtype_probe(ms, counts):
    for cls in (8,9,14,17,31,32,33):
        for m in ms:
            m.reset_case(91)
            m.tree_fixture(m.obj,1,m.heap+0x30000,0)
            m.tree_fixture(m.source,3,m.heap+0x40000,0)
            m.classes={m.obj:cls,m.source:cls}
            if cls in (14,17):
                off=0xa8 if cls==14 else 0xbc
                m.vector_fixture(m.obj+off,2,2,m.heap+0x20000)
                m.vector_fixture(m.source+off,5,5,m.heap+0x21000)
            before,source=m.snapshot()[:2]
            m.call(0x62f3e20,'arch_inherit_dispatch',(m.obj,m.source),this=False,ret_pointer=False)
            ew,eb=CLASS_FIELDS[cls]
            if cls not in (14,17):
                field_oracle(before,m.snapshot()[0],source,EQ_WORDS+ew,EQ_BYTES+eb,True)
        assert_pair(ms)


def main():
    source=ROOT/'src/archetype_ownership.cpp'
    text=source.read_text()
    variants=[
        ('wrong_root_default','word(p,28)=0x42c80000;','word(p,28)=0x42c80001;',alignment_cases),
        ('omit_base_vptr','vptr(p,archetype_lifetime_root_slots); return p;','return p;',alignment_cases),
        ('copy_padding','word(d,0x5c)=word(s,0x5c); octet(d,0x60)=octet(s,0x60);','word(d,0x5c)=word(s,0x5c); octet(d,0x60)=octet(s,0x60); octet(d,0x61)=octet(s,0x61);',subtype_probe),
        ('shallow_root_nodes','t->head->parent=clone(t,source->head->parent,t->head);','t->head->parent=source->head->parent;',copy_cases),
        ('self_early_return','archetype_root_assign(void* d,const void* s) {','archetype_root_assign(void* d,const void* s) { if(d==s) return d;',self_cases),
        ('addref_before_release','client_call(word(d,4),1); word(d,4)=word(s,4); client_call(word(d,4),0);','Word old=word(d,4); word(d,4)=word(s,4); client_call(word(d,4),0); client_call(old,1);',copy_cases),
        ('omit_arm31','case 31: archetype_assign_0626f660(d,s); break;','case 31: archetype_equipment_assign(d,s); break;',subtype_probe),
        ('replace_target_nickname','word(d,8)=nickname; client_call','word(d,8)=nickname+1; client_call',subtype_probe),
        ('alias_subtype_vector','Word out=reinterpret_cast<Word>(arch_runtime_allocate(length*4));','(void)length; Word out=source;',subtype_probe),
        ('omit_nil_free','arch_runtime_free(nil); t->nil=nullptr;','(void)nil; t->nil=nullptr;',destroy_cases),
        ('ignore_array_cookie','if (flags&2) {','if (false) {',destroy_cases),
        ('fpu_stack_pollution','archetype_root_assign(void* d,const void* s) {','archetype_root_assign(void* d,const void* s) { __asm { fninit }',x87_cases),
        ('invent_oom_success','nil->parent=nullptr; nil->nil=0;','if (!nil) return; nil->parent=nullptr; nil->nil=0;',failure_cases),
        ('wrong_base_class8','archetype_equipment_class(void*) { return 6; }','archetype_equipment_class(void*) { return 8; }',reader_cases),
        ('query_without_exact_guard','return candidate==EquipmentArchetypeTree.head || id<candidate->key','return candidate==EquipmentArchetypeTree.head',reader_cases),
    ]
    records=[]
    for name,old,new,probe in variants:
        assert text.count(old)==1,(name,text.count(old))
        path=ROOT/'build/fla263-ownership'/('defect-'+name+'.cpp')
        mutated=text.replace(old,new)
        if name=='shallow_root_nodes':
            # Removing the clone call intentionally leaves its body unused.
            # Keep that body emitted in THIS mutant so -Werror is not mistaken
            # for a behavioral rejection; production warnings stay unchanged.
            marker='static Node* clone(Tree* d, const Node* s, Node* parent) {'
            assert mutated.count(marker)==1
            mutated=mutated.replace(marker,'__attribute__((used)) '+marker)
        path.write_text(mutated)
        dll,commands=build(path,'defect-'+name)
        machines=[Machine(dll,False),Machine(dll,True)]
        try:
            probe(machines,collections.Counter())
        except (AssertionError,UcError) as exc:
            record={'name':name,'compiled':True,'rejected':True,'probe':probe.__name__,
                    'discriminator':str(exc) or type(exc).__name__,'commands':commands}
            records.append(record)
            print(json.dumps({k:v for k,v in record.items() if k!='commands'}),flush=True)
        else:
            raise AssertionError('SURVIVING COMPILED OWNERSHIP DEFECT '+name)
    report={'issue':'FLA-263','compiled_defects':records,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'native_runs':0,'limits':['Mutants are rebuilt and executed; a compiler/link failure is not accepted as rejection.']}
    target=ROOT/'analysis/fla263/ownership-defects.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',len(records),'compiled ownership defects rejected')

if __name__=='__main__':main()
