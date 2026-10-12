#pragma once
using FLIDUInt = unsigned int;
static_assert(sizeof(FLIDUInt)==4,"32-bit words required");

// Field offsets observed in common.dll, including two uninitialized padding bytes.
struct FLIDCRCState {
    FLIDUInt table[256];
    FLIDUInt storage_bits;
    FLIDUInt width;
    FLIDUInt polynomial;
    FLIDUInt initial;
    FLIDUInt final_xor;
    unsigned char reflected;
    unsigned char direct;
    unsigned char padding[2];
    FLIDUInt remainder;
    void Update(unsigned char byte);
};
static_assert(sizeof(FLIDCRCState)==0x41c,"Observed allocation size");
static_assert(__builtin_offsetof(FLIDCRCState,remainder)==0x418,"Observed remainder offset");

class CFLIDMaker {
    FLIDCRCState* state;
    FLIDUInt next_object_id;
protected:
    CFLIDMaker();
    ~CFLIDMaker();
public:
    static CFLIDMaker* m_pTheMaker;
    static CFLIDMaker* GetInstance();
    static void Shutdown();
    int Initialize();
    FLIDUInt CreateStaticID(const char*);
    FLIDUInt AllocateObjectID();
    CFLIDMaker& operator=(const CFLIDMaker&);
#ifdef FLID_TESTING
    friend const FLIDCRCState* flid_test_state();
    friend void flid_test_set_counter(FLIDUInt);
#endif
};
#if __SIZEOF_POINTER__ == 4
static_assert(sizeof(CFLIDMaker)==8,"Observed x86 object allocation size");
#endif

// Runtime imports still need binding to the original CRT and logging interfaces.
extern "C" void* flid_runtime_allocate(__SIZE_TYPE__ bytes);
extern "C" void flid_runtime_free(void*);
extern "C" char* flid_runtime_strlwr(char*);
extern "C" void flid_runtime_allocation_failure();
