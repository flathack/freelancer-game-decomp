#include "equip_desc_collections.hpp"
EquipDesc* EquipDescVector::traverse_equipment_type(unsigned int arch,const EquipDesc* previous){
 for(EquipDesc* item=begin;item!=end;++item)if(item->arch_id==arch){if(!previous)return item;if(item==previous)previous=nullptr;}
 return nullptr;
}
static EquipDesc* traverse(const EquipDescList* list,unsigned int arch,const EquipDesc* previous){
 for(auto* node=list->head->next;node!=list->head;node=node->next)if(node->value.arch_id==arch){if(!previous)return &node->value;if(&node->value==previous)previous=nullptr;}
 return nullptr;
}
EquipDesc* EquipDescList::traverse_equipment_type(unsigned int arch,const EquipDesc* previous){return traverse(this,arch,previous);}
const EquipDesc* EquipDescList::traverse_equipment_type(unsigned int arch,const EquipDesc* previous) const{return traverse(this,arch,previous);}
static EquipDesc* find_id(const EquipDescList* list,unsigned short id){
 for(auto* node=list->head->next;node!=list->head;node=node->next)if(node->value.id==id)return &node->value;
 return nullptr;
}
EquipDesc* EquipDescList::find_equipment_item(unsigned short id){return find_id(this,id);}
const EquipDesc* EquipDescList::find_equipment_item(unsigned short id) const{return find_id(this,id);}
