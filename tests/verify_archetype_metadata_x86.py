#!/usr/bin/env python3
"""P2 paired original/rebuilt readers, independent byte oracle, compiled defects.
Synthetic prepared objects/current-line INI; real reconstructed hash/cache on new
side. Controlled allocator/ASCII CRT/INI/tree/inherit/client; no DB/file claim.
"""
import argparse,collections,hashlib,itertools,json,os,pathlib,random,struct,subprocess,tempfile
import pefile
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_INVALID,UcError
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP
from x86_harness import X86Harness
from verify_good_info_price_x86 import binary80
ROOT=pathlib.Path(__file__).resolve().parents[1]
HASH='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
BASE='8f44ff91f1086f33fd81ca1c4f65f637a9733bf2'
TARGETS=[(0x62f05e0,0x62f0882),(0x62f41e0,0x62f4384),(0x62f5330,0x62f5438),(0x62c0370,0x62c0373),(0x62db060,0x62db063)]
READERS=['archetype_root_read','archetype_equipment_read','archetype_attached_read']
VT=['archetype_root_slots','archetype_equipment_slots','archetype_attached_slots']
OVT=[0x63a11c0,0x6399860,0x6399af4]
SIZES=[0x5c,0x70,0x88]
SCN=['?StringAlloc@@YAPADPBD_N@Z','?clear@CacheString@@QAEXXZ','?StringCacheArena@@3PADA','?StringCacheFront@@3IA','?StringCacheBack@@3IA','?StringCacheInternedCount@@3IA','?StringCachePrivateCount@@3IA','?StringCacheIndex@@3PAUStringCacheTree@@A']
GETEQ='?GetEquipment@Archetype@@YAPAUEquipment@1@I@Z'
GETID='?GetEquipmentID@Archetype@@YAIABUID_String@@@Z'
FILES=['src/archetype_metadata.cpp','src/archetype_metadata.hpp','tests/fixtures/archetype_metadata_runtime.cpp','tests/verify_archetype_metadata_x86.py','src/create_id.cpp','src/cfl_id_maker.hpp','src/string_cache.cpp','src/string_cache.hpp','src/archetype_id.cpp','src/archetype_equipment_lookup.cpp','src/good_block_reader.cpp','src/good_block_reader.hpp','src/good_info_price.cpp','src/good_info_price.hpp','src/good_info_destroy.cpp','tests/fixtures/good_block_reader_runtime.cpp','tests/fixtures/flid_x86_runtime.cpp','tests/fixtures/string_cache_x86_runtime.cpp','tests/fixtures/archetype_lookup_runtime.cpp','tests/x86_harness.py','tests/verify_good_info_price_x86.py','analysis/createid-behavior.json']
U=lambda x:struct.pack('<I',x&0xffffffff)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(source,name='archetype_metadata'):
    (ROOT/'build').mkdir(exist_ok=True)
    sources=[source]+[ROOT/f for f in ['tests/fixtures/archetype_metadata_runtime.cpp','src/create_id.cpp','src/string_cache.cpp','src/archetype_id.cpp','src/archetype_equipment_lookup.cpp','src/good_block_reader.cpp','src/good_info_price.cpp','src/good_info_destroy.cpp','tests/fixtures/good_block_reader_runtime.cpp','tests/fixtures/flid_x86_runtime.cpp','tests/fixtures/string_cache_x86_runtime.cpp','tests/fixtures/archetype_lookup_runtime.cpp']]
    commands=[];objects=[]
    for f in sources:
        obj=ROOT/'build'/(f.stem+'-'+name+'.obj');objects.append(str(obj))
        cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-Wall','-Wextra','-Werror','-I'+str(ROOT/'src'),'-c',str(f),'-o',str(obj)]
        subprocess.run(cmd,check=True);commands.append({'argv':cmd,'exit_code':0})
    symbols=READERS+['archetype_equipment_is_attached','archetype_attached_is_attached','arch_virtual_read','arch_virtual_attached','arch_diagnostic','arch_hash','arch_cache_clear','arch_string_alloc','create_id_reconstructed','?CreateID@@YAIPBD@Z',GETEQ,GETID,'good_info_read_block','good_block_find_good','good_block_find_hull','good_block_unknown_category','??1GoodInfo@@QAE@XZ']+SCN[:2]
    data=VT+SCN[2:]+['EquipmentArchetypeTree']
    dll=ROOT/'build'/(name+'.dll')
    cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x15000000','/out:'+str(dll)]+objects+['/export:'+s for s in symbols]+['/export:'+s+',DATA' for s in data]
    subprocess.run(cmd,check=True);commands.append({'argv':cmd,'exit_code':0})
    return dll,commands
