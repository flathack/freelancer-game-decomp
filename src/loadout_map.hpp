#pragma once
#include "equip_desc.hpp"
#include "subobject_id.hpp"
namespace Loadout {
struct Map {
 unsigned int id;
 unsigned char allocator[4];
 EquipDesc *begin,*end,*capacity;
 SubObjectID::EquipIdMaker ids;
 unsigned char padding_16[2];
 Map();
 Map(const Map&);
 Map& operator=(const Map&);
 ~Map();
};
#if __SIZEOF_POINTER__==4
static_assert(sizeof(Map)==24 && __builtin_offsetof(Map,ids)==20,"Observed Loadout Map extent/ID offset");
#endif
}
extern "C" void* loadout_map_allocate(unsigned int);
extern "C" void loadout_map_free(void*);
