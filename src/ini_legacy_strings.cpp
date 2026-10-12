#include "ini_reader_strings.hpp"
extern "C" const char* __thiscall ini_get_indexed_value(INI_Reader*,unsigned int)
 __asm__("?get_indexed_value@INI_Reader@@QAEPBDI@Z");
extern "C" const char* __thiscall ini_get_value_ptr(INI_Reader*)
 __asm__("?get_value_ptr@INI_Reader@@QAEPBDXZ");
extern "C" const char* __thiscall ini_get_indexed_value(INI_Reader* reader,unsigned int index) {
    return ini_value_string(reader,index);
}
extern "C" const char* __thiscall ini_get_value_ptr(INI_Reader* reader) {
    return ini_value_string_all(reader);
}
