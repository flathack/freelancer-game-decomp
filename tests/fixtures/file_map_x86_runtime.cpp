extern "C" void* filemap_runtime_allocate(unsigned int n){using Fn=void*(__cdecl*)(unsigned int);return (*reinterpret_cast<Fn*>(0x6399328))(n);}
extern "C" const char* filemap_runtime_empty_name(){return *reinterpret_cast<const char**>(0x63991d0);}
