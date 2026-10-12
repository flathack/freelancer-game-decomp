#include "text_file.hpp"
bool ReadTextLine(FileMap& file,unsigned int& line_number,LineParser32& line){
    unsigned int start=file.tell();++line_number;
    unsigned int available=1023;
    const char* source=static_cast<const char*>(file.request_pointer(available));
    if(!source){line.buffer[0]=0;line.length=0;line.position=0;return false;}
    unsigned int count=available,consumed=available;
    for(unsigned int i=0;i<available;++i){
        unsigned char ch=static_cast<unsigned char>(source[i]);
        if(ch==13 || ch==10){count=i;consumed=i+1;if(consumed<available && static_cast<unsigned char>(source[consumed])==(ch^7))++consumed;break;}
    }
    unsigned int offset=0;
    while(offset+4<=count){unsigned int word;__builtin_memcpy(&word,source+offset,4);__builtin_memcpy(line.buffer+offset,&word,4);offset+=4;}
    while(offset<count){line.buffer[offset]=source[offset];++offset;}
    line.buffer[count]=0;line.length=count;line.position=0;
    file.seek(start+consumed);return true;
}

bool TextFile32::read_line(LineParser32& line){return ReadTextLine(*this,line_number,line);}
