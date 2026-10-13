#include "loadout_map.hpp"
extern "C" Loadout::Map* __thiscall loadout_map_initialize(Loadout::Map* object) {
 object->id=0;object->begin=object->end=object->capacity=nullptr;
 object->ids.Reset();return object;
}
// Original opaque allocator byte comes from entry ESP-17, not from a value
// represented in the C++ object model. Keep this temporary ABI boundary explicit.
extern "C" Loadout::Map* __thiscall loadout_map_default(Loadout::Map*)
 __asm__("??0Map@Loadout@@QAE@XZ");
extern "C" __declspec(naked) Loadout::Map* __thiscall loadout_map_default(Loadout::Map*) {
 __asm {
  mov dword ptr [ecx],0
  mov al,byte ptr [esp-17]
  mov byte ptr [ecx+4],al
  jmp loadout_map_initialize
 }
}
