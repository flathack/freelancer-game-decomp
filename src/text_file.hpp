#pragma once
#include "file_map.hpp"
struct LineParser32 { char buffer[1024];unsigned int length,position; };
struct TextFile32 : FileMap {unsigned int line_number;bool read_line(LineParser32&);};
#if __SIZEOF_POINTER__==4
static_assert(sizeof(TextFile32)==40 && sizeof(LineParser32)==1032,"Observed text reader/parser layout");
#endif

bool ReadTextLine(FileMap&,unsigned int&,LineParser32&);
