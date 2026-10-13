#define loadout_create_id loadout_unused_original_create_id
#include "loadout_reader_runtime.cpp"
#undef loadout_create_id
extern unsigned int CreateID(const char*);
extern "C" unsigned int loadout_create_id(const char* text){return CreateID(text);}
