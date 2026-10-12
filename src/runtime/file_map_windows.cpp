// Real external imports for a Windows x86 build. No original-image VA bindings.
#include "../file_map.hpp"
#define IMP __declspec(dllimport)
extern "C" IMP void* __cdecl malloc(unsigned int);
extern "C" IMP void __cdecl free(void*);
extern "C" IMP bool __thiscall msvc_grow(FileMap*,unsigned int,bool)
 __asm__("?_Grow@?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@AAE_NI_N@Z");
extern "C" IMP void __thiscall msvc_split(FileMap*)
 __asm__("?_Split@?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@AAEXXZ");
extern "C" IMP void __thiscall msvc_tidy(FileMap*,bool)
 __asm__("?_Tidy@?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@AAEX_N@Z");
extern "C" IMP FileMap* __thiscall msvc_assign(FileMap*,const char*,unsigned int)
 __asm__("?assign@?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@QAEAAV12@PBDI@Z");
extern "C" IMP const char msvc_empty_name
 __asm__("?_C@?1??_Nullstr@?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@CAPBDXZ@4DB");
extern "C" IMP void* __stdcall win_create_file(const char*,unsigned int,unsigned int,void*,unsigned int,unsigned int,void*) __asm__("_CreateFileA");
extern "C" IMP void* __stdcall win_create_mapping(void*,void*,unsigned int,unsigned int,unsigned int,const char*) __asm__("_CreateFileMappingA");
extern "C" IMP unsigned int __stdcall win_file_size(void*,unsigned int*) __asm__("_GetFileSize");
extern "C" IMP void* __stdcall win_map_view(void*,unsigned int,unsigned int,unsigned int,unsigned int) __asm__("_MapViewOfFile");
extern "C" IMP int __stdcall win_unmap(void*) __asm__("_UnmapViewOfFile");
extern "C" IMP int __stdcall win_close_handle(void*) __asm__("_CloseHandle");
extern "C" void* filemap_runtime_allocate(unsigned int n){return malloc(n);}
extern "C" void filemap_runtime_free(void* p){free(p);}
extern "C" void filemap_runtime_string_free(void* p){free(p);}
extern "C" const char* filemap_runtime_empty_name(){return &msvc_empty_name;}
extern "C" bool filemap_runtime_string_grow(FileMap* s,unsigned int n,bool trim){return msvc_grow(s,n,trim);}
extern "C" void filemap_runtime_string_split(FileMap* s){msvc_split(s);}
extern "C" void filemap_runtime_string_tidy(FileMap* s,bool built){msvc_tidy(s,built);}
extern "C" void filemap_runtime_string_assign(FileMap* s,const char* text,unsigned int n){msvc_assign(s,text,n);}
extern "C" void* filemap_runtime_open_file(const char* name){return win_create_file(name,0x80000000,1,nullptr,3,0,nullptr);}
extern "C" void* filemap_runtime_create_mapping(void* file){return win_create_mapping(file,nullptr,2,0,0,nullptr);}
extern "C" unsigned int filemap_runtime_file_size(void* file){return win_file_size(file,nullptr);}
extern "C" void* filemap_runtime_map_view(void* mapping,unsigned int n){return win_map_view(mapping,4,0,0,n);}
extern "C" void filemap_runtime_unmap(void* p){win_unmap(p);}
extern "C" void filemap_runtime_close_handle(void* p){win_close_handle(p);}
