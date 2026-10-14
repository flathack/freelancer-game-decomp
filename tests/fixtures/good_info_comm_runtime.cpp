#include "../../src/good_info_comm.hpp"
// Only INI service boundaries, intercepted explicitly by the callback suite.
// No callback, copy, constructor, dispatcher or container is modeled here.
extern "C" __declspec(naked) unsigned char __thiscall arch_is_value(INI_Reader*, const char*) {
    __asm { mov eax, 063104a0h }
    __asm { jmp eax }
}
extern "C" __declspec(naked) const char* __thiscall arch_whole_string(INI_Reader*) {
    __asm { mov eax, 06310c00h }
    __asm { jmp eax }
}
