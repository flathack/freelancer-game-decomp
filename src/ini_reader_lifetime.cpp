#include "ini_reader.hpp"
extern "C" void ini_runtime_line_number_warning();
void INI_Reader::close() { (binary_mode ? binary_file : text_file).close(); }
const char* INI_Reader::get_file_name() const { return (binary_mode ? binary_file : text_file).get_file_name(); }
int INI_Reader::get_line_num() const {
    if (binary_mode) { ini_runtime_line_number_warning(); return 0; }
    return static_cast<int>(line_number);
}
