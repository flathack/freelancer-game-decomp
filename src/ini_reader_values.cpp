#include "ini_reader_values.hpp"
static float float_bits(unsigned int bits){float value;__builtin_memcpy(&value,&bits,4);return value;}
static BINI_Parameter* parameter(INI_Reader* reader,unsigned int index){
    if(!reader->current_value)return nullptr;
    if(index>=reader->current_value->parameter_count){
        ini_values_missing_parameter(reader->string_table+reader->current_block->name_offset,reader->string_table+reader->current_value->name_offset,index);
        return nullptr;
    }
    return reader->parameters+index;
}
extern "C" unsigned char __thiscall ini_value_bool(INI_Reader* reader,unsigned int index){
    if(!reader->binary_mode){
        const char* s=ini_runtime_string_index(reader->text_value,index);
        if(!ini_runtime_compare(s,"true") || !ini_runtime_compare(s,"1"))return 1;
        if(!ini_runtime_compare(s,"false") || !ini_runtime_compare(s,"0"))return 0;
        ini_values_invalid_text_bool(s,reader->text_file.get_file_name());return 0;
    }
    BINI_Parameter* p=parameter(reader,index);if(!p)return 0;
    switch(p->type){
        case 0:return static_cast<unsigned char>(p->bits);
        case 1:return p->bits!=0;
        case 2:return float_bits(p->bits)!=0.0f;
        case 3:{
            const char* s=reader->string_table+p->bits;
            if(!ini_runtime_compare(s,"true"))return 1;
            if(!ini_runtime_compare(s,"false"))return 0;
            return ini_values_atoi(s)!=0;
        }
        default:return 0;
    }
}
extern "C" int __thiscall ini_value_int(INI_Reader* reader,unsigned int index){
    if(!reader->binary_mode)return ini_values_atoi(ini_runtime_string_index(reader->text_value,index));
    BINI_Parameter* p=parameter(reader,index);if(!p)return 0;
    switch(p->type){
        case 0:return static_cast<unsigned char>(p->bits);
        case 1:return static_cast<int>(p->bits);
        case 2:return ini_values_float_to_int(float_bits(p->bits));
        case 3:return ini_values_atoi(reader->string_table+p->bits);
        default:return 0;
    }
}
