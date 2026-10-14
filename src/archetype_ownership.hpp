#pragma once
#include "archetype_metadata.hpp"
using ArchDestructor = void(__thiscall*)(void*);
extern "C" void* arch_runtime_allocate(unsigned int);
extern "C" void arch_runtime_free(void*);
extern "C" void arch_runtime_payload_heap_free(void*);
extern "C" void __stdcall arch_runtime_array_destroy(void*, unsigned int, unsigned int, ArchDestructor);
extern "C" void* __thiscall archetype_root_default(void*, void* client);
extern "C" void* __thiscall archetype_equipment_default(void*, void* client);
extern "C" void* __thiscall archetype_attached_default(void*, void* client);
extern "C" void* __thiscall archetype_root_copy(void*, const void*);
extern "C" void* __thiscall archetype_equipment_copy(void*, const void*);
extern "C" void* __thiscall archetype_attached_copy(void*, const void*);
extern "C" void* __thiscall archetype_root_assign(void*, const void*);
extern "C" void* __thiscall archetype_equipment_assign(void*, const void*);
extern "C" void* __thiscall archetype_attached_assign(void*, const void*);
extern "C" void* __thiscall archetype_assign_0626eaf0(void*, const void*);
extern "C" void* __thiscall archetype_assign_0626dbb0(void*, const void*);
extern "C" void* __thiscall archetype_assign_0626e2c0(void*, const void*);
extern "C" void* __thiscall archetype_assign_0626f660(void*, const void*);
extern "C" void* __thiscall archetype_assign_0626f870(void*, const void*);
extern "C" void* __thiscall archetype_assign_0626fa10(void*, const void*);
extern "C" void* __thiscall archetype_pointer_vector_assign(void*, const void*);
extern "C" void __thiscall archetype_root_destroy(void*);
extern "C" void* __thiscall archetype_root_deleting(void*, unsigned int);
extern "C" void* __thiscall archetype_equipment_deleting(void*, unsigned int);
extern "C" void* __thiscall archetype_attached_deleting(void*, unsigned int);
// Recovered lifetime/class/read slots only. Other physical/load methods stay null.
extern "C" const void* const archetype_lifetime_root_slots[6];
extern "C" const void* const archetype_lifetime_equipment_slots[10];
extern "C" const void* const archetype_lifetime_attached_slots[10];