# Independent binary80 -> binary32 rounding, integer arithmetic only.
def round32(data,cw):
    sig,se=struct.unpack('<QH',data);sign=se>>15;exp=se&0x7fff;rc=(cw>>10)&3
    if exp==0x7fff:
        if sig==1<<63:return (sign<<31)|0x7f800000
        # Unicorn softfloat commonNaNToFloat32 chooses default negative NaN
        # when all payload bits disappear in the target precision. Emulator
        # contract only; this is explicitly NOT a native x87 NaN claim.
        payload=(sig>>40)&0x7fffff
        if not payload:return 0xffc00000
        return (sign<<31)|0x7f800000|payload|0x400000
    if not sig:return sign<<31
    power=(exp or 1)-16383-63
    highest=sig.bit_length()-1+power
    step=max(highest-23,-149);shift=step-power
    if shift<=0:mant=sig<<(-shift);rem=0;den=1
    else:mant=sig>>shift;rem=sig&((1<<shift)-1);den=1<<shift
    inc=bool(rem) and (rc==1 and sign or rc==2 and not sign or rc==0 and (2*rem>den or 2*rem==den and mant&1))
    mant+=int(inc)
    if step==-149 and mant<1<<23:return (sign<<31)|mant
    if mant>=1<<24:mant>>=1;step+=1
    exponent=step+23+127
    if exponent>=255:
        infinity=rc==0 or rc==1 and sign or rc==2 and not sign
        return (sign<<31)|(0x7f800000 if infinity else 0x7f7fffff)
    return (sign<<31)|(exponent<<23)|(mant&0x7fffff)

