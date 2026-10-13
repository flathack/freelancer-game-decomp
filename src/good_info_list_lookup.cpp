#include "loadout_tree.hpp"
struct GoodInfo;
struct GoodInfoListStorage { unsigned char bytes[52]; };
static const GoodInfo* lookup(const GoodInfoListStorage* p,unsigned offset,unsigned key) {
    const auto* tree=reinterpret_cast<const Loadout::LookupTree*>(p->bytes+offset);
    auto* candidate=tree->head;auto* node=candidate->parent;
    while(node!=tree->nil) {
        if(node->key<key)node=node->right;
        else {candidate=node;node=node->left;}
    }
    if(candidate==tree->head || key<candidate->key)return nullptr;
    return *reinterpret_cast<const GoodInfo* const*>(reinterpret_cast<const unsigned char*>(candidate)+16);
}
extern "C" const GoodInfo* __thiscall good_info_list_find_id(const GoodInfoListStorage*,unsigned) asm("?find_by_id@GoodInfoList@@QBEPBUGoodInfo@@I@Z");
extern "C" const GoodInfo* __thiscall good_info_list_find_id(const GoodInfoListStorage* p,unsigned key) {return lookup(p,12,key);}
extern "C" const GoodInfo* __thiscall good_info_list_find_archetype(const GoodInfoListStorage*,unsigned) asm("?find_by_archetype@GoodInfoList@@QBEPBUGoodInfo@@I@Z");
extern "C" const GoodInfo* __thiscall good_info_list_find_archetype(const GoodInfoListStorage* p,unsigned key) {return lookup(p,32,key);}
