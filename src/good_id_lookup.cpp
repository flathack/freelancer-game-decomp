#include "loadout_tree.hpp"
struct GoodInfo;
extern "C" {Loadout::LookupTree GoodIDTree;}
namespace GoodList {
const GoodInfo* find_by_archetype(unsigned int);
const GoodInfo* find_by_id(unsigned int id){
 auto* candidate=GoodIDTree.head;auto* node=candidate->parent;
 while(node!=GoodIDTree.nil){if(node->key<id)node=node->right;else {candidate=node;node=node->left;}}
 if(candidate==GoodIDTree.head || id<candidate->key)return nullptr;
 return *reinterpret_cast<const GoodInfo* const*>(reinterpret_cast<const unsigned char*>(candidate)+16);
}
}
unsigned int Good2Arch(unsigned int id){
 const GoodInfo* good=GoodList::find_by_id(id);
 return good?*reinterpret_cast<const unsigned int*>(reinterpret_cast<const unsigned char*>(good)+80):0;
}
unsigned int Arch2Good(unsigned int id){
 const GoodInfo* good=GoodList::find_by_archetype(id);
 return good?*reinterpret_cast<const unsigned int*>(reinterpret_cast<const unsigned char*>(good)+72):0;
}
