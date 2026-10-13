#pragma once
// Scoped reconstruction of pricing branches in GoodInfoList::read_Good_block
// (common.dll VA 0x062708c0), NOT a complete GoodInfo class or block reader.
// Storage must provide the observed 192-byte GoodInfo extent. Offsets 0x58..0x68
// contain the base price and four binary32 buy/sell prices.
struct INI_Reader;
extern "C" void __cdecl good_info_set_price(void* storage, int price);
// offset must be 0x5c, 0x60, 0x64 or 0x68. This preserves the value getter's
// full ST0 precision until FMUL/FSTP, without a C++ double/binary32 spill.
extern "C" void __cdecl good_info_read_price_multiplier(
    void* storage, INI_Reader* reader, unsigned int offset);
// Runtime binding: thiscall getter with index on stack, result in ST0. A native
// binding must implement the original x87 ABI, not a rounded C++ float return.
extern "C" double __thiscall good_price_value_float(INI_Reader*, unsigned int);
