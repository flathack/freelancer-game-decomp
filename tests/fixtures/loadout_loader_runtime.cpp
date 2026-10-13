#include "../../src/equip_desc.hpp"
// Same default field initialization already reconstructed in src/equip_desc.cpp;
// only the constructor is needed in this integration fixture.
EquipDesc::EquipDesc():unknown_00(0),id(0),arch_id(0),hardpoint(CARGO_BAY_HP_NAME),equipped(false),status(1.f),count(1),temporary(false),owner(0){}
extern "C" void loadout_runtime_file_error(const char* filename){
 using Fn=void(__cdecl*)(unsigned int,const char*,const char*,unsigned int,const char*);
 (**reinterpret_cast<Fn**>(0x6399028))(0x100001,"%s(%d) : *** ERROR: unable to open Loadout file %s","E:\\FL\\Scratch\\Source\\Common\\Loadout.cpp",0xb3,filename);
}
extern "C" int equip_collection_compare(const char* a,const char* b){using Fn=int(__cdecl*)(const char*,const char*);return (*reinterpret_cast<Fn*>(0x639902c))(a,b);}
// Emulator-only stack probe binding; the reconstructed DLL still needs real CRT.
extern "C" __declspec(naked) void _chkstk(){
 __asm {mov edx,06391ae0h
        jmp edx}
}
