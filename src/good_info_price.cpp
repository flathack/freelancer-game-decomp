#include "good_info_price.hpp"
// Original binary32 constants; do not replace them by decimal double factors.
extern "C" const unsigned int good_price_zero_bits = 0x00000000;
extern "C" const unsigned int good_price_low_bits  = 0x3f733333; // 0.95f
extern "C" const unsigned int good_price_high_bits = 0x3f866666; // 1.05f

// Temporary arithmetic boundary. Original FILD keeps the signed integer in ST0
// while FST writes its rounded binary32 view at 0x58. Every default multiplies
// the original ST0, not the rounded field. FCOMP/FNSTSW also preserves original
// behavior for signed zeros, unordered values and caller x87 control settings.
extern "C" __declspec(naked) void __cdecl good_info_set_price(void*, int) {
    __asm {
        mov ecx, dword ptr [esp+4]
        fild dword ptr [esp+8]
        fst dword ptr [ecx+58h]
        fld dword ptr [ecx+5ch]
        fcomp dword ptr [good_price_zero_bits]
        fnstsw ax
        test ah, 44h
        jp skip_good_buy
        fld dword ptr [good_price_low_bits]
        fmul st, st(1)
        fstp dword ptr [ecx+5ch]
    skip_good_buy:
        fld dword ptr [ecx+60h]
        fcomp dword ptr [good_price_zero_bits]
        fnstsw ax
        test ah, 44h
        jp skip_bad_buy
        fld dword ptr [good_price_high_bits]
        fmul st, st(1)
        fstp dword ptr [ecx+60h]
    skip_bad_buy:
        fld dword ptr [ecx+64h]
        fcomp dword ptr [good_price_zero_bits]
        fnstsw ax
        test ah, 44h
        jp skip_good_sell
        fld dword ptr [good_price_high_bits]
        fmul st, st(1)
        fstp dword ptr [ecx+64h]
    skip_good_sell:
        fld dword ptr [ecx+68h]
        fcomp dword ptr [good_price_zero_bits]
        fnstsw ax
        test ah, 44h
        jp skip_bad_sell
        fmul dword ptr [good_price_low_bits]
        fstp dword ptr [ecx+68h]
        ret
    skip_bad_sell:
        fstp st(0)
        ret
    }
}

extern "C" __declspec(naked) void __cdecl good_info_read_price_multiplier(
    void*, INI_Reader*, unsigned int) {
    __asm {
        push esi
        push edi
        mov esi, dword ptr [esp+12]
        mov ecx, dword ptr [esp+16]
        mov edi, dword ptr [esp+20]
        push 0
        call good_price_value_float
        fmul dword ptr [esi+58h]
        fstp dword ptr [esi+edi]
        pop edi
        pop esi
        ret
    }
}
