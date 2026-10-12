extern "C" void* stringcache_runtime_allocate(__SIZE_TYPE__ bytes){return reinterpret_cast<void*(__cdecl*)(__SIZE_TYPE__)>(0x06391abc)(bytes);}
extern "C" int stringcache_runtime_compare(const char* a,const char* b){using Fn=int(__cdecl*)(const char*,const char*);return (*reinterpret_cast<Fn*>(0x0639902c))(a,b);}
extern "C" void stringcache_runtime_overflow(unsigned int line){reinterpret_cast<void(__cdecl*)(unsigned int)>(0x20400030)(line);}
extern "C" void stringcache_runtime_free(void* ptr){reinterpret_cast<void(__cdecl*)(void*)>(0x06391a7a)(ptr);}
