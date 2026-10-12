extern "C" void ini_runtime_line_number_warning() {
    using Fn=void(__cdecl*)(unsigned int,const char*,const char*,unsigned int,const char*);
    (**reinterpret_cast<Fn**>(0x6399028))(0x100002,"%s(%d) : *** WARNING: %s","E:\\FL\\Scratch\\Source\\Common\\Ini.cpp",0x1f6,"INI_Reader behavior here differs from traditional behavior.");
}
