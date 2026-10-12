#include "ini_reader.hpp"
#include "text_file.hpp"
extern "C" bool ini_pending_read_text_header(INI_Reader* reader){
    LineParser32 line;line.buffer[0]=0;line.length=line.position=0;
    while(ReadTextLine(reader->text_file,reader->line_number,line)){
        unsigned int start=0;while(line.buffer[start]==' ' || line.buffer[start]=='\t')++start;
        if(start>=line.length || !line.buffer[start] || line.buffer[start]!='[')continue;
        ++start;unsigned int count=0;
        while(count<line.length-start && line.buffer[start+count]!=']')++count;
        while(count && (line.buffer[start+count-1]==' ' || line.buffer[start+count-1]=='\t'))--count;
        unsigned int i=0;
        while(i+4<=count){unsigned int word;__builtin_memcpy(&word,line.buffer+start+i,4);__builtin_memcpy(reader->text_header+i,&word,4);i+=4;}
        while(i<count){reader->text_header[i]=line.buffer[start+i];++i;}
        reader->text_header[count]=0;
        if(reader->text_header[0]!=';')return true;
    }
    reader->text_header[0]=0;return false;
}
