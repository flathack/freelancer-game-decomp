// GoodInfo assignment, common.dll VA 0x06264300. Storage view pending full class.
using u32=unsigned int;
struct GoodInfoStorage { unsigned char bytes[192]; };
extern "C" void* good_info_runtime_allocate(u32);
extern "C" void good_info_runtime_free(void*);
static u32& word(GoodInfoStorage* p,unsigned o) {return *reinterpret_cast<u32*>(p->bytes+o);}
static void copy(unsigned char* d,const unsigned char* s,unsigned n) {for(unsigned i=0;i<n;++i)d[i]=s[i];}
static void assign_list(GoodInfoStorage* d,GoodInfoStorage* s,unsigned o) {
    if(d==s)return;
    auto* dh=reinterpret_cast<u32*>(word(d,o+4));auto* sh=reinterpret_cast<u32*>(word(s,o+4));
    auto* dn=reinterpret_cast<u32*>(dh[0]);auto* sn=reinterpret_cast<u32*>(sh[0]);
    while(dn!=dh && sn!=sh) {
        copy(reinterpret_cast<unsigned char*>(dn)+8,reinterpret_cast<unsigned char*>(sn)+8,32);
        dn=reinterpret_cast<u32*>(dn[0]);sn=reinterpret_cast<u32*>(sn[0]);
    }
    while(dn!=dh) {
        auto* next=reinterpret_cast<u32*>(dn[0]);reinterpret_cast<u32*>(dn[1])[0]=dn[0];next[1]=dn[1];
        good_info_runtime_free(dn);--word(d,o+8);dn=next;
    }
    while(sn!=sh) {
        auto* previous=reinterpret_cast<u32*>(dh[1]);auto* node=static_cast<u32*>(good_info_runtime_allocate(40));
        node[0]=reinterpret_cast<u32>(dh);node[1]=reinterpret_cast<u32>(previous?previous:node);dh[1]=reinterpret_cast<u32>(node);reinterpret_cast<u32*>(node[1])[0]=reinterpret_cast<u32>(node);
        auto* out=reinterpret_cast<unsigned char*>(node)+8;auto* in=reinterpret_cast<unsigned char*>(sn)+8;
        for(unsigned i=0;i<32;++i)if(i!=1 && !(i>=13&&i<=15) && !(i>=25&&i<=27))out[i]=in[i];
        ++word(d,o+8);sn=reinterpret_cast<u32*>(sn[0]);
    }
}
extern "C" GoodInfoStorage* __thiscall good_info_assign(GoodInfoStorage*,GoodInfoStorage*) asm("??4GoodInfo@@QAEAAU0@ABU0@@Z");
extern "C" GoodInfoStorage* __thiscall good_info_assign(GoodInfoStorage* d,GoodInfoStorage* s) {
    unsigned length=0;while(s->bytes[8+length])++length;if(length>=64)length=63;
    copy(d->bytes+8,s->bytes+8,length);d->bytes[8+length]=0;word(d,4)=length;
    for(unsigned o=72;o<=108;o+=4)word(d,o)=word(s,o);
    d->bytes[112]=s->bytes[112];for(unsigned o=116;o<=144;o+=4)word(d,o)=word(s,o);
    assign_list(d,s,148);assign_list(d,s,160);assign_list(d,s,172);
    word(d,184)=word(s,184);word(d,188)=word(s,188);return d;
}
