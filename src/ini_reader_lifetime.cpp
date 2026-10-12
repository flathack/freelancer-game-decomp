#include "ini_reader.hpp"
extern "C" void ini_runtime_line_number_warning();
void INI_Reader::close() { (binary_mode ? binary_file : text_file).close(); }
const char* INI_Reader::get_file_name() const { return (binary_mode ? binary_file : text_file).get_file_name(); }
int INI_Reader::get_line_num() const {
    if (binary_mode) { ini_runtime_line_number_warning(); return 0; }
    return static_cast<int>(line_number);
}
bool INI_Reader::open_memory(const char* source,unsigned int size) {
    FileMap temporary;
    if (!temporary.open_memory(source,size)) return false;
    binary_mode=false;
    text_file=temporary;
    temporary.data=nullptr; // Transfer data without releasing the previous reader mapping.
    line_number=0;
    text_header[0]=0;
    return true;
}

const char* INI_Reader::get_name() const {return get_file_name();}
