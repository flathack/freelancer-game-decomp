// Behavior reconstructed from common.dll RVA 0xad0f0, 0xad270, 0xad3b0.
// This implementation is behavior-verified, not machine-code matching yet.
// _strlwr is modeled for ASCII; the original CRT's locale-dependent bytes are
// outside the verified domain. The original has a 256-byte unchecked copy.
using u32 = unsigned int;
static_assert(sizeof(u32) == 4, "32-bit unsigned integer required");

static u32 reflect(u32 value, unsigned width) {
    u32 result = 0;
    for (unsigned bit = 0; bit < width; ++bit) {
        result |= (value & 1) << (width - 1 - bit);
        value >>= 1;
    }
    return result;
}

static void make_table(u32 (&table)[256]) {
    // Observed configuration: width=30, polynomial=0x8005, reflected input
    // and output, initial remainder=0, final XOR=0, output storage=32 bits.
    for (u32 i = 0; i < 256; ++i) {
        u32 value = reflect(i, 8) << 22;
        for (unsigned bit = 0; bit < 8; ++bit)
            value = (value & 0x20000000u) ? (value << 1) ^ 0x8005u : value << 1;
        table[i] = reflect(value, 30) & 0x3fffffffu;
    }
}

extern "C" u32 create_id_reconstructed(const char* name) {
    if (!name) return 0;
    u32 table[256];
    make_table(table);
    u32 remainder = 0;
    for (const unsigned char* p = reinterpret_cast<const unsigned char*>(name); *p; ++p) {
        unsigned char byte = *p;
        if (byte >= 'A' && byte <= 'Z') byte += 'a' - 'A';
        remainder = (remainder >> 8) ^ table[(remainder & 0xff) ^ byte];
    }
    // Reverse byte order in the 32-bit storage word, then shift to 30 bits.
    u32 swapped = ((remainder & 0xff) << 24) | ((remainder & 0xff00) << 8)
                | ((remainder >> 8) & 0xff00) | (remainder >> 24);
    return (swapped >> 2) | 0x80000000u;
}
