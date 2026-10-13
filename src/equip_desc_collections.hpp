#pragma once
#include "equip_desc.hpp"
struct EquipDescVector {
 unsigned char allocator[4];EquipDesc *begin,*end,*capacity;
 int add_equipment_item(const EquipDesc&,bool);
 EquipDesc* traverse_equipment_type(unsigned int,const EquipDesc*);
};
class EquipDescList {
public:
 struct Node {Node *next,*previous;EquipDesc value;};
 unsigned char allocator[4];Node* head;unsigned int size;
 EquipDesc* traverse_equipment_type(unsigned int,const EquipDesc*);
 const EquipDesc* traverse_equipment_type(unsigned int,const EquipDesc*) const;
 EquipDesc* find_equipment_item(unsigned short);
 const EquipDesc* find_equipment_item(unsigned short) const;
};
#if __SIZEOF_POINTER__==4
static_assert(sizeof(EquipDescVector)==16 && sizeof(EquipDescList)==12 && sizeof(EquipDescList::Node)==40,"Observed collection layouts");
#endif
