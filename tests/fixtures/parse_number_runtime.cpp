extern "C" int parse_number_tolower(int c){using Fn=int(__cdecl*)(int);return (*reinterpret_cast<Fn*>(0x63992f4))(c);}
extern "C" double parse_number_atof(const char* s){using Fn=double(__cdecl*)(const char*);return (*reinterpret_cast<Fn*>(0x63992f0))(s);}
extern "C" void parse_number_bad_digit(const char* s){
 using Fn=void(__cdecl*)(unsigned int,const char*,...);Fn fn=**reinterpret_cast<Fn**>(0x6399028);
 fn(0x100002,"%s(%d) : *** WARNING: ParseNumber: illegal BASE-N digit(s) in argument! '%s'","E:\\FL\\Scratch\\Source\\Common\\Parse.cpp",0x14e,s);
}

