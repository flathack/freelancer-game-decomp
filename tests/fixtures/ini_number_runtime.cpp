extern "C" int ini_number_tolower(int value) {
    using Fn=int(__cdecl*)(int);return (*reinterpret_cast<Fn*>(0x63992f4))(value);
}
