extern "C" void good_info_runtime_free(void* p) {
    reinterpret_cast<void (__cdecl*)(void*)>(0x06391a7a)(p);
}
extern "C" unsigned good_info_runtime_vtable(bool) { return 0x063993e8; }
