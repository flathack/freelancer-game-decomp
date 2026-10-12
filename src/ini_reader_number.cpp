#include "ini_reader.hpp"
extern "C" int ini_number_tolower(int);
bool INI_Reader::is_number(const char* text) const {
    bool exponent=false,sign_used=true,point=false;
    if (*text=='-' || *text=='+') ++text;
    if (*text=='.') {point=true;++text;}
    if (*text=='\'') {
        ++text;
        if (ini_number_tolower(static_cast<signed char>(*text))>'`' &&
            ini_number_tolower(static_cast<signed char>(*text))<'{' && text[1]=='\'') return true;
    }
    if (*text=='0' && ini_number_tolower(static_cast<signed char>(text[1]))=='x') {
        text+=2;
        while (*text) {
            if (*text<'0' || *text>'9') {
                signed char lower=static_cast<signed char>(ini_number_tolower(static_cast<signed char>(*text)));
                if(lower<'a' || lower>'f')return false;
            }
            ++text;
        }
        return true;
    }
    if (*text<'0' || *text>'9') return false;
    while (*++text) {
        if (*text>='0' && *text<='9')continue;
        if (!sign_used && (*text=='+' || *text=='-')) {sign_used=true;continue;}
        if (!point && *text=='.') {point=true;continue;}
        if (exponent || ini_number_tolower(static_cast<signed char>(*text))!='e')return false;
        exponent=true;sign_used=false;
    }
    return true;
}
