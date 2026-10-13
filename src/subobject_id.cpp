#include "subobject_id.hpp"
namespace SubObjectID {
#define DEFINE_ID_MAKER(Name,Method,Initial) \
Name::Name():next_id(Initial) {} \
void Name::Reset(){next_id=Initial;} \
unsigned short Name::Method(){next_id=static_cast<unsigned short>(next_id+1);return next_id;} \
Name& Name::operator=(const Name& other){next_id=other.next_id;return *this;}
DEFINE_ID_MAKER(EquipIdMaker,CreateEquipID,0x21)
DEFINE_ID_MAKER(CollGroupIdMaker,CreateGroupID,3)
DEFINE_ID_MAKER(ShieldIdMaker,CreateShieldID,0xfff0)
#undef DEFINE_ID_MAKER
}
