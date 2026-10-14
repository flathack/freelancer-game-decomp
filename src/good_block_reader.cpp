#include "good_block_reader.hpp"
using u32 = GoodBlockWord;
static u32 word(const void* p, unsigned int offset) {
    // Integer address arithmetic preserves the observed unchecked low-address
    // reads for missing hull/equipment; this is NOT a safe replacement API.
    return *reinterpret_cast<const volatile u32*>(reinterpret_cast<u32>(p) + offset);
}
static void word(void* p, unsigned int offset, u32 value) {
    *reinterpret_cast<volatile u32*>(reinterpret_cast<u32>(p) + offset) = value;
}
static unsigned char byte(const void* p, unsigned int offset = 0) {
    return *reinterpret_cast<const volatile unsigned char*>(reinterpret_cast<u32>(p) + offset);
}
static void byte(void* p, unsigned int offset, unsigned char value) {
    *reinterpret_cast<volatile unsigned char*>(reinterpret_cast<u32>(p) + offset) = value;
}
static const char* string(const void* p, unsigned int offset) {
    return reinterpret_cast<const char*>(word(p, offset));
}
static u32 resolve(const char* text) {
    u32 id = good_block_hash(text);
    return good_block_resolve(&id);
}
static void cached_string(void* good, unsigned int offset, const char* text) {
    // Original clears a LOCAL CacheString before allocating, never the old
    // GoodInfo cache handle. Repeated keys alias/overwrite without freeing it.
    u32 temporary;
    good_block_cache_clear(&temporary);
    temporary = reinterpret_cast<u32>(good_block_string_alloc(text, true));
    word(good, offset, temporary);
}
static void addon(INI_Reader* reader, void* good) {
    u32 id = good_block_hash(good_block_indexed_string(reader, 0));
    const char* hp = good_block_string_alloc(good_block_indexed_string(reader, 1), false);
    int count = good_block_int(reader, 2);
    if (count < 1) count = 1;
    char level[64];
    level[0] = 0;
    if (!good_block_is_empty(reader, 3)) {
        const char* value = good_block_indexed_string(reader, 3);
        if (value) {
            // Original scans to NUL BEFORE truncating to 63, including its
            // fault when the source is unterminated at an inaccessible page.
            unsigned int length = 0;
            while (value[length]) ++length;
            unsigned int n = length > 63 ? 63 : length;
            for (unsigned int i = 0; i < n; ++i) level[i] = value[i];
            level[n] = 0;
        }
    }
    u32 arch = good_block_resolve(&id);
    unsigned int head_offset = 0x98;
    if (good_block_stricmp(level, "mid") == 0) head_offset = 0xa4;
    else if (good_block_stricmp(level, "high") == 0) head_offset = 0xb0;
    // Constructor/copy preserve descriptor padding in the allocated node. Do
    // not zero all 40 bytes, nor copy unspecified temporary stack padding.
    unsigned short subobj = good_block_subobj_none();
    u32 bay = good_block_bay_pointer();
    void* head = reinterpret_cast<void*>(word(good, head_offset));
    u32 previous = word(head, 4);
    void* node = good_block_allocate(40);
    word(node, 0, reinterpret_cast<u32>(head));
    if (!previous) previous = reinterpret_cast<u32>(node);
    word(node, 4, previous);
    word(head, 4, reinterpret_cast<u32>(node));
    word(reinterpret_cast<void*>(previous), 0, reinterpret_cast<u32>(node));
    void* descriptor = reinterpret_cast<unsigned char*>(node) + 8;
    byte(descriptor, 0, 0);
    __builtin_memcpy(reinterpret_cast<unsigned char*>(descriptor) + 2, &subobj, 2);
    word(descriptor, 4, 0);
    word(descriptor, 8, bay);
    byte(descriptor, 12, 0);
    word(descriptor, 16, 0x3f800000);
    word(descriptor, 20, 1);
    byte(descriptor, 24, 0);
    word(descriptor, 28, 0);
    word(good, head_offset + 4, word(good, head_offset + 4) + 1);
    // Defined member setters in their observed order.
    word(descriptor, 4, arch);
    word(descriptor, 20, static_cast<u32>(count));
    word(descriptor, 16, 0x3f800000);
    byte(descriptor, 12, 1);
    if (good_block_stricmp(hp, "internal") == 0) word(descriptor, 8, bay);
    else word(descriptor, 8, reinterpret_cast<u32>(hp));
}
extern "C" void __thiscall good_info_read_block(void* list, INI_Reader* reader, void* good) {
    u32 equipment = 0;
    while (good_block_read_value(reader)) {
        if (good_block_is_value(reader, "nickname")) {
            u32 id = good_block_hash(good_block_whole_string(reader));
            if (good_block_find_good(list, id)) return; // No finalization on duplicate.
            word(good, 0x48, id);
        } else if (good_block_is_value(reader, "equipment")) {
            equipment = resolve(good_block_whole_string(reader));
        } else if (good_block_is_value(reader, "free_ammo")) {
            word(good, 0xb8, resolve(good_block_indexed_string(reader, 0)));
            word(good, 0xbc, static_cast<u32>(good_block_int(reader, 1)));
        } else if (good_block_is_value(reader, "ids_name") || good_block_is_value(reader, "name")) {
            word(good, 0x88, static_cast<u32>(good_block_int(reader, 0)));
        } else if (good_block_is_value(reader, "ids_info") || good_block_is_value(reader, "info_desc")) {
            word(good, 0x8c, static_cast<u32>(good_block_int(reader, 0)));
        } else if (good_block_is_value(reader, "category")) {
            const char* value = good_block_whole_string(reader);
            const char* names[] = {"Commodity", "Equipment", "ShipHull", "Ship"};
            unsigned int i = 0;
            for (; i < 4; ++i) {
                if (good_block_stricmp(value, names[i]) == 0) { word(good, 0x4c, i); break; }
            }
            if (i == 4) good_block_unknown_category(good_block_whole_string(reader));
        } else if (good_block_is_value(reader, "ship")) {
            word(good, 0x54, resolve(good_block_whole_string(reader)));
        } else if (good_block_is_value(reader, "price")) {
            good_info_set_price(good, good_block_int(reader, 0));
        } else if (good_block_is_value(reader, "good_buy_price")) {
            good_info_read_price_multiplier(good, reader, 0x5c);
        } else if (good_block_is_value(reader, "bad_buy_price")) {
            good_info_read_price_multiplier(good, reader, 0x60);
        } else if (good_block_is_value(reader, "good_sell_price")) {
            good_info_read_price_multiplier(good, reader, 0x64);
        } else if (good_block_is_value(reader, "bad_sell_price")) {
            good_info_read_price_multiplier(good, reader, 0x68);
        } else if (good_block_is_value(reader, "jump_dist")) {
            word(good, 0x6c, static_cast<u32>(good_block_int(reader, 0)));
        } else if (good_block_is_value(reader, "shop_archetype")) {
            cached_string(good, 0x74, good_block_whole_string(reader));
        } else if (good_block_is_value(reader, "material_library")) {
            cached_string(good, 0x7c, good_block_whole_string(reader));
        } else if (good_block_is_value(reader, "item_icon")) {
            cached_string(good, 0x78, good_block_whole_string(reader));
        } else if (good_block_is_value(reader, "HP_child")) {
            word(good, 0x80, reinterpret_cast<u32>(good_block_string_alloc(good_block_whole_string(reader), false)));
        } else if (good_block_is_value(reader, "attachment_archetype")) {
            cached_string(good, 0x84, good_block_whole_string(reader));
        } else if (good_block_is_value(reader, "hull")) {
            void* hull = good_block_find_hull(good_block_hash(good_block_whole_string(reader)));
            word(good, 0x90, word(hull, 0x48)); // Original unchecked missing reference.
        } else if (good_block_is_value(reader, "addon")) {
            addon(reader, good);
        } else if (good_block_is_value(reader, "combinable")) {
            byte(good, 0x70, good_block_bool(reader, 0));
        } else {
            using ReadUnknown = void (__thiscall *)(void*, INI_Reader*);
            reinterpret_cast<ReadUnknown>(word(reinterpret_cast<void*>(word(good, 0)), 8))(good, reader);
        }
    }
    if (word(good, 0x4c) == 0 || word(good, 0x4c) == 1) {
        word(good, 0x50, equipment);
        void* archetype = good_block_get_equipment(equipment);
        if (!word(good, 0x88)) word(good, 0x88, word(archetype, 0x14));
        if (!word(good, 0x8c)) word(good, 0x8c, word(archetype, 0x18));
        using HasAttachment = unsigned char (__thiscall *)(void*);
        if (reinterpret_cast<HasAttachment>(word(reinterpret_cast<void*>(word(archetype, 0)), 0x24))(archetype)) {
            if (!byte(string(good, 0x84)) && byte(string(archetype, 0x0c))) word(good, 0x84, word(archetype, 0x0c));
            if (!byte(string(good, 0x80)) && byte(string(archetype, 0x80))) word(good, 0x80, word(archetype, 0x80));
        }
    } else word(good, 0x50, 0);
    if (!byte(string(good, 0x74)) && byte(string(good, 0x84))) word(good, 0x74, word(good, 0x84));
}
