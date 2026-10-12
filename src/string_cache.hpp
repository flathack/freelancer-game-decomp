#pragma once
struct CacheString { const char* value; void clear(); };
char* StringAlloc(const char*,bool);
struct StringCacheNode {
    StringCacheNode *left,*parent,*right;
    const char* key;
    char* value;
    unsigned char color,is_nil,padding[2];
};
struct StringCacheTree {
    unsigned char unknown[4];
    StringCacheNode *head,*nil;
    unsigned char multi,padding[3];
    unsigned int size;
};
extern char StringCacheArena[0x180000];
extern unsigned int StringCacheFront,StringCacheBack,StringCacheInternedCount,StringCachePrivateCount;
extern StringCacheTree* StringCacheIndex;
extern "C" void* stringcache_runtime_allocate(__SIZE_TYPE__);
extern "C" int stringcache_runtime_compare(const char*,const char*);
extern "C" void stringcache_runtime_overflow(unsigned int);
#if __SIZEOF_POINTER__==4
static_assert(sizeof(StringCacheNode)==24,"Original map node size");
static_assert(sizeof(StringCacheTree)==20,"Original tree object size");
#endif
void StringShutdown();
extern "C" void stringcache_runtime_free(void*);
