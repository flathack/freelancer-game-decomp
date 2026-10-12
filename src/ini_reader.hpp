#pragma once
#include "file_map.hpp"
struct INI_Reader {
    FileMap text_file;
    unsigned int line_number;
    char text_header[1024],text_name[1024],text_value[1024];
    unsigned char unknown_0c28[0x800];
    FileMap binary_file;
    BINI_Header* binary_header;
    char* string_table;
    BINI_Block* current_block;
    short value_index;
    unsigned char padding_145a[2];
    BINI_Value* current_value;
    BINI_Parameter* parameters;
    unsigned char unknown_1464[0x100];
    bool binary_mode;
    unsigned char padding_1565[3];
    struct State { unsigned char bytes[0xc08]; };
    bool open_memory(const char*,unsigned int);
    void close();
    const char* get_line_ptr();
    const char* get_file_name() const;
    int get_line_num() const;
    bool initialize_binary(); // Internal helper at common.dll VA 0x0630fc60.
    bool read_header();
    bool read_value();
    bool find_header(const char*);
    const char* get_header_ptr();
    const char* get_name_ptr();
    unsigned int get_num_parameters() const;
    bool is_value_empty(unsigned int);
    bool is_header(const char*);
    bool is_value(const char*);
    bool is_end() const;
    void seek(unsigned int);
    unsigned int tell() const;
    void reset();
    void get_state(State&) const;
    void set_state(const State&);
};
#if __SIZEOF_POINTER__==4
static_assert(__builtin_offsetof(INI_Reader,binary_file)==0x1428,"Observed binary reader offset");
static_assert(__builtin_offsetof(INI_Reader,current_value)==0x145c,"Observed entry offset");
static_assert(__builtin_offsetof(INI_Reader,binary_mode)==0x1564,"Observed mode offset");
static_assert(sizeof(INI_Reader)==0x1568,"Observed field extent/alignment");
#endif
// Text iteration providers are reconstructed in ini_text_header/value.cpp.
extern "C" bool ini_pending_read_text_header(INI_Reader*);
extern "C" bool ini_pending_read_text_value(INI_Reader*);
extern "C" int ini_runtime_compare(const char*,const char*);
extern "C" const char* ini_runtime_string_index(const char*,unsigned int);
