#include "ini_reader.hpp"
extern "C" void ini_runtime_refresh_loading();
extern "C" void ini_runtime_fatal_open(const char*);
bool INI_Reader::open(const char* name,bool fatal) {
    ini_runtime_refresh_loading();
    FileMap temporary;
    if (!temporary.open(name)) {if(fatal)ini_runtime_fatal_open(name);return false;}
    temporary.seek(0);
    BINI_Header* header=nullptr;
    if(temporary.read_ptr(header) && header->magic==0x494e4942 && header->string_table_offset<temporary.length) {
        binary_file=temporary;
        temporary.data=nullptr;temporary.mapping_handle=nullptr;temporary.file_handle=reinterpret_cast<void*>(~0u);
        if(initialize_binary()){binary_mode=true;return true;}
    } else temporary.seek(0);
    binary_mode=false;
    text_file=temporary;
    temporary.data=nullptr;temporary.mapping_handle=nullptr;temporary.file_handle=reinterpret_cast<void*>(~0u);
    line_number=0;text_header[0]=0;
    return true;
}