class Machine:
    def __init__(self,dll,rebuilt):
        self.h=X86Harness();self.u=self.h.uc;self.original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
        self.orig=self.h.load(self.original);self.new=self.h.load(dll);self.rebuilt=rebuilt
        h=self.h;u=self.u;self.obj=h.scratch+0x100;self.reader=h.scratch+0x2000;self.client=h.scratch+0x2500;self.clientvt=h.scratch+0x2600
        self.node=h.scratch+0x2800;self.head=h.scratch+0x2900;self.source=h.scratch+0x2a00;self.fp=h.scratch+0x3000;self.control=self.fp+0x20;self.state=self.fp+0x40
        self.good=h.scratch+0x5000;self.listing=h.scratch+0x5800;self.tree=h.scratch+0x6000;self.nil=self.tree+0x100;self.treehead=self.tree+0x200;self.treenode=self.tree+0x300
        self.heap=0x23000000;u.mem_map(self.heap,0x1000000);u.mem_map(0,4096)
        self.cursor=self.heap;self.texts={};self.text_cursor=h.scratch+0x8000;self.events=[];self.spec={};self.position=-1;self.operations=[];self.block=False;self.fault=None;self.instructions=set();self.cache_calls=0;self.hash_calls=0
        self.arena=self.new[SCN[2]] if rebuilt else 0x6409810
        self.globals=[self.new[n] for n in SCN[3:]] if rebuilt else [0x63ecb6c,0x63ecb70,0x63ecb74,0x6589810,0x6589814]
        self.cache_entry=self.new[SCN[0]] if rebuilt else 0x6333bd0
        self.clear_entry=self.new[SCN[1]] if rebuilt else 0x6333d60
        self.hash_entry=self.new['?CreateID@@YAIPBD@Z'] if rebuilt else 0x630d470
        h.write_word(0x639902c,h.stop+0x900);h.write_word(0x6399350,h.stop+0x920);h.write_word(0x6399028,h.stop+0x1000);h.write_word(h.stop+0x1000,h.stop+0x940)
        h.write_word(self.client,self.clientvt);h.write_word(self.clientvt+8,h.stop+0x960)
        h.write_word(0x63fbad8,self.head)
        u.mem_write(h.stop+0x100,b'\xdb\x2d'+U(self.fp)+b'\xc2\x04\x00')
        u.mem_write(h.stop+0x120,b'\xdb\xe3\xd9\x2d'+U(self.control)+b'\xc3')
        u.mem_write(h.stop+0x140,b'\xdd\x35'+U(self.state)+b'\xc3')
        u.mem_write(h.stop+0x160,b'\xdb\x2d'+U(self.fp+0x200)+b'\xdb\x2d'+U(self.fp+0x210)+b'\xc3')
        u.mem_write(self.fp+0x200,binary80(1.25));u.mem_write(self.fp+0x210,binary80(-3.5))
        # Original-side dispatch uses ORIGINAL tables. Rebuilt-side uses partial reconstructed tables.
        u.mem_write(h.stop+0xa00,b'\x8b\x01\xff\x60\x04');u.mem_write(h.stop+0xa20,b'\x8b\x01\xff\x60\x24')
        u.hook_add(UC_HOOK_CODE,self.hook);u.hook_add(UC_HOOK_MEM_INVALID,self.invalid)
        # Initialize hash once before resetting per-case allocator regions.
        h.invoke(self.hash_entry,(0,));self.cursor=self.heap+0x10000
    def text_ptr(self,value):
        if value is None:return 0
        if value not in self.texts:
            p=self.text_cursor;data=value.encode('ascii')+b'\0';self.text_cursor+=len(data);assert self.text_cursor<self.h.scratch+0xe000
            self.u.mem_write(p,data);self.texts[value]=p
        return self.texts[value]
    def text(self,p):
        if not p:return None
        out=bytearray()
        for i in range(4096):
            b=self.u.mem_read(p+i,1)[0]
            if not b:return out.decode('ascii')
            out.append(b)
        raise AssertionError('unterminated fixture')
    def ret(self,value=0,pop=0):
        h=self.h;u=self.u;sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EAX,value&0xffffffff);u.reg_write(UC_X86_REG_EIP,h.word(sp));u.reg_write(UC_X86_REG_ESP,sp+4+pop)
    def invalid(self,u,access,address,size,value,user):self.fault=(access,address,size);return False
    def hook(self,u,a,size,user):
        h=self.h;sp=u.reg_read(UC_X86_REG_ESP);ecx=u.reg_read(UC_X86_REG_ECX)
        if any(lo<=a<hi for lo,hi in TARGETS):
            assert not self.rebuilt,'FORBIDDEN ORIGINAL P2 FALLBACK';self.instructions.add(a)
        if self.rebuilt and 0x62708c0<=a<0x62710ed:raise AssertionError('FORBIDDEN ORIGINAL P1 FALLBACK')
        # Existing P1 fixture thunks use original service VAs: bounce only to the
        # already reconstructed hash/cache/ID/lookup, never P2/P1 target bodies.
        if self.rebuilt and a in (0x630d470,0x6333bd0,0x6333d60,0x62f11d0,0x62f9370):
            target={0x630d470:self.hash_entry,0x6333bd0:self.cache_entry,0x6333d60:self.clear_entry,0x62f11d0:self.new[GETID],0x62f9370:self.new[GETEQ]}[a]
            u.reg_write(UC_X86_REG_EIP,target);return
        if a==self.hash_entry or self.rebuilt and a==self.new['arch_hash']:
            self.hash_calls+=1;self.events.append(('hash',self.text(h.word(sp+4))))
        elif a==self.cache_entry:
            self.cache_calls+=1;self.events.append(('cache',self.text(h.word(sp+4)),h.word(sp+8)&255))
        elif a==self.clear_entry:
            assert not self.obj<=ecx<self.obj+0x88 and not self.good<=ecx<self.good+0xc0,'clear touched object field'
            self.events.append(('clear-local',))
        elif a==0x6310200:
            assert self.block and ecx==self.reader;self.position+=1;self.events.append(('read',self.position));self.ret(0x80 if self.position<len(self.operations) else 0)
        elif a==0x63104a0:
            assert ecx==self.reader;k=self.text(h.word(sp+4));self.events.append(('is',k));key=self.operations[self.position][0] if self.block else self.spec['key'];self.ret(0x80 if k.lower()==key.lower() else 0,4)
        elif a in (0x6310ac0,0x6310c00):
            assert ecx==self.reader;idx=h.word(sp+4) if a==0x6310ac0 else None;val=self.operations[self.position][1][idx or 0] if self.block else self.spec.get('text','sample');self.events.append(('string',idx,val));self.ret(self.text_ptr(val),4 if idx is not None else 0)
        elif a in (0x6310850,0x6310640):
            assert ecx==self.reader and h.word(sp+4)==0;val=self.operations[self.position][1][0] if self.block else self.spec.get('integer',0x81234567);self.events.append(('int' if a==0x6310850 else 'bool',0,val&0xffffffff));self.ret(val,4)
        elif a==0x6310980:
            assert ecx==self.reader;idx=h.word(sp+4);values=self.spec.get('floats',[binary80(1.5),binary80(2.5),binary80(3.5)]);self.events.append(('float',idx,values[idx].hex()));u.mem_write(self.fp,values[idx]);u.reg_write(UC_X86_REG_EIP,h.stop+0x100)
        elif a==0x63015d0:
            value=h.word(h.word(sp+8));out=h.word(sp+4)
            if ecx==0x63fbad4:
                self.events.append(('inherit-query',value));h.write_word(out,self.head if self.spec.get('entry','missing')=='missing' else self.node)
            else:
                assert self.block;self.events.append(('hull-query',value));h.write_word(out,self.head);h.write_word(ecx+4,self.head)
            self.ret(out,8)
        elif a==0x62f3e20:
            target,source=h.word(sp+4),h.word(sp+8);self.events.append(('inherit-dispatch',target-self.obj,source-self.source));h.write_word(target+0x64,0x13579bdf);self.ret()
        elif a==h.stop+0x900:
            x=self.text(h.word(sp+4)).lower();y=self.text(h.word(sp+8)).lower();self.ret((x>y)-(x<y))
        elif a==h.stop+0x920:
            p=h.word(sp+4);text=self.text(p);assert text is not None and len(text)<=255;u.mem_write(p,text.lower().encode()+b'\0');self.ret(p)
        elif a==h.stop+0x940:
            sev,line,arg=h.word(sp+4),h.word(sp+16),h.word(sp+20)
            if line==0xe1:kind=0;value=self.text(arg)
            elif line==0x3c:kind=1;value=arg
            elif line==0x828:kind=2;value=self.text(arg)
            else:raise AssertionError(('unexpected diagnostic',hex(sev),hex(line)))
            assert sev==(0x100001 if kind==1 else 0x100002);self.events.append(('diagnostic',kind,value));self.ret()
        elif a==self.new['arch_diagnostic']:
            kind=h.word(sp+4);self.events.append(('diagnostic',kind,h.word(sp+12) if kind==1 else self.text(h.word(sp+8))));self.ret()
        elif a==h.stop+0x960:
            assert ecx==self.client and h.word(sp+4)==self.reader;self.events.append(('client',self.spec.get('callback',0x80)));h.write_word(self.obj+0x18,0xdeadbabe);self.ret(self.spec.get('callback',0x80),4)
        elif a==0x6391abc:
            length=h.word(sp+4);p=self.cursor;self.cursor+=(length+15)&~15;assert self.cursor<self.heap+0x1000000;u.mem_write(p,b'\xa5'*length);self.ret(p)
        elif a==0x6391a7a:self.events.append(('free',h.word(sp+4)));self.ret()
        elif a==self.new['good_block_find_good']:self.events.append(('good-query',h.word(sp+8)));self.ret(0)
        elif a==self.new['good_block_find_hull']:self.events.append(('hull-query',h.word(sp+4)));self.ret(0)
        elif a==self.new['good_block_unknown_category']:raise AssertionError('unplanned P1 category')
    def fpu(self):
        self.h.invoke(self.h.stop+0x140);data=bytes(self.u.mem_read(self.state,108));cw,sw,tag=[struct.unpack_from('<H',data,i)[0] for i in (0,4,8)];top=(sw>>11)&7
        live=tuple((i,data[28+10*i:38+10*i].hex()) for i in range(8) if (tag>>(2*((top+i)&7)))&3!=3)
        return cw,sw,tag,live
    def reset(self,cw=0x37f,older=False):
        h=self.h;u=self.u;self.events.clear();self.block=False;self.fault=None;self.cursor=self.heap+0x10000
        for p,v in zip(self.globals,[1,0x180000,1,0,0]):h.write_word(p,v)
        u.mem_write(self.arena,b'\0');u.mem_write(self.control,struct.pack('<H',cw));h.invoke(h.stop+0x120)
        if older:h.invoke(h.stop+0x160)
    def normalized(self,raw,kind):
        out=bytearray(raw);out[16:20]=U(kind)
        for offset in (0x0c,0x80):
            key=self.spec['key'].lower()
            if offset+4>SIZES[kind] or (offset==0x0c and key not in ('da_archetype','attachment_archetype')) or (offset==0x80 and key!='hp_child'):continue
            pos=16+offset;val=struct.unpack_from('<I',out,pos)[0]
            if self.arena<=val<self.arena+0x180000:out[pos:pos+4]=U(0x70000000+val-self.arena)
        return bytes(out)
    def invoke_reader(self,kind,spec,seed,cw=0x37f,older=False,virtual=False,reset=True):
        if reset:self.reset(cw,older)
        h=self.h;u=self.u;self.spec=spec;h.write_word(self.node+16,0 if spec.get('entry')=='null' else self.source)
        start=self.obj-16;u.mem_write(start,seed);h.write_word(self.obj,(self.new[VT[kind]] if self.rebuilt else OVT[kind]));h.write_word(self.obj+4,self.client if spec.get('client') else 0)
        before=bytes(u.mem_read(start,len(seed)));self.events.clear()
        regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP];values=[0x11223344,0x55667788,0x99aabbcc,0x12345678]
        for r,v in zip(regs,values):u.reg_write(r,v)
        entry=(self.new['arch_virtual_read'] if self.rebuilt else h.stop+0xa00) if virtual else (self.new[READERS[kind]] if self.rebuilt else TARGETS[kind][0])
        al=h.invoke(entry,(self.reader,),self.obj)&255
        assert all(u.reg_read(r)==v for r,v in zip(regs,values)),'reader nonvolatile registers'
        raw=bytes(u.mem_read(start,len(seed)));fpu=self.fpu();trace=tuple(self.events)
        counters=tuple(h.word(p) for p in self.globals[:4]);cache={}
        for offset in (12,128):
            key=spec['key'].lower()
            if offset+4<=SIZES[kind] and (offset==12 and key in ('da_archetype','attachment_archetype') or offset==128 and key=='hp_child'):
                p=h.word(self.obj+offset)
                if self.arena<=p<self.arena+0x180000:cache[offset]=(p-self.arena,self.text(p))
        return {'raw':raw,'before':before,'normalized':self.normalized(raw,kind),'al':al,'trace':trace,'fpu':fpu,'counters':counters,'cache':cache}

