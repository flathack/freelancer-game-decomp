// CFLIDMaker reconstructed from common.dll exports and instructions.
// Behavior and layouts are tested separately from machine-code matching.
#include "cfl_id_maker.hpp"
inline void* operator new(__SIZE_TYPE__,void* storage) noexcept { return storage; }

CFLIDMaker* CFLIDMaker::m_pTheMaker = nullptr;
CFLIDMaker::CFLIDMaker() : state(nullptr), next_object_id(1) {}
CFLIDMaker::~CFLIDMaker() { if(state) flid_runtime_free(state); }
CFLIDMaker& CFLIDMaker::operator=(const CFLIDMaker& other) {
    // Observed shallow assignment; not changed to deep copy.
    state=other.state;
    next_object_id=other.next_object_id;
    return *this;
}
CFLIDMaker* CFLIDMaker::GetInstance() {
    if(!m_pTheMaker) {
        void* storage=flid_runtime_allocate(sizeof(CFLIDMaker));
        m_pTheMaker=storage ? new(storage) CFLIDMaker : nullptr;
    }
    return m_pTheMaker;
}
void CFLIDMaker::Shutdown() {
    if(m_pTheMaker) {
        m_pTheMaker->~CFLIDMaker();
        flid_runtime_free(m_pTheMaker);
    }
    m_pTheMaker=nullptr;
}
FLIDUInt CFLIDMaker::AllocateObjectID() { return next_object_id++ & 0x3fffffffu; }

int CFLIDMaker::Initialize() {
    if(state) return 1;
    FLIDCRCState* crc=static_cast<FLIDCRCState*>(flid_runtime_allocate(sizeof(FLIDCRCState)));
    if(!crc) { state=nullptr; return 0; }
    crc->storage_bits=32; crc->width=30; crc->polynomial=0x8005;
    crc->initial=0; crc->final_xor=0; crc->reflected=1; crc->direct=1; crc->remainder=0;
    for(FLIDUInt i=0;i<256;++i) {
        FLIDUInt value=i;
        if(crc->reflected) {
            FLIDUInt input=value;
            for(unsigned bit=0;bit<8;++bit) {
                FLIDUInt mask=1u<<(7-bit);
                value=(input&1) ? value|mask : value&~mask;
                input>>=1;
            }
        }
        FLIDUInt top=1u<<((crc->width-1)&31);
        value<<=(crc->width-8)&31;
        for(unsigned bit=0;bit<8;++bit)
            value=(value&top) ? (value<<1)^crc->polynomial : value<<1;
        if(crc->reflected) {
            FLIDUInt input=value;
            for(unsigned bit=0;bit<crc->width;++bit) {
                FLIDUInt mask=1u<<((crc->width-bit-1)&31);
                value=(input&1) ? value|mask : value&~mask;
                input>>=1;
            }
        }
        crc->table[i]=value & ((top*2-1)|1);
    }
    state=crc;
    return state!=nullptr;
}
void FLIDCRCState::Update(unsigned char byte) {
    if(reflected) {
        if(direct) remainder=table[(remainder&255)^byte]^(remainder>>8);
        else remainder=(FLIDUInt(byte)<<((width-8)&31))^table[remainder&255]^(remainder>>8);
    } else {
        FLIDUInt index=(remainder>>((width-8)&31))&255;
        if(direct) remainder=table[index^byte]^(remainder<<8);
        else remainder=table[index]^(remainder<<8)^byte;
    }
}
FLIDUInt CFLIDMaker::CreateStaticID(const char* name) {
    if(!state) Initialize();
    if(!name) return 0;
    char buffer[256];
    unsigned length=0;
    // Preserve the original copy and 256-byte buffer; inputs >255 are unverified.
    do { buffer[length]=name[length]; } while(name[length++]);
    --length;
    flid_runtime_strlwr(buffer);
    state->remainder=state->initial;
    for(unsigned i=0;i<length;++i) state->Update(static_cast<unsigned char>(buffer[i]));
    FLIDUInt top=1u<<((state->width-1)&31);
    FLIDUInt result=(state->remainder^state->final_xor)&((top*2-1)|1);
    FLIDUInt word=0;
    if(!state->reflected) word=result<<((state->storage_bits-state->width)&31);
    else {
        for(FLIDUInt bit=8;bit<=state->storage_bits;bit+=8) {
            word|=(result&255)<<((state->storage_bits-bit)&31);
            result>>=8;
        }
    }
    return (word>>((state->storage_bits-state->width)&31))|0x80000000u;
}
FLIDUInt CreateID(const char* name) {
    CFLIDMaker* maker=CFLIDMaker::GetInstance();
    if(!maker) { flid_runtime_allocation_failure(); return 0; }
    return maker->CreateStaticID(name);
}
extern "C" FLIDUInt create_id_reconstructed(const char* name) { return CreateID(name); }
#ifdef FLID_TESTING
const FLIDCRCState* flid_test_state() { return CFLIDMaker::m_pTheMaker ? CFLIDMaker::m_pTheMaker->state : nullptr; }
void flid_test_set_counter(FLIDUInt value) { CFLIDMaker::GetInstance()->next_object_id=value; }
extern "C" const void* flid_test_state_ptr() { return flid_test_state(); }
extern "C" void flid_shutdown_reconstructed() { CFLIDMaker::Shutdown(); }
extern "C" FLIDUInt flid_allocate_object_id_reconstructed() { return CFLIDMaker::GetInstance()->AllocateObjectID(); }
extern "C" void flid_set_counter_reconstructed(FLIDUInt value) { flid_test_set_counter(value); }
#endif
