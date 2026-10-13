#define LOADOUT_REAL_BAY
#define StringAlloc loadout_unused_original_StringAlloc
#include "loadout_reader_hash_runtime.cpp"
#undef StringAlloc

#undef LOADOUT_REAL_BAY
char* StringAlloc(const char*,bool);
const CacheString EquipDesc::CARGO_BAY_HP_NAME={StringAlloc("BAY",false)};
