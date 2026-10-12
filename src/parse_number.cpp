#include "parse_number.hpp"
static const unsigned char flags[128]={
0,0,0,0,0,0,0,0,0,64,64,0,0,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,128,0,32,0,0,128,0,0,0,128,128,0,128,0,128,56,56,56,56,56,56,56,56,56,56,0,0,128,128,128,0,0,51,51,51,51,51,51,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,35,0,0,0,128,32,0,53,53,53,53,53,53,37,37,37,37,37,37,37,37,37,37,37,37,37,37,37,37,37,37,37,37,0,128,0,128,0};
static const unsigned char digits[128]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4,5,6,7,8,9,0,0,0,0,0,0,0,10,11,12,13,14,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,10,11,12,13,14,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
extern "C" unsigned int parse_number_digit(unsigned int byte){byte&=255;return byte<128?digits[byte]:flags[byte-128];}
static bool hex(unsigned char ch){return (flags[ch&127]&16)!=0;}
static bool decimal(unsigned char ch){return (flags[ch&127]&8)!=0;}
double ParseNumber(const char* input){
    NumberPlan plan;plan.original=input;plan.base=10;plan.sign=1;plan.kind=0;plan.character=0;
    const unsigned char* start=reinterpret_cast<const unsigned char*>(input);
    if(*start=='+')++start;
    if(*start=='-'){plan.sign=-1;++start;}
    if(*start=='0'){while(*start=='0')++start;if(parse_number_tolower(static_cast<signed char>(*start))=='x'){++start;plan.base=16;}}
    const unsigned char* end=start;
    if(plan.base==16){while(hex(*end))++end;if(*end=='.')++end;while(hex(*end))++end;plan.kind=1;}
    else{
        if(*start=='\''){plan.kind=2;plan.character=static_cast<signed char>(start[1]);plan.start=start;plan.end=end;return parse_number_evaluate(&plan);}
        if(*start){
            while(hex(*end))++end;
            unsigned int count=static_cast<unsigned int>(end-start);
            if(count){
                int last=parse_number_tolower(static_cast<signed char>(end[-1]));
                if(count>1){if(last=='d'){--end;plan.base=10;}else if(last=='b'){--end;plan.base=2;}}
                else if(parse_number_tolower(*end=='h'))plan.base=16;
            }
            if(*end=='.'){++end;while(decimal(*end))++end;}
        }
        if(plan.base!=10)plan.kind=1;
    }
    plan.start=start;plan.end=end;return parse_number_evaluate(&plan);
}
