#pragma once
#include "good_info_price.hpp"

// P1 storage-level blockreader, not a recovered polymorphic class or file loader.
// GoodInfo storage is 192 bytes; GoodInfoList is an opaque runtime binding.
// All runtime dependencies below must be supplied by integration. Fixtures bind
// them to controlled reader/hash/cache/index/Archetype services, NOT a database.
using GoodBlockWord = unsigned int;
extern "C" void __thiscall good_info_read_block(void* list, INI_Reader*, void* storage);
extern "C" unsigned char __thiscall good_block_read_value(INI_Reader*);
extern "C" unsigned char __thiscall good_block_is_value(INI_Reader*, const char*);
extern "C" unsigned char __thiscall good_block_is_empty(INI_Reader*, unsigned int);
extern "C" const char* __thiscall good_block_whole_string(INI_Reader*);
extern "C" const char* __thiscall good_block_indexed_string(INI_Reader*, unsigned int);
extern "C" int __thiscall good_block_int(INI_Reader*, unsigned int);
// Preserve raw AL, including noncanonical true bytes; do not normalize to bool.
extern "C" unsigned char __thiscall good_block_bool(INI_Reader*, unsigned int);
extern "C" GoodBlockWord good_block_hash(const char*);
extern "C" GoodBlockWord good_block_resolve(const GoodBlockWord*);
extern "C" void* good_block_find_good(void* list, GoodBlockWord);
extern "C" void* good_block_find_hull(GoodBlockWord);
extern "C" void* good_block_get_equipment(GoodBlockWord);
extern "C" int good_block_stricmp(const char*, const char*);
extern "C" void good_block_unknown_category(const char*);
extern "C" void __thiscall good_block_cache_clear(GoodBlockWord*);
extern "C" const char* good_block_string_alloc(const char*, bool lowercase);
extern "C" void* good_block_allocate(unsigned int);
extern "C" GoodBlockWord good_block_bay_pointer();
extern "C" unsigned short good_block_subobj_none();
