extern "C" void* good_info_runtime_allocate(unsigned n) {return reinterpret_cast<void* (__cdecl*)(unsigned)>(0x06391abc)(n);}
extern "C" void good_info_runtime_free(void* p) {reinterpret_cast<void (__cdecl*)(void*)>(0x06391a7a)(p);}
extern "C" unsigned good_info_runtime_vtable(bool final) {return final?0x063993e8:0x063993d8;}
