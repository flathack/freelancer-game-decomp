#include "good_info_comm.hpp"
using byte = unsigned char;
using Word = unsigned int;
static Word& word(void* self, unsigned int offset) {
    return *reinterpret_cast<Word*>(static_cast<byte*>(self) + offset);
}
extern "C" unsigned char __thiscall good_info_has_voice(void* self) {
    return word(self, 4) != 0;
}
extern "C" void* __thiscall good_info_prefix_ref(void* self) {
    return static_cast<byte*>(self) + 4;
}
// Original 0x0632e6a0..0x0632e71a. The complete scan is intentional: an
// unterminated source can fault even when the first 63 characters are readable.
extern "C" unsigned char __thiscall good_info_read_comm(void* self, INI_Reader* reader) {
    if (!arch_is_value(reader, "msg_id_prefix")) return 0; // unknown key
    const char* source = arch_whole_string(reader);
    byte* target = static_cast<byte*>(self) + 8;
    if (!source) {
        target[0] = 0;
        word(self, 4) = 0;
        return 1;
    }
    const volatile char* scan = source;
    Word length = 0;
    while (scan[length]) ++length;
    length = length > 63 ? 63 : length;
    Word pos = 0;
    // Original REP MOVSD followed by REP MOVSB, preserving the write order and
    // the integer payload. Neither a safe bounded scan nor blanket zeroing.
    for (; pos + 4 <= length; pos += 4)
        *reinterpret_cast<Word*>(target + pos) = *reinterpret_cast<const Word*>(source + pos);
    for (; pos < length; ++pos) target[pos] = static_cast<byte>(source[pos]);
    target[length] = 0;
    word(self, 4) = length;
    return 1;
}
extern "C" const void* const good_info_comm_slots[3] = {
    reinterpret_cast<const void*>(good_info_has_voice),
    reinterpret_cast<const void*>(good_info_prefix_ref),
    reinterpret_cast<const void*>(good_info_read_comm)
};
// Original base 063993d8 and derived 063993e8 are distinct three-slot tables
// with identical entries 0632e690/062bd490/0632e6a0. Preserve that identity.
extern "C" const void* const good_info_comm_base_slots[3] = {
    reinterpret_cast<const void*>(good_info_has_voice),
    reinterpret_cast<const void*>(good_info_prefix_ref),
    reinterpret_cast<const void*>(good_info_read_comm)
};
extern "C" unsigned int good_info_runtime_vtable(bool derived) {
    return reinterpret_cast<unsigned int>(derived ? good_info_comm_slots : good_info_comm_base_slots);
}
