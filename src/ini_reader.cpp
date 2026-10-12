#include "ini_reader.hpp"
bool INI_Reader::initialize_binary(){
    binary_file.seek(0);BINI_Header* header=nullptr;
    if(!binary_file.read_ptr(header) || header->magic!=0x494e4942 || header->string_table_offset>=binary_file.length){binary_file.seek(0);header=nullptr;}
    binary_header=header;if(!header)return false;
    string_table=reinterpret_cast<char*>(header)+header->string_table_offset;current_block=nullptr;current_value=nullptr;return true;
}
void INI_Reader::seek(unsigned int offset){(binary_mode?binary_file:text_file).seek(offset);}
unsigned int INI_Reader::tell() const{return (binary_mode?binary_file:text_file).tell();}
void INI_Reader::reset(){
    if(binary_mode){current_block=nullptr;current_value=nullptr;binary_file.seek(12);}
    else{line_number=0;text_header[0]=0;text_file.seek(0);}
}
bool INI_Reader::read_header(){
    if(!binary_mode)return ini_pending_read_text_header(this);
    if(current_block && int(value_index)<int(current_block->value_count)){
        do{
            if(binary_file.read_ptr(current_value))binary_file.seek(binary_file.tell()+unsigned(current_value->parameter_count)*5);
            ++value_index;
        }while(int(value_index)<int(current_block->value_count));
    }
    current_block=nullptr;current_value=nullptr;
    if(binary_file.tell()>=binary_header->string_table_offset)return false;
    if(!binary_file.read_ptr(current_block))return false;
    value_index=0;return true;
}
bool INI_Reader::read_value(){
    if(!binary_mode)return ini_pending_read_text_value(this);
    if(int(current_block->value_count)<=int(value_index))return false;
    if(!binary_file.read_ptr(current_value))return false;
    unsigned int bytes=unsigned(current_value->parameter_count)*5;
    parameters=static_cast<BINI_Parameter*>(binary_file.request_pointer(bytes));
    ++value_index;return true;
    // Original accepts a short/null payload request after a complete entry header.
}
const char* INI_Reader::get_header_ptr(){return binary_mode?string_table+current_block->name_offset:text_header;}
const char* INI_Reader::get_name_ptr(){return binary_mode?string_table+current_value->name_offset:text_name;}
bool INI_Reader::is_header(const char* name){return ini_runtime_compare(get_header_ptr(),name)==0;}
bool INI_Reader::is_value(const char* name){return ini_runtime_compare(get_name_ptr(),name)==0;}
bool INI_Reader::find_header(const char* name){reset();while(read_header())if(is_header(name))return true;return false;}
unsigned int INI_Reader::get_num_parameters() const{
    if(binary_mode)return current_value->parameter_count;
    const char* s=text_value;if(!*s)return 0;unsigned int count=1;for(;*s;++s)if(*s==',')++count;return count;
}
bool INI_Reader::is_value_empty(unsigned int index){
    if(binary_mode)return !current_value || index>=current_value->parameter_count;
    return *ini_runtime_string_index(text_value,index)==0;
}
bool INI_Reader::is_end() const{return binary_mode?binary_file.tell()>=binary_header->string_table_offset:(text_file.data?text_file.eof():text_file.length==0);}
static void store_word(unsigned char* p,unsigned int value){__builtin_memcpy(p,&value,4);}
static unsigned int load_word(const unsigned char* p){unsigned int value;__builtin_memcpy(&value,p,4);return value;}
static void copy_1024(unsigned char* d,const unsigned char* s){for(unsigned int i=0;i<1024;i+=4){unsigned int value=load_word(s+i);store_word(d+i,value);}}
void INI_Reader::get_state(State& out) const{
    unsigned char* p=out.bytes;store_word(p,tell());
    if(binary_mode){
        unsigned int base=reinterpret_cast<__SIZE_TYPE__>(binary_file.data);
        store_word(p+4,reinterpret_cast<__SIZE_TYPE__>(current_block)-base);
        __builtin_memcpy(p+8,&value_index,2);
        store_word(p+12,reinterpret_cast<__SIZE_TYPE__>(current_value)-base);
        store_word(p+16,reinterpret_cast<__SIZE_TYPE__>(parameters)-base);
    }else{
        store_word(p+4,line_number);copy_1024(p+8,reinterpret_cast<const unsigned char*>(text_header));
        copy_1024(p+0x408,reinterpret_cast<const unsigned char*>(text_name));copy_1024(p+0x808,reinterpret_cast<const unsigned char*>(text_value));
    }
}
void INI_Reader::set_state(const State& state){
    const unsigned char* p=state.bytes;seek(load_word(p));
    if(binary_mode){
        unsigned int base=reinterpret_cast<__SIZE_TYPE__>(binary_file.data);
        current_block=reinterpret_cast<BINI_Block*>(base+load_word(p+4));__builtin_memcpy(&value_index,p+8,2);
        current_value=reinterpret_cast<BINI_Value*>(base+load_word(p+12));parameters=reinterpret_cast<BINI_Parameter*>(base+load_word(p+16));
    }else{
        line_number=load_word(p+4);copy_1024(reinterpret_cast<unsigned char*>(text_header),p+8);
        copy_1024(reinterpret_cast<unsigned char*>(text_name),p+0x408);copy_1024(reinterpret_cast<unsigned char*>(text_value),p+0x808);
    }
}
