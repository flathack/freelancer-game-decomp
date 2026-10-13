extern "C" void archetype_lookup_error(unsigned id) {
    using Dump=void (__cdecl*)(unsigned,const char*,const char*,unsigned,unsigned);
    auto pointer=*reinterpret_cast<Dump**>(0x06399028);
    (*pointer)(0x100001,"%s(%d) : *** ERROR: ArchDB::Get(%u) failed","E:\\FL\\Scratch\\Source\\Common\\Archetype.cpp",0x3c,id);
}
