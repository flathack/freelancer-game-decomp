#pragma once
struct NumberPlan {const unsigned char* start;const unsigned char* end;const char* original;unsigned int base;int sign,kind,character;};
double ParseNumber(const char*);
extern "C" double parse_number_evaluate(const NumberPlan*);
extern "C" unsigned int parse_number_digit(unsigned int);
extern "C" int parse_number_tolower(int);
extern "C" double parse_number_atof(const char*);
extern "C" void parse_number_bad_digit(const char*);
