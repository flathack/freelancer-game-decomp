extern "C" void* good_info_runtime_allocate(unsigned n) {return reinterpret_cast<void* (__cdecl*)(unsigned)>(0x06391abc)(n);}
extern "C" void good_info_runtime_free(void* p) {reinterpret_cast<void (__cdecl*)(void*)>(0x06391a7a)(p);}
