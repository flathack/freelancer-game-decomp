#pragma once
#include "ini_reader.hpp"
// ABI entries use original member symbols. The bool entry returns the raw AL byte
// because original tag-0 values are not canonicalized to 0/1.
extern "C" unsigned char __thiscall ini_value_bool(INI_Reader*,unsigned int)
 __asm__("?get_value_bool@INI_Reader@@QAE_NI@Z");
extern "C" int __thiscall ini_value_int(INI_Reader*,unsigned int)
 __asm__("?get_value_int@INI_Reader@@QAEHI@Z");
extern "C" int ini_values_atoi(const char*);
extern "C" int ini_values_float_to_int(float);
extern "C" void ini_values_missing_parameter(const char*,const char*,unsigned int);
extern "C" void ini_values_invalid_text_bool(const char*,const char*);
extern "C" double __thiscall ini_value_float(INI_Reader*,unsigned int)
 __asm__("?get_value_float@INI_Reader@@QAEMI@Z");
extern "C" double ini_values_atof(const char*);
extern "C" double __fastcall ini_values_pending_text_float(INI_Reader*,unsigned int);
