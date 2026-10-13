#include "loadout_tree.hpp"
#include "loadout_map.hpp"
#include "equip_desc_collections.hpp"
#include "ini_reader_strings.hpp"
struct LoadoutPair {unsigned int key;Loadout::Map value;};
struct LoadoutInsertResult {Loadout::LookupNode* node;unsigned char inserted;};
extern "C" void __thiscall loadout_tree_emplace(Loadout::LookupTree*,LoadoutInsertResult*,const LoadoutPair*);
extern unsigned int CreateID(const char*);
extern "C" unsigned char arch_is_combinable_raw(unsigned int) __asm__("?arch_is_combinable@@YA_NI@Z");
extern "C" void loadout_runtime_file_error(const char*);
namespace Loadout {
bool ReadEquipLine(INI_Reader&,EquipDesc&);
bool ReadCargoLine(INI_Reader&,EquipDesc&);
int Load(const char* name,bool){
 unsigned int before=LoadoutLookupTree.size;
 INI_Reader reader;
 if(!reader.open(name,false))loadout_runtime_file_error(name);
 else while(reader.read_header()){
  if(!reader.is_header("Loadout"))continue;
  Map* current=nullptr;
  while(reader.read_value()){
   if(reader.is_value("nickname")){
    if(!current){
     Map initial;LoadoutPair temporary{CreateID(ini_value_string_all(&reader)),initial};
     LoadoutInsertResult result;loadout_tree_emplace(&LoadoutLookupTree,&result,&temporary);
     current=reinterpret_cast<Map*>(reinterpret_cast<unsigned char*>(result.node)+16);current->id=temporary.key;
     if(!result.inserted){current->end=current->begin;current->ids.Reset();}
    }
   }else if(reader.is_value("equip")){
    EquipDesc item;
    auto* vector=reinterpret_cast<EquipDescVector*>(reinterpret_cast<unsigned char*>(current)+4);
    vector->add_equipment_item(item,false);
    ReadEquipLine(reader,current->end[-1]);current->end[-1].id=current->ids.CreateEquipID();
   }else if(reader.is_value("cargo")){
    EquipDesc item;ReadCargoLine(reader,item);
    bool combine=arch_is_combinable_raw(item.arch_id)!=0;
    if(item.hardpoint.value!=EquipDesc::CARGO_BAY_HP_NAME.value)combine=false;
    auto* vector=reinterpret_cast<EquipDescVector*>(reinterpret_cast<unsigned char*>(current)+4);
    if(!vector->add_equipment_item(item,combine))current->end[-1].id=current->ids.CreateEquipID();
   }else reader.is_value("archetype");
  }
 }
 return static_cast<int>(LoadoutLookupTree.size-before);
}
}
