#include "../../src/good_info_price.hpp"
// Fixture binds only a dependency; no original pricing instructions execute
// when calling the reconstructed handlers. The getter is controlled by the
// Unicorn hook in the differential suite and returns genuine binary80 ST0.
extern "C" __declspec(naked) double __thiscall good_price_value_float(
    INI_Reader*, unsigned int) {
    __asm { mov eax, 06310980h }
    __asm { jmp eax }
}
// ABI checker: calls either CDECL handler while seeding nonvolatile registers.
// Returns 1 iff EBX/ESI/EDI/EBP survived. Real ESP cleanup is checked by harness.
extern "C" __declspec(naked) unsigned int __cdecl good_price_check_abi(
    unsigned int, void*, unsigned int, unsigned int) {
    __asm {
        push ebx
        push esi
        push edi
        push ebp
        mov ebx, 11223344h
        mov esi, 55667788h
        mov edi, 99aabbcch
        mov ebp, 12345678h
        // Original arguments now at ESP+20, +24, +28, +32.
        push dword ptr [esp+32]
        push dword ptr [esp+32]
        push dword ptr [esp+32]
        call dword ptr [esp+32]
        add esp, 12
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
