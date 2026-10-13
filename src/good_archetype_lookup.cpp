#include "loadout_tree.hpp"
struct GoodInfo;
extern "C" { Loadout::LookupTree GoodArchetypeTree; }
namespace GoodList {
const GoodInfo* find_by_archetype(unsigned int id){
 auto* candidate=GoodArchetypeTree.head;auto* node=candidate->parent;
 while(node!=GoodArchetypeTree.nil){if(node->key<id)node=node->right;else{candidate=node;node=node->left;}}
 if(candidate==GoodArchetypeTree.head || id<candidate->key)return nullptr;
 return *reinterpret_cast<const GoodInfo* const*>(reinterpret_cast<const unsigned char*>(candidate)+16);
}
}
extern "C" unsigned char arch_is_combinable_raw(unsigned int)
 __asm__("?arch_is_combinable@@YA_NI@Z");
extern "C" unsigned char arch_is_combinable_raw(unsigned int id){
 const GoodInfo* good=GoodList::find_by_archetype(id);
 return good?reinterpret_cast<const unsigned char*>(good)[112]:0;
}
