#include "../../src/archetype_metadata.hpp"
#include "../../src/cfl_id_maker.hpp"
#include "../../src/string_cache.hpp"
#define JUMP(address) __asm { mov eax, address } __asm { jmp eax }
extern "C" __declspec(naked) unsigned char __thiscall arch_is_value(INI_Reader*, const char*) { JUMP(063104a0h) }
extern "C" __declspec(naked) const char* __thiscall arch_indexed_string(INI_Reader*, unsigned int) { JUMP(06310ac0h) }
extern "C" __declspec(naked) const char* __thiscall arch_whole_string(INI_Reader*) { JUMP(06310c00h) }
extern "C" __declspec(naked) int __thiscall arch_int(INI_Reader*, unsigned int) { JUMP(06310850h) }
extern "C" __declspec(naked) unsigned char __thiscall arch_bool(INI_Reader*, unsigned int) { JUMP(06310640h) }
extern "C" __declspec(naked) double __thiscall arch_float(INI_Reader*, unsigned int) { JUMP(06310980h) }
extern "C" ArchWord create_id_reconstructed(const char*);
extern "C" ArchWord arch_hash(const char* s) { return create_id_reconstructed(s); }
extern "C" void __thiscall arch_cache_clear(ArchWord* p) { reinterpret_cast<CacheString*>(p)->clear(); }
extern "C" const char* arch_string_alloc(const char* s, bool p) { return StringAlloc(s,p); }
extern "C" __declspec(naked) int arch_stricmp(const char*, const char*) { __asm { jmp dword ptr ds:[0639902ch] } }
extern "C" void* arch_inherit_node(ArchWord id) {
    void* result;
    using Query=void*(__thiscall*)(void*,void**,const ArchWord*);
    reinterpret_cast<Query>(0x063015d0)(reinterpret_cast<void*>(0x063fbad4),&result,&id);
    return result;
}
extern "C" void* arch_inherit_sentinel() { return *reinterpret_cast<void**>(0x063fbad8); }
extern "C" __declspec(naked) void arch_inherit_dispatch(void*,void*) { JUMP(062f3e20h) }
extern "C" __declspec(naked) void arch_diagnostic(unsigned int,const char*,ArchWord) { __asm { int 3 } __asm { ret } }
// Deliberate mutation-only trap; correct source never frees arena field handles.
extern "C" __declspec(naked) void arch_defect_free(void*) { JUMP(06391a7ah) }
extern "C" __declspec(naked) unsigned int __thiscall arch_virtual_read(void*,INI_Reader*) { __asm { mov eax, [ecx] } __asm { jmp dword ptr [eax+4] } }
extern "C" __declspec(naked) unsigned int __thiscall arch_virtual_attached(void*) { __asm { mov eax, [ecx] } __asm { jmp dword ptr [eax+24h] } }