def oracle(result,kind,spec,cw,id_vectors,type_table):
    raw=result['raw'];want=bytearray(result['before']);key=spec['key'].lower();integer=spec.get('integer',0x81234567);text=spec.get('text','sample');expected_al=1
    offsets={'nickname':8,'explosion_arch':0x24,'tractored_explosion':0x68,'separation_explosion':0x70,'debris_type':0x74}
    ints={'ids_name':0x14,'ids_info':0x18,'units_per_container':0x64,'toughness':0x84}
    bools={'phantom_physics':0x39,'use_count':0x60,'lootable':0x6c}
    floats={'hit_pts':0x1c,'mass':0x20,'explosion_resistance':0x28,'volume':0x5c,'child_impulse':0x78,'parent_impulse':0x7c}
    def put(off,data):want[16+off:16+off+len(data)]=data
    recognized=set(offsets)|set(ints)|set(bools)|set(floats)|{'rotation_inertia','type','da_archetype','attachment_archetype','hp_child','mission_property','inherit'}
    if key in offsets:put(offsets[key],U(id_vectors[text]))
    elif key in ints:put(ints[key],U(integer))
    elif key in bools:put(bools[key],bytes([integer&255]))
    elif key in floats:put(floats[key],U(round32(spec.get('floats',[binary80(1.5)])[0],cw)))
    elif key=='rotation_inertia':
        values=spec.get('floats',[binary80(1.5),binary80(2.5),binary80(3.5)])
        for i,v in enumerate(values):put(0x2c+4*i,U(round32(v,cw)))
        put(0x38,b'\1')
    elif key=='type':put(0x10,U(type_table.get(text.upper(),0)))
    elif key in ('da_archetype','attachment_archetype','hp_child'):
        off=0x80 if key=='hp_child' else 0xc;put(off,raw[16+off:20+off]);assert result['cache'][off][1]==spec.get('expected_cached_text',text or '')
        assert [e for e in result['trace'] if e[0]=='cache']==[('cache',text,0 if key=='hp_child' else 1)]
        assert sum(e[0]=='clear-local' for e in result['trace'])==int(key!='hp_child')
    elif key=='inherit':
        entry=spec.get('entry','missing');assert [e[1] for e in result['trace'] if e[0]=='diagnostic']==([1,2] if entry=='missing' else [2] if entry=='null' else [])
        dispatch=[e for e in result['trace'] if e[0]=='inherit-dispatch'];assert dispatch==([('inherit-dispatch',0,0)] if entry=='valid' else [])
        if entry=='valid':put(0x64,U(0x13579bdf))
    elif key=='mission_property':pass
    else:
        callback=spec.get('callback',0x80) if spec.get('client') else 0;expected_al=callback if kind==0 else int(callback!=0)
    if spec.get('client') and key not in {'nickname','da_archetype','attachment_archetype','type','ids_name','ids_info','explosion_arch','explosion_resistance','hit_pts','mass','rotation_inertia','phantom_physics','mission_property'}:
        put(0x18,U(0xdeadbabe))
        if spec.get('callback',0x80):expected_al=spec.get('callback',0x80) if kind==0 else 1
    assert raw==bytes(want),('independent write set',kind,key,hex(cw),spec.get('floats'),[(i,a,b) for i,(a,b) in enumerate(zip(raw,want)) if a!=b][:8])
    assert result['al']==expected_al,('independent AL',kind,key,result['al'],expected_al)
    assert not any(e[0]=='free' for e in result['trace']),'unexpected old cache free'
    if key in ints or key in bools or key in floats:assert sum(e[0] in ('int','bool','float') for e in result['trace'])==1,'base getter repeated/skipped'
    if key in offsets:assert ('string',None if key=='tractored_explosion' else 0,text) in result['trace']
    if key=='type':assert sum(e[0]=='diagnostic' for e in result['trace'])==int(text.upper() not in type_table)
    if key not in recognized and spec.get('client'):assert sum(e[0]=='client' for e in result['trace'])==1

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--quick',action='store_true');parser.add_argument('--defects-only',action='store_true');args=parser.parse_args()
    original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert digest(original)==HASH
    p=pefile.PE(str(original));base=p.OPTIONAL_HEADER.ImageBase;types=[]
    for a in range(0x63eb810,0x63eb8f8,8):ptr,val=struct.unpack('<II',p.get_data(a-base,8));types.append((p.get_string_at_rva(ptr-base).decode(),val))
    vectors=json.loads((ROOT/'analysis/createid-behavior.json').read_text())['vectors'];id_vectors={(bytes.fromhex(v['input_hex']).decode('ascii') if v['input_hex'] is not None else None):int(v['result'],16) for v in vectors}
    dll,commands=build(ROOT/'src/archetype_metadata.cpp');machines=[Machine(dll,False),Machine(dll,True)];rng=random.Random(2462003);cases=[]
    def add(label,kind,key,**spec):cases.append((label,kind,dict(key=key,**spec)))
    rootkeys=['nickname','DA_archetype','attachment_archetype','type','ids_name','ids_info','explosion_arch','explosion_resistance','hit_pts','mass','rotation_inertia','phantom_physics','mission_property']
    equipkeys=['inherit','use_count','units_per_container','hit_pts','volume','tractored_explosion','lootable']
    attachkeys=['separation_explosion','debris_type','child_impulse','parent_impulse','HP_child','toughness']
    for kind in range(3):
        for key in rootkeys+(equipkeys if kind else [])+(attachkeys if kind==2 else []):add('every-key',kind,key,text='li01' if key.lower()!='type' else 'jUmP_gAtE')
        add('unknown',kind,'not-a-key')
        for cb in (0,1,0x80,0xff):add('client-al',kind,'not-a-key',client=True,callback=cb)
    for kind,key in [(k,'phantom_physics') for k in range(3)]+[(k,v) for k in (1,2) for v in ('use_count','lootable')]:
        for v in range(256):add('raw-bool',kind,key,integer=v)
    for kind,key in [(k,v) for k in range(3) for v in ('ids_name','ids_info')]+[(k,'units_per_container') for k in (1,2)]+[(2,'toughness')]:
        for v in (0,-1,-2147483648,2147483647,0x80000000,0xffffffff):add('integer-boundary',kind,key,integer=v)
    for token,val in types:
        for kind in range(3):add('all-object-types',kind,'type',text=''.join(c.lower() if i%2 else c for i,c in enumerate(token)))
    for kind in range(3):add('unknown-type',kind,'type',text='not-an-object-type')
    for kind,key in [(0,'nickname'),(2,'explosion_arch'),(1,'tractored_explosion'),(2,'separation_explosion'),(2,'debris_type')]:
        for text in (None,'','li01','LI01','Li01','ge_fighter','A'*255,'z'*255):add('id-vectors',kind,key,text=text)
    for kind in (1,2):
        for entry in ('missing','null','valid'):add('inherit-contract',kind,'inherit',text='li01',entry=entry)
    for kind,key in ((0,'DA_archetype'),(2,'attachment_archetype'),(2,'HP_child')):
        for text in ('','MixedCase','X'*255):add('cache',kind,key,text=text)
    floatkeys=[(0,'hit_pts'),(1,'mass'),(2,'explosion_resistance'),(1,'volume'),(2,'child_impulse'),(2,'parent_impulse'),(2,'rotation_inertia')]
    values=[binary80(v) for v in (0.,-0.,1.5,-2.5,2**-149,-2**-149,float('inf'),-float('inf'),float('nan'))]+[struct.pack('<QH',0x8000008000000000+i,0x3fff) for i in (-1,0,1)]+[struct.pack('<QH',1,0),struct.pack('<QH',0x8000000000000001,0x7fff)]
    controls=[0x7f|pc|rc for pc in (0,0x200,0x300) for rc in (0,0x400,0x800,0xc00)]
    for kind,key in floatkeys:
        for v in values:add('float80',kind,key,floats=[v]*3)
    # Named additional high-precision case is also the binary64-spill discriminator.
    add('full-st0-discriminator',0,'hit_pts',floats=[struct.pack('<QH',0x8000008000000001,0x3fff)]*3)
    def pair(kind,spec,seed,cw,virtual=False,older=False):
        a,b=[m.invoke_reader(kind,spec,seed,cw,older,virtual) for m in machines]
        oracle(a,kind,spec,cw,id_vectors,dict(types));oracle(b,kind,spec,cw,id_vectors,dict(types))
        for key in ('normalized','al','trace','fpu','counters','cache'):assert a[key]==b[key],('pair',kind,spec['key'],key,a[key],b[key])
        return a,b
    totals=collections.Counter();reader_count=0
    run_cases=cases[:65] if args.quick else ([] if args.defects_only else cases)
    for label,kind,spec in run_cases:
        seed=rng.randbytes(SIZES[kind]+32)
        cws=controls if label in ('float80','full-st0-discriminator') and not args.quick else [0x37f]
        for cw in cws:
            for virtual in (False,True):pair(kind,spec,seed,cw,virtual,reader_count%2==1);totals[label]+=1;reader_count+=1
    # Virtual is_attached including deliberately swapped Equipment/Attached tables.
    virtual_cases=0
    for storage_kind,table_kind in itertools.product((1,2),repeat=2):
        for m in machines:
            m.reset();m.u.mem_write(m.obj,rng.randbytes(0x88));m.h.write_word(m.obj,m.new[VT[table_kind]] if m.rebuilt else OVT[table_kind]);before=bytes(m.u.mem_read(m.obj,0x88));ecx=m.obj
            got=m.h.invoke(m.new['arch_virtual_attached'] if m.rebuilt else m.h.stop+0xa20,(),ecx)&255;assert got==table_kind-1 and m.u.reg_read(UC_X86_REG_ECX)==ecx;assert bytes(m.u.mem_read(m.obj,0x88))==before
        virtual_cases+=1
    mutations={
        'wrong_ids_name_offset':('word(self,0x14)=static_cast<ArchWord>(arch_int(r,0));','word(self,0x18)=static_cast<ArchWord>(arch_int(r,0));',0,dict(key='ids_name',integer=0x80000000)),
        'normalize_raw_field_bool':('octet(self,0x39)=arch_bool(r,0);','octet(self,0x39)=arch_bool(r,0)!=0;',0,dict(key='phantom_physics',integer=0xfe)),
        'constant_true_is_attached':('archetype_equipment_is_attached(void*) { return 0; }','archetype_equipment_is_attached(void*) { return 1; }',1,None),
        'skip_root_base_hit':('if (archetype_root_read(self,r)) return 1;','if (false) return 1;',1,dict(key='ids_name',integer=42)),
        'normalize_root_callback_al':('return slots[2](client,r);','return slots[2](client,r)!=0;',0,dict(key='not-a-key',client=True,callback=0x80)),
        'root_string_flag_zero':('arch_string_alloc(value,true)','arch_string_alloc(value,false)',0,dict(key='DA_archetype',text='MixedCase')),
        'free_old_cache_handle':('arch_cache_clear(&temporary);','reinterpret_cast<void(__cdecl*)(void*)>(0x06391a7a)(reinterpret_cast<void*>(word(self,0x0c))); arch_cache_clear(&temporary);',0,dict(key='DA_archetype',text='MixedCase')),
        'merge_inherit_missing_null':('if (node==arch_inherit_sentinel()) arch_diagnostic(1,nullptr,id);','if (node==arch_inherit_sentinel()) {}',1,dict(key='inherit',text='li01',entry='missing')),
        'swap_dispatch_arguments':('arch_inherit_dispatch(self,source);','arch_inherit_dispatch(source,self);',1,dict(key='inherit',text='li01',entry='valid')),
        'early_binary64_spill':('fstp dword ptr [ebx]','sub esp, 8\n        fstp qword ptr [esp]\n        fld qword ptr [esp]\n        add esp, 8\n        fstp dword ptr [ebx]',0,dict(key='hit_pts',floats=[struct.pack('<QH',0x8000008000000001,0x3fff)]*3)),
    }
    defects={}
    if not args.quick:
        scratch=pathlib.Path(tempfile.mkdtemp(prefix='fla246-defects-',dir='/opt/data/cache/scratch'));source=(ROOT/FILES[0]).read_text()
        for label,(before,after,kind,spec) in mutations.items():
            assert source.count(before)==1,label;path=scratch/(label+'.cpp');path.write_text(source.replace(before,after));bad_dll,bad_commands=build(path,'p2_defect_'+label);commands+=bad_commands;bad=Machine(bad_dll,True);seed=rng.randbytes(SIZES[kind]+32)
            if spec is None:
                good=machines[1];good.h.write_word(good.obj,good.new[VT[1]]);bad.h.write_word(bad.obj,bad.new[VT[1]]);expected=good.h.invoke(good.new['arch_virtual_attached'],(),good.obj)&255;got=bad.h.invoke(bad.new['arch_virtual_attached'],(),bad.obj)&255;assert expected==0 and got==1;reason='independent slot+0x24 false expectation violated'
            else:
                good_a,good_b=pair(kind,spec,seed,0x37f)
                try:
                    result=bad.invoke_reader(kind,spec,seed);oracle(result,kind,spec,0x37f,id_vectors,dict(types))
                    assert all(result[k]==good_b[k] for k in ('normalized','al','trace','fpu','counters','cache')),'compiled defect differs from passing pair'
                except AssertionError as e:reason=str(e)
                else:raise AssertionError(('compiled defect escaped',label))
            defects[label]={'discriminator':spec or {'slot':'0x24','table':'Equipment'},'detected':True,'reason':reason,'mutation_source':str(path),'mutation_source_sha256':digest(path),'dll_sha256':digest(bad_dll)}
        assert len(defects)==10
    report={'status':'passed' if not args.quick and not args.defects_only else 'debug-only' if args.quick else 'defects-only','base_commit':BASE,'original_sha256':HASH,'reader_pairs':reader_count,'independent_reader_oracles':reader_count*2,'counts':dict(totals),'virtual_is_attached_pairs':virtual_cases,'x87_controls':[hex(c) for c in controls],'compiled_defects':defects,'dll_sha256':digest(dll),'source_hashes':{f:digest(ROOT/f) for f in FILES},'commands':commands,'object_type_table':types,'object_type_tokens_sha256':hashlib.sha256(json.dumps(types,separators=(',',':')).encode()).hexdigest(),'id_vector_input_sha256':digest(ROOT/'analysis/createid-behavior.json'),'original_instruction_addresses':sorted(hex(a) for a in machines[0].instructions),'evidence_kind':'synthetic objects; original vs reconstructed x86 with controlled service boundaries','open':['coupled P1 path and full regressions reported separately','real DB/file loader','native Windows/CRT','inherit copy implementation','GoodInfo callback','malformed sentinel','unmasked x87 exceptions','full game']}
    if not args.quick:(ROOT/'analysis'/('archetype-metadata-defects.json' if args.defects_only else 'archetype-metadata-x86-behavior.json')).write_text(json.dumps(report,indent=2,default=lambda v:v.hex() if isinstance(v,bytes) else str(v))+'\n')
    print(json.dumps({k:report[k] for k in ('status','reader_pairs','independent_reader_oracles','counts','virtual_is_attached_pairs','compiled_defects')},indent=2,default=lambda v:v.hex() if isinstance(v,bytes) else str(v)))
if __name__=='__main__':main()
