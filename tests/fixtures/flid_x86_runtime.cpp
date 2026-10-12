// Emulator-only binding to this SHA-pinned common.dll image. Not a production runtime.
extern "C" void* flid_runtime_allocate(__SIZE_TYPE__ bytes) {
    using Fn=void*(__cdecl*)(__SIZE_TYPE__);
    return reinterpret_cast<Fn>(0x06391abc)(bytes);
}
extern "C" void flid_runtime_free(void* ptr) {
    using Fn=void(__cdecl*)(void*);
    reinterpret_cast<Fn>(0x06391a7a)(ptr);
}
extern "C" char* flid_runtime_strlwr(char* ptr) {
    using Fn=char*(__cdecl*)(char*);
    return (*reinterpret_cast<Fn*>(0x06399350))(ptr);
}
extern "C" void flid_runtime_allocation_failure() {
    // Unused in success-domain tests. The original logging interface is unresolved.
    __builtin_trap();
}
