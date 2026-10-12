// Host-side substitutes for original runtime imports, confined to tests.
#include <cstdlib>
extern "C" void* flid_runtime_allocate(__SIZE_TYPE__ bytes) { return std::malloc(bytes); }
extern "C" void flid_runtime_free(void* p) { std::free(p); }
extern "C" char* flid_runtime_strlwr(char* p) {
    for(char* i=p;*i;++i) if(*i>='A' && *i<='Z') *i+=32;
    return p;
}
extern "C" void flid_runtime_allocation_failure() { std::abort(); }
