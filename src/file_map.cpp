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

static unsigned int name_size(const char* s){unsigned int n=0;while(s[n])++n;return n;}
static void tidy_name_inline(FileMap* target){
    if(target->file_name){
        unsigned char& refs=reinterpret_cast<unsigned char*>(target->file_name)[-1];
        if(refs==0 || refs==255)filemap_runtime_string_free(target->file_name-1);
        else --refs;
    }
    target->file_name=nullptr;target->name_length=target->name_capacity=0;
}
static void copy_name(FileMap* target,const FileMap* source){
    if(target==source){filemap_runtime_string_split(target);filemap_runtime_string_split(target);return;}
    unsigned int size=source->name_length;
    const char* text=source->file_name?source->file_name:filemap_runtime_empty_name();
    if(size && static_cast<unsigned char>(text[-1])<254){
        tidy_name_inline(target);
        target->file_name=const_cast<char*>(text);target->name_length=size;target->name_capacity=source->name_capacity;
        ++reinterpret_cast<unsigned char*>(target->file_name)[-1];return;
    }
    if(filemap_runtime_string_grow(target,size,true)){
        copy_forward(target->file_name,text,size);target->name_length=size;target->file_name[size]=0;
    }
}
static void clear_name(FileMap* target){
    char* text=target->file_name;
    if(text && static_cast<unsigned char>(text[-1])!=0 && static_cast<unsigned char>(text[-1])!=255){
        --reinterpret_cast<unsigned char*>(text)[-1];
        target->file_name=nullptr;target->name_length=target->name_capacity=0;
        filemap_runtime_string_assign(target,text,name_size(text));
    }
    if(target->name_length){target->name_length=0;target->file_name[0]=0;}
}
static void release_resources(FileMap* target){
    if(target->file_handle!=reinterpret_cast<void*>(~0u)){
        if(target->mapping_handle){
            if(target->data){filemap_runtime_unmap(target->data);target->data=nullptr;target->length=0;}
            filemap_runtime_close_handle(target->mapping_handle);target->mapping_handle=nullptr;
        }
        filemap_runtime_close_handle(target->file_handle);target->file_handle=reinterpret_cast<void*>(~0u);
    }
    if(target->data){filemap_runtime_free(target->data);target->data=nullptr;target->length=0;}
    target->position=0;
}
FileMap::FileMap(const FileMap& other):file_name(nullptr),name_length(0),name_capacity(0){
    allocator_opaque[0]=other.allocator_opaque[0];copy_name(this,&other);
    file_handle=other.file_handle;mapping_handle=other.mapping_handle;data=other.data;length=other.length;position=other.position;
}
FileMap& FileMap::operator=(const FileMap& other){
    copy_name(this,&other);file_handle=other.file_handle;mapping_handle=other.mapping_handle;data=other.data;length=other.length;position=other.position;return *this;
}
FileMap::~FileMap(){close();filemap_runtime_string_tidy(this,true);}
void FileMap::close(){clear_name(this);release_resources(this);}
void FileMap::handoff_to(FileMap& other){
    copy_name(&other,this);other.file_handle=file_handle;other.mapping_handle=mapping_handle;other.data=data;other.length=length;other.position=position;
    data=nullptr;mapping_handle=nullptr;file_handle=reinterpret_cast<void*>(~0u);
}
bool FileMap::open(const char* name){
    filemap_runtime_string_split(this);clear_name(this);release_resources(this);
    unsigned int size=name_size(name);
    if(filemap_runtime_string_grow(this,size,true)){copy_forward(file_name,name,size);name_length=size;file_name[size]=0;}
    file_handle=filemap_runtime_open_file(name);
    if(file_handle!=reinterpret_cast<void*>(~0u)){
        mapping_handle=filemap_runtime_create_mapping(file_handle);
        if(mapping_handle){length=filemap_runtime_file_size(file_handle);data=static_cast<unsigned char*>(filemap_runtime_map_view(mapping_handle,length));if(data){position=0;return true;}}
    }
    close();return false;
}
