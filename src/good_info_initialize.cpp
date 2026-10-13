// ABI storage view, not a recovered polymorphic GoodInfo class definition.
struct GoodInfoStorage {unsigned char bytes[192];};
extern "C" void* good_info_runtime_allocate(unsigned int);
extern "C" unsigned int good_info_runtime_vtable(bool);
extern "C" unsigned int good_info_runtime_empty_cache();
extern unsigned int CreateID(const char*);
static void word(GoodInfoStorage* p,unsigned int offset,unsigned int value){__builtin_memcpy(p->bytes+offset,&value,4);}
extern "C" GoodInfoStorage* __fastcall good_info_initialize(GoodInfoStorage* p,unsigned int opaque){
 word(p,4,0);p->bytes[8]=0;word(p,0,good_info_runtime_vtable(false));word(p,72,0);
 for(unsigned int offset=116;offset<=132;offset+=4)word(p,offset,good_info_runtime_empty_cache());
 for(unsigned int offset=148;offset<=172;offset+=12){
  p->bytes[offset]=static_cast<unsigned char>(opaque);
  void* head=good_info_runtime_allocate(40);unsigned int pointer=reinterpret_cast<unsigned int>(head);
  __builtin_memcpy(head,&pointer,4);__builtin_memcpy(static_cast<unsigned char*>(head)+4,&pointer,4);
  word(p,offset+4,pointer);word(p,offset+8,0);
 }
 word(p,0,good_info_runtime_vtable(true));word(p,72,CreateID(nullptr));
 for(unsigned int offset=80;offset<=104;offset+=4)word(p,offset,0);
 p->bytes[112]=0;
 for(unsigned int offset=136;offset<=144;offset+=4)word(p,offset,0);
 word(p,184,0);word(p,188,0);word(p,76,0xffffffff);word(p,108,50);return p;
}
extern "C" GoodInfoStorage* __thiscall good_info_default(GoodInfoStorage*) __asm__("??0GoodInfo@@QAE@XZ");
extern "C" __declspec(naked) GoodInfoStorage* __thiscall good_info_default(GoodInfoStorage*){
 __asm {movzx edx,byte ptr [esp-17]
        jmp good_info_initialize}
}
