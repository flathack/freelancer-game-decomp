// Reconstructed from this installation's common.dll exports and instructions.
// Only the observed offsets are modeled; this is not a complete CSimple layout.
class CSimple {
    unsigned char unknown_000[0xb0];
    unsigned int id;
    unsigned char unknown_0b4[0x2c];
    unsigned int type;
public:
    const unsigned int& get_id() const;
    unsigned int get_type() const;
};
const unsigned int& CSimple::get_id() const { return id; }
unsigned int CSimple::get_type() const { return type; }
