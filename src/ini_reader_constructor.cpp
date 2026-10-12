#include "ini_reader.hpp"
INI_Reader::INI_Reader() {
    // Original uses the incoming ECX high byte as the opaque allocator byte.
    unsigned char allocator=static_cast<unsigned char>(reinterpret_cast<unsigned int>(this)>>24);
    text_file.allocator_opaque[0]=allocator;
    binary_file.allocator_opaque[0]=allocator;
    line_number=0;
    text_header[0]=0;
    binary_header=nullptr;
    string_table=nullptr;
    current_block=nullptr;
    current_value=nullptr;
    binary_mode=false;
    // Remaining text/binary parser buffers, value_index and parameters are untouched.
}
