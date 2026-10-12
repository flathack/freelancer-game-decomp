#include "ini_reader_strings.hpp"
// Original line output starts at 0x0658d800; numeric output at +0x100.
extern "C" { char INIStringStorage[512]; }
__asm__(".globl \"?INIBinaryLineBuffer@@3PADA\"\n"
        ".set \"?INIBinaryLineBuffer@@3PADA\", _INIStringStorage\n"
        ".globl \"?INIValuesStringBuffer@@3PADA\"\n"
        ".set \"?INIValuesStringBuffer@@3PADA\", _INIStringStorage+256\n");
extern "C" int ini_strings_sprintf(char*,const char*,...);
static const char* binary_string(INI_Reader* reader,unsigned int index){
    if(!reader->current_value)return "";
    if(index>=reader->current_value->parameter_count){
        ini_values_missing_parameter(reader->string_table+reader->current_block->name_offset,reader->string_table+reader->current_value->name_offset,index);
        return "";
    }
    BINI_Parameter* p=reader->parameters+index;
    switch(p->type){
        case 0:ini_strings_sprintf(INIValuesStringBuffer,"%d",static_cast<unsigned char>(p->bits));break;
        case 1:ini_strings_sprintf(INIValuesStringBuffer,"%d",static_cast<int>(p->bits));break;
        case 2:{float value;__builtin_memcpy(&value,&p->bits,4);ini_strings_sprintf(INIValuesStringBuffer,"%g",static_cast<double>(value));break;}
        case 3:return reader->string_table+p->bits;
        default:break; // Return existing shared-buffer contents, not a newly empty string.
    }
    return INIValuesStringBuffer;
}
extern "C" const char* __thiscall ini_value_string(INI_Reader* reader,unsigned int index){
    return reader->binary_mode?binary_string(reader,index):ini_runtime_string_index(reader->text_value,index);
}
static unsigned int length(const char* s){unsigned int n=0;while(s[n])++n;return n;}
static void append(char* target,const char* text){
    unsigned int size=length(text)+1;target+=length(target);
    while(size>=4){unsigned int word;__builtin_memcpy(&word,text,4);__builtin_memcpy(target,&word,4);target+=4;text+=4;size-=4;}
    while(size--)*target++=*text++;
}
extern "C" const char* __thiscall ini_value_string_all(INI_Reader* reader){
    if(!reader->binary_mode)return reader->text_value;
    char* joined=reinterpret_cast<char*>(reader->unknown_1464);joined[0]=0;
    if(reader->current_value){
        for(unsigned int index=0;index<reader->current_value->parameter_count;++index){
            const char* value=binary_string(reader,index);
            if(index){unsigned int n=length(joined);joined[n]=',';joined[n+1]=' ';joined[n+2]=0;}
            append(joined,value);
        }
    }
    return joined;
    // No length guard: original can overwrite the adjacent mode byte. The internal
    // binary helper intentionally does not re-read that byte during the join loop.
}
