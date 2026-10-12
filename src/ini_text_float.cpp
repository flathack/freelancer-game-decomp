#include "ini_reader_values.hpp"
#include "string_index.hpp"
#include "parse_number.hpp"
extern "C" double __fastcall ini_values_pending_text_float(INI_Reader* reader,unsigned int index){return ParseNumber(StringIndex(reader->text_value,index));}
