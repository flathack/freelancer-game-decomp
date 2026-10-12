#include "../../src/ini_reader.hpp"
#include "../../src/equip_desc.hpp"
const CacheString EquipDesc::CARGO_BAY_HP_NAME={reinterpret_cast<const char*>(0x20507000)};
extern "C" const char* loadout_value_string(INI_Reader* r,unsigned int i){return reinterpret_cast<const char*(__thiscall*)(INI_Reader*,unsigned int)>(0x6310ac0)(r,i);}
extern "C" bool loadout_value_empty(INI_Reader* r,unsigned int i){return reinterpret_cast<bool(__thiscall*)(INI_Reader*,unsigned int)>(0x63105f0)(r,i);}
extern "C" double loadout_value_float(INI_Reader* r,unsigned int i){return reinterpret_cast<double(__thiscall*)(INI_Reader*,unsigned int)>(0x6310980)(r,i);}
extern "C" int loadout_value_int(INI_Reader* r,unsigned int i){return reinterpret_cast<int(__thiscall*)(INI_Reader*,unsigned int)>(0x6310850)(r,i);}
extern "C" unsigned char loadout_value_bool(INI_Reader* r,unsigned int i){return reinterpret_cast<unsigned char(__thiscall*)(INI_Reader*,unsigned int)>(0x6310640)(r,i);}
extern "C" int loadout_atoi(const char* s){using F=int(__cdecl*)(const char*);return (*reinterpret_cast<F*>(0x6399248))(s);}
extern "C" double loadout_atof(const char* s){using F=double(__cdecl*)(const char*);return (*reinterpret_cast<F*>(0x63992f0))(s);}
extern "C" unsigned int loadout_create_id(const char* s){return reinterpret_cast<unsigned int(__cdecl*)(const char*)>(0x630d470)(s);}
char* StringAlloc(const char* s,bool p){return reinterpret_cast<char*(__cdecl*)(const char*,bool)>(0x6333bd0)(s,p);}
extern "C" { int _fltused=0; }
