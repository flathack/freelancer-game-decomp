struct GoodInfo;
extern unsigned int CreateID(const char*);
namespace GoodList {
const GoodInfo* find_by_id(unsigned int);
const GoodInfo* find_by_nickname(const char* name){return find_by_id(CreateID(name));}
}
namespace Loadout {
unsigned int GetID(const char* name){return CreateID(name);}
}
