#include "ini_reader.hpp"
#include "text_file.hpp"
extern "C" bool ini_pending_read_text_value(INI_Reader* reader){
    for(;;){
        unsigned int prior_line=reader->line_number,prior_cursor=reader->text_file.tell();
        LineParser32 line;line.buffer[0]=0;line.length=line.position=0;
        if(!ReadTextLine(reader->text_file,reader->line_number,line)){reader->text_name[0]=0;return false;}
        unsigned int position=0;while(line.buffer[position]==' ' || line.buffer[position]=='\t')++position;
        if(position>=line.length || !line.buffer[position] || line.buffer[position]==';')continue;
        if(line.buffer[position]=='['){reader->line_number=prior_line;reader->text_file.seek(prior_cursor);return false;}
        unsigned int name_length=0;
        while(position+name_length<line.length && line.buffer[position+name_length]!='=' && line.buffer[position+name_length]!=';'){
            reader->text_name[name_length]=line.buffer[position+name_length];++name_length;
        }
        position+=name_length;
        while(name_length && (reader->text_name[name_length-1]==' ' || reader->text_name[name_length-1]=='\t'))--name_length;
        reader->text_name[name_length]=0;
        if(position>=line.length || line.buffer[position]!='='){reader->text_value[0]=0;return true;}
        do{++position;}while(line.buffer[position]==' ' || line.buffer[position]=='\t');
        unsigned int count=0;while(position+count<line.length && line.buffer[position+count]!=';')++count;
        while(count && (line.buffer[position+count-1]==' ' || line.buffer[position+count-1]=='\t'))--count;
        unsigned int offset=0;
        while(offset+4<=count){unsigned int word;__builtin_memcpy(&word,line.buffer+position+offset,4);__builtin_memcpy(reader->text_value+offset,&word,4);offset+=4;}
        while(offset<count){reader->text_value[offset]=line.buffer[position+offset];++offset;}
        reader->text_value[count]=0;return true;
    }
}
