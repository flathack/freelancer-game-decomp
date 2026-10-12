extern "C" __declspec(naked) int ini_strings_sprintf(char*,const char*,...){
    __asm{mov eax,dword ptr [0639931ch]
          jmp eax}
}
