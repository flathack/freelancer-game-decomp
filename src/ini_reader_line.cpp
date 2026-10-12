#include "ini_reader_strings.hpp"
extern "C" int ini_strings_sprintf(char*,const char*,...);
// Separate original static destinations; extents beyond tested output need more audit.
char INITextLineBuffer[2048];
char INIBinaryLineBuffer[256];
const char* INI_Reader::get_line_ptr() {
    if (!binary_mode) {
        ini_strings_sprintf(INITextLineBuffer,"%s = %s",text_name,text_value);
        return INITextLineBuffer;
    }
    if (!current_value) return "";
    ini_strings_sprintf(INIBinaryLineBuffer,"%s = ",string_table+current_value->name_offset);
    const char* value=ini_value_string_all(this);
    unsigned int end=0;while(INIBinaryLineBuffer[end])++end;
    unsigned int size=0;while(value[size])++size;++size;
    char* out=INIBinaryLineBuffer+end;
    while(size>=4){unsigned int word;__builtin_memcpy(&word,value,4);__builtin_memcpy(out,&word,4);out+=4;value+=4;size-=4;}
    while(size--)*out++=*value++;
    return INIBinaryLineBuffer;
}
