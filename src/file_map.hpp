#pragma once
// Packed-size views only; field meanings are reserved for the BINI parser reconstruction.
struct BINI_Header { unsigned char bytes[12]; };
struct BINI_Block { unsigned char bytes[4]; };
struct BINI_Value { unsigned char bytes[3]; };
struct FileMap {
    // Observed MSVC6 std::string layout; imported COW operations remain in MSVCP60.
    unsigned char allocator_opaque[4];
    char* file_name;
    unsigned int name_length,name_capacity;
    void *file_handle,*mapping_handle;
    unsigned char* data;
    unsigned int length,position;
    FileMap();
    FileMap(const FileMap&);
    ~FileMap();
    FileMap& operator=(const FileMap&);
    bool open(const char*);
    void close();
    void handoff_to(FileMap&);
    bool open_memory(const void*,unsigned int);
    const char* get_file_name() const;
    unsigned int get_file_length() const;
    bool eof() const;
    unsigned int tell() const;
    void seek(unsigned int);
    void* request_pointer(unsigned int&);
    unsigned int read(void*,unsigned int);
    bool read_ptr(BINI_Header*&);
    bool read_ptr(BINI_Block*&);
    bool read_ptr(BINI_Value*&);
};
#if __SIZEOF_POINTER__==4
static_assert(sizeof(FileMap)==36,"Observed FileMap allocation/stride");
static_assert(__builtin_offsetof(FileMap,data)==24,"Observed data offset");
#endif
extern "C" void* filemap_runtime_allocate(unsigned int);
extern "C" const char* filemap_runtime_empty_name();

// Imported MSVCP60 COW operations and Win32 file APIs are external dependencies.
extern "C" bool filemap_runtime_string_grow(FileMap*,unsigned int,bool);
extern "C" void filemap_runtime_string_split(FileMap*);
extern "C" void filemap_runtime_string_tidy(FileMap*,bool);
extern "C" void filemap_runtime_string_assign(FileMap*,const char*,unsigned int);
extern "C" void filemap_runtime_string_free(void*);
extern "C" void filemap_runtime_free(void*);
extern "C" void* filemap_runtime_open_file(const char*);
extern "C" void* filemap_runtime_create_mapping(void*);
extern "C" unsigned int filemap_runtime_file_size(void*);
extern "C" void* filemap_runtime_map_view(void*,unsigned int);
extern "C" void filemap_runtime_unmap(void*);
extern "C" void filemap_runtime_close_handle(void*);
