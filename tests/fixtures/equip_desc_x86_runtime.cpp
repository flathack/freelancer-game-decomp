#include "../../src/equip_desc.hpp"
// Test-only constants: mirrored into the original DLL's globals by the harness.
extern const unsigned short SUBOBJ_ID_NONE=0;
const CacheString EquipDesc::CARGO_BAY_HP_NAME={reinterpret_cast<const char*>(0x20501000)};
namespace Archetype {
Equipment* GetEquipment(unsigned int id) {
    using Fn=Equipment*(__cdecl*)(unsigned int);
    return reinterpret_cast<Fn>(0x062f9370)(id);
}
}
extern "C" { int _fltused=0; }
