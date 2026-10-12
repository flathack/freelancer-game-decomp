#include "ini_reader_values.hpp"
// Explicit hidden return pointer keeps the original class-Vector ABI.
extern "C" float* __thiscall ini_get_vector(INI_Reader*,float*)
 __asm__("?get_vector@INI_Reader@@QAE?AVVector@@XZ");
extern "C" float* __thiscall ini_get_vector(INI_Reader* reader,float* out) {
    volatile float x=static_cast<float>(ini_value_float(reader,0));
    volatile float y=static_cast<float>(ini_value_float(reader,1));
    volatile float z=static_cast<float>(ini_value_float(reader,2));
    out[0]=x;out[1]=y;out[2]=z;
    return out;
}
extern "C" double __thiscall ini_value_num(INI_Reader*,unsigned int)
 __asm__("?value_num@INI_Reader@@QAENI@Z");
extern "C" double __thiscall ini_value_num(INI_Reader* reader,unsigned int index) {
    return ini_value_float(reader,index);
}
