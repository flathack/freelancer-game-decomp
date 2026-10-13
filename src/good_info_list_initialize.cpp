// GoodInfoList default construction, original common.dll VA 0x062704f0.
using u32=unsigned int;
struct GoodInfoListStorage { unsigned char bytes[52]; };
extern "C" void* good_info_list_allocate(u32);
static u32& word(GoodInfoListStorage* p,unsigned o) {return *reinterpret_cast<u32*>(p->bytes+o);}
extern "C" GoodInfoListStorage* __fastcall good_info_list_initialize(GoodInfoListStorage* p,u32 opaque) {
    p->bytes[0]=static_cast<unsigned char>(opaque);
    auto* list=static_cast<u32*>(good_info_list_allocate(12));
    list[0]=reinterpret_cast<u32>(list);list[1]=reinterpret_cast<u32>(list);
    word(p,4)=reinterpret_cast<u32>(list);word(p,8)=0;
    for(unsigned o=12;o<=32;o+=20) {
        p->bytes[o]=p->bytes[o+1]=static_cast<unsigned char>(opaque);p->bytes[o+12]=0;
        auto* nil=static_cast<u32*>(good_info_list_allocate(24));
        nil[1]=0;reinterpret_cast<unsigned char*>(nil)[20]=1;reinterpret_cast<unsigned char*>(nil)[21]=1;
        word(p,o+8)=reinterpret_cast<u32>(nil);nil[0]=0;nil[2]=0;
        auto* head=static_cast<u32*>(good_info_list_allocate(24));
        head[1]=reinterpret_cast<u32>(nil);reinterpret_cast<unsigned char*>(head)[20]=0;reinterpret_cast<unsigned char*>(head)[21]=0;
        word(p,o+4)=reinterpret_cast<u32>(head);head[0]=reinterpret_cast<u32>(head);head[2]=reinterpret_cast<u32>(head);word(p,o+16)=0;
    }
    return p;
}
extern "C" GoodInfoListStorage* __thiscall good_info_list_constructor(GoodInfoListStorage*) asm("??0GoodInfoList@@QAE@XZ");
extern "C" __attribute__((naked)) GoodInfoListStorage* __thiscall good_info_list_constructor(GoodInfoListStorage*) {
    __asm { movzx edx, byte ptr [esp-17] }
    __asm { jmp good_info_list_initialize }
}
