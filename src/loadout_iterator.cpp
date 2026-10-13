#include "loadout_tree.hpp"
static bool is_nil(const Loadout::LookupNode* node) {
 return reinterpret_cast<const unsigned char*>(node)[41]!=0;
}
extern "C" void __fastcall loadout_tree_next(Loadout::LookupNode** iterator) {
 Loadout::LookupNode* right=(*iterator)->right;
 if(is_nil(right)) {
  Loadout::LookupNode* parent=(*iterator)->parent;
  while(*iterator==parent->right){*iterator=parent;parent=parent->parent;}
  if((*iterator)->right!=parent)*iterator=parent;
 } else {
  while(!is_nil(right->left))right=right->left;
  *iterator=right;
 }
}
