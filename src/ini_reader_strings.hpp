#pragma once
#include "ini_reader_values.hpp"
extern char INIValuesStringBuffer[256];
extern "C" const char* __thiscall ini_value_string(INI_Reader*,unsigned int)
 __asm__("?get_value_string@INI_Reader@@QAEPBDI@Z");
extern "C" const char* __thiscall ini_value_string_all(INI_Reader*)
 __asm__("?get_value_string@INI_Reader@@QAEPBDXZ");
