#include "../../src/ini_reader_strings.hpp"
#include "../../src/equip_desc.hpp"
const CacheString EquipDesc::CARGO_BAY_HP_NAME={reinterpret_cast<const char*>(0x20507000)};
extern "C" const char* loadout_value_string(INI_Reader* r,unsigned int i){return ini_value_string(r,i);}
extern "C" bool loadout_value_empty(INI_Reader* r,unsigned int i){return r->is_value_empty(i);}
extern "C" double loadout_value_float(INI_Reader* r,unsigned int i){return ini_value_float(r,i);}
extern "C" int loadout_value_int(INI_Reader* r,unsigned int i){return ini_value_int(r,i);}
extern "C" unsigned char loadout_value_bool(INI_Reader* r,unsigned int i){return ini_value_bool(r,i);}
extern "C" int loadout_atoi(const char* s){return ini_values_atoi(s);}
extern "C" double loadout_atof(const char* s){return ini_values_atof(s);}
extern "C" unsigned int loadout_create_id(const char* s){return reinterpret_cast<unsigned int(__cdecl*)(const char*)>(0x630d470)(s);}
char* StringAlloc(const char* s,bool p){return reinterpret_cast<char*(__cdecl*)(const char*,bool)>(0x6333bd0)(s,p);}
