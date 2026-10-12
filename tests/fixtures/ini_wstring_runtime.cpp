extern "C" unsigned int ini_runtime_mbstowcs(unsigned short* out,const char* in,unsigned int size) {
 using Fn=unsigned int(__cdecl*)(unsigned short*,const char*,unsigned int);
 return (*reinterpret_cast<Fn*>(0x639920c))(out,in,size);
}
