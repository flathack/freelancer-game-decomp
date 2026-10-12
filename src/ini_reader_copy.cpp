#include "ini_reader.hpp"
static void copy_bytes(unsigned char* out,const unsigned char* in,unsigned int count,unsigned int width) {
    while(count){unsigned int value=0;__builtin_memcpy(&value,in,width);__builtin_memcpy(out,&value,width);in+=width;out+=width;count-=width;}
}
static void copy_parser(INI_Reader* to,const INI_Reader* from,unsigned int width) {
    to->line_number=from->line_number;
    copy_bytes(reinterpret_cast<unsigned char*>(to->text_header),reinterpret_cast<const unsigned char*>(from->text_header),0x1400,width);
    to->binary_header=from->binary_header;to->string_table=from->string_table;
    to->current_block=from->current_block;to->value_index=from->value_index;
    to->current_value=from->current_value;to->parameters=from->parameters;
    copy_bytes(to->unknown_1464,from->unknown_1464,256,width);
    to->binary_mode=from->binary_mode;
}
INI_Reader::INI_Reader(const INI_Reader& source):text_file(source.text_file),binary_file(source.binary_file) {
    copy_parser(this,&source,4);
}
INI_Reader& INI_Reader::operator=(const INI_Reader& source) {
    text_file=source.text_file;
    line_number=source.line_number;
    copy_bytes(reinterpret_cast<unsigned char*>(text_header),reinterpret_cast<const unsigned char*>(source.text_header),0xc00,1);
    copy_bytes(unknown_0c28,source.unknown_0c28,0x800,2);
    binary_file=source.binary_file;
    binary_header=source.binary_header;string_table=source.string_table;
    current_block=source.current_block;value_index=source.value_index;
    current_value=source.current_value;parameters=source.parameters;
    copy_bytes(unknown_1464,source.unknown_1464,256,1);
    binary_mode=source.binary_mode;
    return *this;
}
