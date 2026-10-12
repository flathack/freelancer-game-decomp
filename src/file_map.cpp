#include "file_map.hpp"
static void copy_forward(void* destination,const void* source,unsigned int size) {
    unsigned char* d=static_cast<unsigned char*>(destination);
    const unsigned char* s=static_cast<const unsigned char*>(source);
    while(size>=4){unsigned int word;__builtin_memcpy(&word,s,4);__builtin_memcpy(d,&word,4);s+=4;d+=4;size-=4;}
    while(size--)*d++=*s++;
}
FileMap::FileMap() : file_name(nullptr),name_length(0),name_capacity(0),file_handle(reinterpret_cast<void*>(~0u)),mapping_handle(nullptr),data(nullptr),length(0),position(0) {}
bool FileMap::open_memory(const void* source,unsigned int size) {
    if(!source || !size)return false;
    data=static_cast<unsigned char*>(filemap_runtime_allocate(size));
    copy_forward(data,source,size);
    length=size;position=0;return true;
    // Original does not release old data/handles here; do not turn this into close/open.
}
const char* FileMap::get_file_name() const { return file_name?file_name:filemap_runtime_empty_name(); }
unsigned int FileMap::get_file_length() const { return length; }
bool FileMap::eof() const { return position>=length; }
unsigned int FileMap::tell() const { return data?position:0; }
void FileMap::seek(unsigned int offset) { if(data)position=offset<=length?offset:length; }
void* FileMap::request_pointer(unsigned int& size) {
    if(!data || position>=length){size=0;return nullptr;}
    unsigned int available=length-position;
    if(available<size)size=available;
    unsigned char* result=data+position;position+=size;return result;
}
unsigned int FileMap::read(void* destination,unsigned int size) {
    void* source=request_pointer(size);
    if(source)copy_forward(destination,source,size);
    return source?size:0;
}
bool FileMap::read_ptr(BINI_Header*& out) { unsigned int size=12;out=static_cast<BINI_Header*>(request_pointer(size));if(size!=12){out=nullptr;return false;}return true; }
bool FileMap::read_ptr(BINI_Block*& out) { unsigned int size=4;out=static_cast<BINI_Block*>(request_pointer(size));if(size!=4){out=nullptr;return false;}return true; }
bool FileMap::read_ptr(BINI_Value*& out) { unsigned int size=3;out=static_cast<BINI_Value*>(request_pointer(size));if(size!=3){out=nullptr;return false;}return true; }
