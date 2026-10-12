#include "ini_reader.hpp"
#include "equip_desc.hpp"
extern "C" const char* loadout_value_string(INI_Reader*,unsigned int);
extern "C" bool loadout_value_empty(INI_Reader*,unsigned int);
extern "C" double loadout_value_float(INI_Reader*,unsigned int);
extern "C" int loadout_value_int(INI_Reader*,unsigned int);
extern "C" unsigned char loadout_value_bool(INI_Reader*,unsigned int);
extern "C" int loadout_atoi(const char*);
extern "C" double loadout_atof(const char*);
extern "C" unsigned int loadout_create_id(const char*);
namespace Loadout {
bool ReadEquipLine(INI_Reader& reader,EquipDesc& item) {
    item.equipped=true;item.count=1;
    unsigned int id=loadout_atoi(loadout_value_string(&reader,0));
    if(!id)id=loadout_create_id(loadout_value_string(&reader,0));
    item.arch_id=id;
    if(loadout_value_empty(&reader,1))item.hardpoint=EquipDesc::CARGO_BAY_HP_NAME;
    else item.hardpoint.value=StringAlloc(loadout_value_string(&reader,1),false);
    if(!loadout_value_empty(&reader,2))item.status=static_cast<float>(loadout_value_float(&reader,2));
    return true;
}
bool ReadCargoLine(INI_Reader& reader,EquipDesc& item) {
    item.equipped=false;
    unsigned int id=loadout_atoi(loadout_value_string(&reader,0));
    if(!id)id=loadout_create_id(loadout_value_string(&reader,0));
    item.arch_id=id;
    if(!loadout_value_empty(&reader,1))item.count=loadout_value_int(&reader,1);
    if(loadout_value_empty(&reader,2))item.hardpoint=EquipDesc::CARGO_BAY_HP_NAME;
    else {
        if(loadout_atof(loadout_value_string(&reader,2))!=0.0)return true;
        item.hardpoint.value=StringAlloc(loadout_value_string(&reader,2),false);
    }
    if(!loadout_value_empty(&reader,3))item.status=static_cast<float>(loadout_value_float(&reader,3));
    if(!loadout_value_empty(&reader,4))reinterpret_cast<unsigned char*>(&item)[24]=loadout_value_bool(&reader,4);
    return true;
}
}
