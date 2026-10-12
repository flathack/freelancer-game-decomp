extern "C" int ini_values_atoi(const char* s){using Fn=int(__cdecl*)(const char*);return (*reinterpret_cast<Fn*>(0x6399248))(s);}
extern "C" __declspec(naked) int ini_values_float_to_int(float){
    __asm{fld dword ptr [esp+4]
          mov eax,dword ptr [06399320h]
          jmp eax}
}
extern "C" void ini_values_missing_parameter(const char* header,const char* value,unsigned int index){
    char buffer[256];using Format=int(__cdecl*)(char*,const char*,...);
    (*reinterpret_cast<Format*>(0x639931c))(buffer,"header [%s] value %s missing parameter %u",header,value,index);
    using Message=int(__stdcall*)(void*,const char*,const char*,unsigned int);
    (*reinterpret_cast<Message*>(0x6399378))(nullptr,buffer,"ERROR",0);
}
extern "C" void ini_values_invalid_text_bool(const char*,const char*){__builtin_trap();}
extern "C" {int _fltused=0;}
