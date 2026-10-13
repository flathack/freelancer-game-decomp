#pragma once
namespace SubObjectID {
#define ID_MAKER(Name,Method) \
class Name {public: unsigned short next_id; Name(); void Reset(); unsigned short Method(); Name& operator=(const Name&);};
ID_MAKER(EquipIdMaker,CreateEquipID)
ID_MAKER(CollGroupIdMaker,CreateGroupID)
ID_MAKER(ShieldIdMaker,CreateShieldID)
#undef ID_MAKER
static_assert(sizeof(EquipIdMaker)==2 && sizeof(CollGroupIdMaker)==2 && sizeof(ShieldIdMaker)==2,"Observed 16-bit counter extent");
}
