#include "ini_reader_values.hpp"
extern "C" unsigned char __thiscall ini_get_bool(INI_Reader*,unsigned int)
 __asm__("?get_bool@INI_Reader@@QAE_NI@Z");
extern "C" unsigned char __thiscall ini_get_bool(INI_Reader* reader,unsigned int index) {
    return ini_value_bool(reader,index);
}
