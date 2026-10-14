#include "../../src/good_block_reader.hpp"
// Controlled services only. None of the original blockreader instructions are
// executed on the reconstructed side. Original-address getter services are
// intercepted by the Python harness. Full ST0 getter is reused unchanged.
#define JUMP(address) __asm { mov eax, address } __asm { jmp eax }
extern "C" __declspec(naked) unsigned char __thiscall good_block_read_value(INI_Reader*) { JUMP(06310200h) }
extern "C" __declspec(naked) unsigned char __thiscall good_block_is_value(INI_Reader*, const char*) { JUMP(063104a0h) }
extern "C" __declspec(naked) unsigned char __thiscall good_block_is_empty(INI_Reader*, unsigned int) { JUMP(063105f0h) }
extern "C" __declspec(naked) const char* __thiscall good_block_whole_string(INI_Reader*) { JUMP(06310c00h) }
extern "C" __declspec(naked) const char* __thiscall good_block_indexed_string(INI_Reader*, unsigned int) { JUMP(06310ac0h) }
extern "C" __declspec(naked) int __thiscall good_block_int(INI_Reader*, unsigned int) { JUMP(06310850h) }
extern "C" __declspec(naked) unsigned char __thiscall good_block_bool(INI_Reader*, unsigned int) { JUMP(06310640h) }
extern "C" __declspec(naked) double __thiscall good_price_value_float(INI_Reader*, unsigned int) { JUMP(06310980h) }
extern "C" __declspec(naked) unsigned int good_block_hash(const char*) { JUMP(0630d470h) }
extern "C" __declspec(naked) unsigned int good_block_resolve(const unsigned int*) { JUMP(062f11d0h) }
extern "C" __declspec(naked) void* good_block_get_equipment(unsigned int) { JUMP(062f9370h) }
extern "C" __declspec(naked) void __thiscall good_block_cache_clear(unsigned int*) { JUMP(06333d60h) }
extern "C" __declspec(naked) const char* good_block_string_alloc(const char*, bool) { JUMP(06333bd0h) }
extern "C" __declspec(naked) void* good_block_allocate(unsigned int) { JUMP(06391abch) }
extern "C" __declspec(naked) int good_block_stricmp(const char*, const char*) {
    __asm { jmp dword ptr ds:[0639902ch] }
}
// New-side lookup/diagnostic traps make the dependency boundary explicit.
// Python provides the same scripted lookup contract to both images.
extern "C" __declspec(naked) void* good_block_find_good(void*, unsigned int) { __asm { int 3 } __asm { ret } }
extern "C" __declspec(naked) void* good_block_find_hull(unsigned int) { __asm { int 3 } __asm { ret } }
extern "C" __declspec(naked) void good_block_unknown_category(const char*) { __asm { int 3 } __asm { ret } }
extern "C" __declspec(naked) unsigned int good_block_bay_pointer() {
    __asm { mov eax, dword ptr ds:[063fbf0ch] }
    __asm { ret }
}
extern "C" __declspec(naked) unsigned short good_block_subobj_none() {
    __asm { mov ax, word ptr ds:[063a4a74h] }
    __asm { ret }
}
// Reuse reconstructed GoodInfo destruction to verify node ownership/unlinking.
extern "C" __declspec(naked) void good_info_runtime_free(void*) { JUMP(06391a7ah) }
extern "C" unsigned int good_info_runtime_vtable(bool) { return 0x063993e8; }

// thiscall block ABI checker. Args: entry, list, reader, good. Original and new
// must each RET 8 and preserve EBX/ESI/EDI/EBP. Harness verifies outer CDECL ESP.
extern "C" __declspec(naked) unsigned int __cdecl good_block_check_abi(unsigned int, void*, INI_Reader*, void*) {
    __asm {
        push ebx
        push esi
        push edi
        push ebp
        mov ebx, 11223344h
        mov esi, 55667788h
        mov edi, 99aabbcch
        mov ebp, 12345678h
        mov ecx, dword ptr [esp+24]
        mov eax, dword ptr [esp+20]
        push dword ptr [esp+32]
        push dword ptr [esp+32]
        call eax
        xor eax, eax
        cmp ebx, 11223344h
        jne finished
        cmp esi, 55667788h
        jne finished
        cmp edi, 99aabbcch
        jne finished
        cmp ebp, 12345678h
        jne finished
        inc eax
    finished:
        pop ebp
        pop edi
        pop esi
        pop ebx
        ret
    }
}
