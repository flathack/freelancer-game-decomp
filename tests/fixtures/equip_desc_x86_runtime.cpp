#include "../../src/equip_desc.hpp"
// Equipment lookup remains bound to the controlled emulator fixture.
namespace Archetype {
Equipment* GetEquipment(unsigned int id) {
    using Fn=Equipment*(__cdecl*)(unsigned int);
    return reinterpret_cast<Fn>(0x062f9370)(id);
}
}
extern "C" { int _fltused=0; }
