#include "../../src/string_index.hpp"
extern "C" int ini_runtime_compare(const char* a,const char* b){using Fn=int(__cdecl*)(const char*,const char*);return (*reinterpret_cast<Fn*>(0x639902c))(a,b);}
extern "C" const char* ini_runtime_string_index(const char* text,unsigned int n){return StringIndex(text,n);}
