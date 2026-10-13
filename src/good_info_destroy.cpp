// GoodInfo storage lifecycle, recovered from common.dll VA 0x06270330.
using u32 = unsigned int;
struct GoodInfoStorage { unsigned char bytes[192]; };
extern "C" void good_info_runtime_free(void*);
extern "C" u32 good_info_runtime_vtable(bool);
static volatile u32& word(GoodInfoStorage* p, unsigned offset) {
    return *reinterpret_cast<volatile u32*>(p->bytes + offset);
}
static void clear(GoodInfoStorage* p, unsigned offset) {
    auto* head = reinterpret_cast<u32*>(word(p, offset + 4));
    auto* node = reinterpret_cast<u32*>(head[0]);
    while (node != head) {
        auto* next = reinterpret_cast<u32*>(node[0]);
        reinterpret_cast<u32*>(node[1])[0] = node[0];
        next[1] = node[1];
        good_info_runtime_free(node);
        word(p, offset + 8) = word(p, offset + 8) - 1;
        node = next;
    }
}
extern "C" void __thiscall good_info_destroy(GoodInfoStorage*)
    asm("??1GoodInfo@@QAE@XZ");
extern "C" void __thiscall good_info_destroy(GoodInfoStorage* p) {
    word(p, 0) = good_info_runtime_vtable(true);
    clear(p,148); clear(p,160); clear(p,172);
    for (unsigned offset = 172; offset >= 148; offset -= 12) {
        clear(p,offset);
        good_info_runtime_free(reinterpret_cast<void*>(word(p,offset+4)));
        word(p,offset+4)=0; word(p,offset+8)=0;
    }
}
