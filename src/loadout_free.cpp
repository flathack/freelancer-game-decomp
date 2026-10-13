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
namespace Loadout {
void Free() {
 // Valid empty trees have head.left==head. The original has an iterator-erase
 // fallback for inconsistent zero-size/nonempty trees; that recovery remains open.
 if(!LoadoutLookupTree.size)return;
 release_subtree(LoadoutLookupTree.head->parent);
 LoadoutLookupTree.head->parent=LoadoutLookupTree.nil;
 LoadoutLookupTree.size=0;
 LoadoutLookupTree.head->left=LoadoutLookupTree.head;
 LoadoutLookupTree.head->right=LoadoutLookupTree.head;
}
}
