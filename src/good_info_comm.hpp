#pragma once
struct INI_Reader;
// GoodInfo's CommReferrable subobject begins at offset zero. Slot +4 returns
// the counted-string storage (+4), NOT the first character (+8).
extern "C" unsigned char __thiscall good_info_has_voice(void*);
extern "C" void* __thiscall good_info_prefix_ref(void*);
extern "C" unsigned char __thiscall good_info_read_comm(void*, INI_Reader*);
extern "C" const void* const good_info_comm_slots[3];
extern "C" const void* const good_info_comm_base_slots[3];
// Production binding for the already reconstructed GoodInfo constructor's
// existing runtime-vtable dependency; separate base/derived table identities.
extern "C" unsigned int good_info_runtime_vtable(bool derived);
// Explicit reader leaf bindings, shared with the already reconstructed P2.
extern "C" unsigned char __thiscall arch_is_value(INI_Reader*, const char*);
extern "C" const char* __thiscall arch_whole_string(INI_Reader*);
