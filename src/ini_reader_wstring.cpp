#include "ini_reader_strings.hpp"
extern "C" unsigned int ini_runtime_mbstowcs(unsigned short*,const char*,unsigned int);
unsigned short INIWideValueBuffer[256];
const unsigned short* INI_Reader::get_value_wstring() {
    if (!binary_mode) {
        unsigned short* output=reinterpret_cast<unsigned short*>(unknown_0c28);
        ini_runtime_mbstowcs(output,text_value,1024);
        return output;
    }
    const char* joined=ini_value_string_all(this);
    ini_runtime_mbstowcs(INIWideValueBuffer,joined,256);
    return INIWideValueBuffer;
}
