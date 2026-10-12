#include "ini_reader_values.hpp"
// ABI-oriented double return under the original float member symbol. x87 uses
// ST0 for both types; double avoids Clang's premature binary32 return narrowing.
// Every int32/byte and finite float32 value is representable exactly as binary64.
extern "C" double __thiscall ini_value_float(INI_Reader* reader,unsigned int index){
    if(!reader->binary_mode)return ini_values_pending_text_float(reader,index);
    if(!reader->current_value)return 0.0;
    if(index>=reader->current_value->parameter_count){
        ini_values_missing_parameter(reader->string_table+reader->current_block->name_offset,reader->string_table+reader->current_value->name_offset,index);
        return 0.0;
    }
    BINI_Parameter* p=reader->parameters+index;
    switch(p->type){
        case 0:return static_cast<unsigned char>(p->bits);
        case 1:return static_cast<int>(p->bits);
        case 2:{float value;__builtin_memcpy(&value,&p->bits,4);return value;}
        case 3:return ini_values_atof(reader->string_table+p->bits);
        default:return 0.0;
    }
}
