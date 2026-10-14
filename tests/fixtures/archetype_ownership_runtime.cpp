#include "../../src/archetype_ownership.hpp"
extern char StringCacheArena[0x180000];
// Constructor leaf services only. Its vtable binding is the production body
// in good_info_comm.cpp, not an original-address or fixed-return fixture.
extern "C" void* good_info_runtime_allocate(unsigned int n) { return arch_runtime_allocate(n); }
extern "C" unsigned int good_info_runtime_empty_cache() { return reinterpret_cast<unsigned int>(StringCacheArena); }
// Allocator, external header allocation release and native CRT iteration are
// explicit runtime boundaries. Only the array iterator is modeled in C++.
extern "C" __declspec(naked) void* arch_runtime_allocate(unsigned int) {
    __asm { int 3 }
    __asm { ret }
}
extern "C" __declspec(naked) void arch_runtime_free(void*) {
    __asm { int 3 }
    __asm { ret }
}
extern "C" __declspec(naked) void arch_runtime_payload_heap_free(void*) {
    __asm { int 3 }
    __asm { ret }
}
extern "C" void __stdcall arch_runtime_array_destroy(void* p, unsigned int stride, unsigned int count, ArchDestructor destroy) {
    auto* first=static_cast<unsigned char*>(p);
    while (count) { --count; destroy(first+stride*count); }
}
