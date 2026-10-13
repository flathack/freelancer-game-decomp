#include "loadout_tree.hpp"
#include "loadout_map.hpp"
struct LoadoutPair {unsigned int key;Loadout::Map value;};
struct LoadoutInsertResult {Loadout::LookupNode* node;unsigned char inserted;};
extern "C" void __thiscall loadout_tree_insert(Loadout::LookupTree*,Loadout::LookupNode**,Loadout::LookupNode*,Loadout::LookupNode*,const LoadoutPair*);
extern "C" void __thiscall loadout_tree_emplace(Loadout::LookupTree* tree,LoadoutInsertResult* result,const LoadoutPair* value){
 using Node=Loadout::LookupNode;
 Node* parent=tree->head;Node* cursor=parent->parent;bool left=true;
 while(cursor!=tree->nil){parent=cursor;left=value->key<cursor->key;cursor=left?cursor->left:cursor->right;}
 if(!tree->flags[0]){
  Node* candidate=parent;
  if(left && parent!=tree->head->left){
   if(candidate->left!=tree->nil){candidate=candidate->left;while(candidate->right!=tree->nil)candidate=candidate->right;}
   else {Node* up=candidate->parent;while(candidate==up->left){candidate=up;up=up->parent;}candidate=up;}
  }
  if(!(left && parent==tree->head->left) && value->key<=candidate->key){result->inserted=0;result->node=candidate;return;}
 }
 Node* inserted;loadout_tree_insert(tree,&inserted,cursor,parent,value);
 result->inserted=1;result->node=inserted;
}
