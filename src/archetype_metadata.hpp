#pragma once
// P2 storage views only; no production constructors, database or lifetime claim.
using ArchWord = unsigned int;
struct INI_Reader;
struct ArchRootView {
    ArchWord vptr, client, nickname, archetype, type, ids_name, ids_info;
    float hit_pts, mass;
    ArchWord explosion_arch;
    float explosion_resistance, rotation_inertia[3];
    unsigned char inertia_present, phantom_physics, opaque_3a[0x22];
};
struct ArchEquipmentView {
    ArchRootView root;
    float volume;
    unsigned char use_count, padding_61[3];
    ArchWord units_per_container, tractored_explosion;
    unsigned char lootable, padding_6d[3];
};
struct ArchAttachedView {
    ArchEquipmentView equipment;
    ArchWord separation_explosion, debris_type;
    float child_impulse, parent_impulse;
    ArchWord hp_child, toughness;
};
static_assert(sizeof(ArchRootView)==0x5c && sizeof(ArchEquipmentView)==0x70 && sizeof(ArchAttachedView)==0x88, "original strides");
static_assert(__builtin_offsetof(ArchRootView, ids_name)==0x14 && __builtin_offsetof(ArchRootView, phantom_physics)==0x39, "root fields");
static_assert(__builtin_offsetof(ArchEquipmentView, use_count)==0x60 && __builtin_offsetof(ArchAttachedView, hp_child)==0x80, "derived fields");
extern "C" unsigned char __thiscall archetype_root_read(void*, INI_Reader*);
extern "C" unsigned char __thiscall archetype_equipment_read(void*, INI_Reader*);
extern "C" unsigned char __thiscall archetype_attached_read(void*, INI_Reader*);
extern "C" unsigned char __thiscall archetype_equipment_is_attached(void*);
extern "C" unsigned char __thiscall archetype_attached_is_attached(void*);
// Partial slot bindings. Null slots are deliberately NOT recovered methods.
extern "C" const void* const archetype_root_slots[6];
extern "C" const void* const archetype_equipment_slots[10];
extern "C" const void* const archetype_attached_slots[10];
// Required service boundary; integration supplies implementations.
extern "C" unsigned char __thiscall arch_is_value(INI_Reader*, const char*);
extern "C" const char* __thiscall arch_indexed_string(INI_Reader*, unsigned int);
extern "C" const char* __thiscall arch_whole_string(INI_Reader*);
extern "C" int __thiscall arch_int(INI_Reader*, unsigned int);
extern "C" unsigned char __thiscall arch_bool(INI_Reader*, unsigned int);
// ABI returns full ST0. Reader assembly stores directly to binary32.
extern "C" double __thiscall arch_float(INI_Reader*, unsigned int);
extern "C" ArchWord arch_hash(const char*);
extern "C" void __thiscall arch_cache_clear(ArchWord*);
extern "C" const char* arch_string_alloc(const char*, bool private_copy);
extern "C" int arch_stricmp(const char*, const char*);
extern "C" void* arch_inherit_node(ArchWord);
extern "C" void* arch_inherit_sentinel();
extern "C" void arch_inherit_dispatch(void* target, void* source);
// kind 0=unknown type, 1=ArchDB missing, 2=inherit warning.
extern "C" void arch_diagnostic(unsigned int kind, const char* text, ArchWord id);
