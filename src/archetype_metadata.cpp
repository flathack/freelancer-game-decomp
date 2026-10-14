#include "archetype_metadata.hpp"
using byte = unsigned char;
static ArchWord& word(void* p, unsigned int off) { return *reinterpret_cast<ArchWord*>(static_cast<byte*>(p)+off); }
static byte& octet(void* p, unsigned int off) { return *(static_cast<byte*>(p)+off); }
// No C++ binary64 intermediate: arch_float is an ABI-only full-ST0 service.
extern "C" __declspec(naked) void arch_store_float(void*, INI_Reader*, unsigned int) {
    __asm {
        push ebx
        mov ebx, dword ptr [esp+8]
        mov ecx, dword ptr [esp+12]
        push dword ptr [esp+16]
        call arch_float
        fstp dword ptr [ebx]
        pop ebx
        ret
    }
}
static void floating(void* p, unsigned int off, INI_Reader* r, unsigned int index=0) {
    arch_store_float(static_cast<byte*>(p)+off,r,index);
}
struct ObjectType { const char* token; ArchWord value; };
// Pinned independent original table 0x063eb810..0x063eb8f8, in original order.
static const ObjectType types[] = {
    {"NONE",0},{"MOON",1},{"PLANET",2},{"SUN",4},{"ASTEROID",0x20000000},
    {"BLACKHOLE",8},{"SATELLITE",0x10},{"DOCKING_RING",0x20},{"JUMP_GATE",0x40},
    {"JUMP_HOLE",0x800},{"WEAPONS_PLATFORM",0x1000},{"DESTROYABLE_DEPOT",0x2000},
    {"NON_TARGETABLE",0x4000},{"MISSION_SATELLITE",0x8000},{"AIRLOCK_GATE",0x400},
    {"TRADELANE_RING",0x80},{"STATION",0x100},{"WAYPOINT",0x200},
    {"FIGHTER",0x10000},{"FREIGHTER",0x20000},{"GUNBOAT",0x40000},{"CRUISER",0x80000},
    {"TRANSPORT",0x100000},{"CAPITAL",0x200000},{"MINING",0x400000},
    {"GUIDED",0x1000000},{"MINE",0x4000000},{"LOOT",0x10000000},{"BULLET",0x2000000}
};
extern "C" unsigned char __thiscall archetype_root_read(void* self, INI_Reader* r) {
    if (arch_is_value(r,"nickname")) { word(self,0x08)=arch_hash(arch_indexed_string(r,0)); return 1; }
    if (arch_is_value(r,"DA_archetype") || arch_is_value(r,"attachment_archetype")) {
        const char* value=arch_indexed_string(r,0);
        ArchWord temporary;
        arch_cache_clear(&temporary); // only a local; never the previous object handle
        word(self,0x0c)=reinterpret_cast<ArchWord>(arch_string_alloc(value,true));
        return 1;
    }
    if (arch_is_value(r,"type")) {
        const char* value=arch_indexed_string(r,0);
        for (const auto& t: types) if (!arch_stricmp(value,t.token)) { word(self,0x10)=t.value; return 1; }
        arch_diagnostic(0,value,0);
        word(self,0x10)=0; return 1;
    }
    if (arch_is_value(r,"ids_name")) { word(self,0x14)=static_cast<ArchWord>(arch_int(r,0)); return 1; }
    if (arch_is_value(r,"ids_info")) { word(self,0x18)=static_cast<ArchWord>(arch_int(r,0)); return 1; }
    if (arch_is_value(r,"explosion_arch")) { word(self,0x24)=arch_hash(arch_indexed_string(r,0)); return 1; }
    if (arch_is_value(r,"explosion_resistance")) { floating(self,0x28,r); return 1; }
    if (arch_is_value(r,"hit_pts")) { floating(self,0x1c,r); return 1; }
    if (arch_is_value(r,"mass")) { floating(self,0x20,r); return 1; }
    if (arch_is_value(r,"rotation_inertia")) {
        ArchWord temporary[3];
        floating(temporary,0,r,0); floating(temporary,4,r,1); floating(temporary,8,r,2);
        word(self,0x2c)=temporary[0]; word(self,0x30)=temporary[1];
        octet(self,0x38)=1; word(self,0x34)=temporary[2]; return 1;
    }
    if (arch_is_value(r,"phantom_physics")) { octet(self,0x39)=arch_bool(r,0); return 1; }
    if (arch_is_value(r,"mission_property")) return 1;
    void* client=reinterpret_cast<void*>(word(self,4));
    if (!client) return 0;
    using Callback=unsigned char(__thiscall*)(void*,INI_Reader*);
    const auto* slots=*reinterpret_cast<Callback**>(client);
    return slots[2](client,r); // raw AL, unlike successful derived-base paths
}
extern "C" unsigned char __thiscall archetype_equipment_read(void* self, INI_Reader* r) {
    if (archetype_root_read(self,r)) return 1;
    if (arch_is_value(r,"inherit")) {
        const ArchWord id=arch_hash(arch_whole_string(r));
        void* node=arch_inherit_node(id);
        void* source=nullptr;
        if (node==arch_inherit_sentinel()) arch_diagnostic(1,nullptr,id);
        else source=reinterpret_cast<void*>(word(node,0x10));
        if (!source) arch_diagnostic(2,arch_whole_string(r),0);
        else arch_inherit_dispatch(self,source); // explicitly controlled, not recovered copying
        return 1;
    }
    if (arch_is_value(r,"use_count")) { octet(self,0x60)=arch_bool(r,0); return 1; }
    if (arch_is_value(r,"units_per_container")) { word(self,0x64)=static_cast<ArchWord>(arch_int(r,0)); return 1; }
    if (arch_is_value(r,"hit_pts")) { floating(self,0x1c,r); return 1; }
    if (arch_is_value(r,"volume")) { floating(self,0x5c,r); return 1; }
    if (arch_is_value(r,"tractored_explosion")) { word(self,0x68)=arch_hash(arch_whole_string(r)); return 1; }
    if (arch_is_value(r,"lootable")) { octet(self,0x6c)=arch_bool(r,0); return 1; }
    return 0;
}
extern "C" unsigned char __thiscall archetype_attached_read(void* self, INI_Reader* r) {
    if (archetype_equipment_read(self,r)) return 1;
    if (arch_is_value(r,"separation_explosion")) { word(self,0x70)=arch_hash(arch_indexed_string(r,0)); return 1; }
    if (arch_is_value(r,"debris_type")) { word(self,0x74)=arch_hash(arch_indexed_string(r,0)); return 1; }
    if (arch_is_value(r,"child_impulse")) { floating(self,0x78,r); return 1; }
    if (arch_is_value(r,"parent_impulse")) { floating(self,0x7c,r); return 1; }
    if (arch_is_value(r,"HP_child")) { word(self,0x80)=reinterpret_cast<ArchWord>(arch_string_alloc(arch_indexed_string(r,0),false)); return 1; }
    if (arch_is_value(r,"toughness")) { word(self,0x84)=static_cast<ArchWord>(arch_int(r,0)); return 1; }
    return 0;
}
extern "C" unsigned char __thiscall archetype_equipment_is_attached(void*) { return 0; }
extern "C" unsigned char __thiscall archetype_attached_is_attached(void*) { return 1; }
extern "C" const void* const archetype_root_slots[6] = {nullptr,reinterpret_cast<const void*>(archetype_root_read),nullptr,nullptr,nullptr,nullptr};
extern "C" const void* const archetype_equipment_slots[10] = {nullptr,reinterpret_cast<const void*>(archetype_equipment_read),nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,reinterpret_cast<const void*>(archetype_equipment_is_attached)};
extern "C" const void* const archetype_attached_slots[10] = {nullptr,reinterpret_cast<const void*>(archetype_attached_read),nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,nullptr,reinterpret_cast<const void*>(archetype_attached_is_attached)};
