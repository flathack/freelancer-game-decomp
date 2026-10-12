extern "C" void* filemap_runtime_allocate(unsigned int n){using Fn=void*(__cdecl*)(unsigned int);return (*reinterpret_cast<Fn*>(0x6399328))(n);}
extern "C" const char* filemap_runtime_empty_name(){return *reinterpret_cast<const char**>(0x63991d0);}
#include "../../src/file_map.hpp"
extern "C" bool filemap_runtime_string_grow(FileMap* s,unsigned int n,bool trim){using Fn=bool(__thiscall*)(FileMap*,unsigned int,bool);return (*reinterpret_cast<Fn*>(0x63991d4))(s,n,trim);}
extern "C" void filemap_runtime_string_split(FileMap* s){using Fn=void(__thiscall*)(FileMap*);(*reinterpret_cast<Fn*>(0x63991bc))(s);}
extern "C" void filemap_runtime_string_tidy(FileMap* s,bool built){using Fn=void(__thiscall*)(FileMap*,bool);(*reinterpret_cast<Fn*>(0x63991b8))(s,built);}
extern "C" void filemap_runtime_string_assign(FileMap* s,const char* text,unsigned int n){using Fn=FileMap*(__thiscall*)(FileMap*,const char*,unsigned int);(*reinterpret_cast<Fn*>(0x63991a4))(s,text,n);}
extern "C" void filemap_runtime_string_free(void* p){reinterpret_cast<void(__cdecl*)(void*)>(0x6391a7a)(p);}
extern "C" void filemap_runtime_free(void* p){using Fn=void(__cdecl*)(void*);(*reinterpret_cast<Fn*>(0x639932c))(p);}
extern "C" void* filemap_runtime_open_file(const char* name){using Fn=void*(__stdcall*)(const char*,unsigned int,unsigned int,void*,unsigned int,unsigned int,void*);return (*reinterpret_cast<Fn*>(0x63990d4))(name,0x80000000,1,nullptr,3,0,nullptr);}
extern "C" void* filemap_runtime_create_mapping(void* file){using Fn=void*(__stdcall*)(void*,void*,unsigned int,unsigned int,unsigned int,const char*);return (*reinterpret_cast<Fn*>(0x6399144))(file,nullptr,2,0,0,nullptr);}
extern "C" unsigned int filemap_runtime_file_size(void* file){using Fn=unsigned int(__stdcall*)(void*,unsigned int*);return (*reinterpret_cast<Fn*>(0x639913c))(file,nullptr);}
extern "C" void* filemap_runtime_map_view(void* mapping,unsigned int n){using Fn=void*(__stdcall*)(void*,unsigned int,unsigned int,unsigned int,unsigned int);return (*reinterpret_cast<Fn*>(0x6399138))(mapping,4,0,0,n);}
extern "C" void filemap_runtime_unmap(void* data){using Fn=int(__stdcall*)(void*);(*reinterpret_cast<Fn*>(0x6399130))(data);}
extern "C" void filemap_runtime_close_handle(void* handle){using Fn=int(__stdcall*)(void*);(*reinterpret_cast<Fn*>(0x6399140))(handle);}
