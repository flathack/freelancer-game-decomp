#include "loadout_tree.hpp"
#include "loadout_map.hpp"
static void release_subtree(Loadout::LookupNode* node) {
 while(node!=LoadoutLookupTree.nil){
  release_subtree(node->right);
  Loadout::LookupNode* left=node->left;
  reinterpret_cast<Loadout::Map*>(reinterpret_cast<unsigned char*>(node)+16)->~Map();
  loadout_map_free(node);node=left;
 }
}
extern "C" void __fastcall loadout_tree_next(Loadout::LookupNode**);
extern "C" void __thiscall loadout_tree_erase(Loadout::LookupTree*,Loadout::LookupNode**,Loadout::LookupNode*);
namespace Loadout {
void Free() {
 if(!LoadoutLookupTree.size){
  LookupNode* current=LoadoutLookupTree.head->left;
  while(current!=LoadoutLookupTree.head){
   LookupNode* node=current;loadout_tree_next(&current);
   LookupNode* ignored;loadout_tree_erase(&LoadoutLookupTree,&ignored,node);
  }
  return;
 }
 release_subtree(LoadoutLookupTree.head->parent);
 LoadoutLookupTree.head->parent=LoadoutLookupTree.nil;
 LoadoutLookupTree.size=0;
 LoadoutLookupTree.head->left=LoadoutLookupTree.head;
 LoadoutLookupTree.head->right=LoadoutLookupTree.head;
}
}
