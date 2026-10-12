#include "../../src/ini_reader.hpp"
extern "C" double ini_values_atof(const char* text){using Fn=double(__cdecl*)(const char*);return (*reinterpret_cast<Fn*>(0x63992f0))(text);}
