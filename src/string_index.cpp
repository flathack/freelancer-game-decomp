#include "string_index.hpp"
char StringIndexBuffer[1024];
static bool space(unsigned char ch){ch&=0x7f;return ch==9 || ch==10 || ch==13 || ch==32;}
const char* StringIndex(const char* text,unsigned int index){
    const char* end;
    for(;;){
        while(space(static_cast<unsigned char>(*text)))++text;
        end=text;while(*end && *end!=',')++end;
        if(!index)break;
        if(!*end){StringIndexBuffer[0]=0;return StringIndexBuffer;}
        text=end+1;--index;
    }
    while(text<end && space(static_cast<unsigned char>(end[-1])))--end;
    unsigned int length=static_cast<unsigned int>(end-text),remaining=length;
    const char* source=text;char* destination=StringIndexBuffer;
    while(remaining>=4){unsigned int word;__builtin_memcpy(&word,source,4);__builtin_memcpy(destination,&word,4);source+=4;destination+=4;remaining-=4;}
    while(remaining--)*destination++=*source++;
    StringIndexBuffer[length]=0;return StringIndexBuffer;
    // Original uses a global scratch buffer and has no bounds/quote handling.
}
