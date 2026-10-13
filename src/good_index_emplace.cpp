#include "loadout_tree.hpp"
struct GoodIndexPair {unsigned int key;void* value;};
struct GoodIndexResult {Loadout::LookupNode* node;unsigned char inserted;};
extern "C" Loadout::LookupNode** __thiscall good_index_insert(Loadout::LookupTree*,Loadout::LookupNode**,Loadout::LookupNode*,Loadout::LookupNode*,const GoodIndexPair*);
extern "C" GoodIndexResult* __thiscall good_index_emplace(Loadout::LookupTree* tree,GoodIndexResult* result,const GoodIndexPair* value){
 using Node=Loadout::LookupNode;
 Node* parent=tree->head;Node* cursor=parent->parent;bool left=true;
 while(cursor!=tree->nil){parent=cursor;left=value->key<cursor->key;cursor=left?cursor->left:cursor->right;}
 if(!tree->flags[0]){
  Node* candidate=parent;
  if(left && parent!=tree->head->left){
   if(candidate->left!=tree->nil){candidate=candidate->left;while(candidate->right!=tree->nil)candidate=candidate->right;}
   else {Node* up=candidate->parent;while(candidate==up->left){candidate=up;up=up->parent;}candidate=up;}
  }
  if(!(left && parent==tree->head->left) && value->key<=candidate->key){result->inserted=0;result->node=candidate;return result;}
 }
 Node* inserted;good_index_insert(tree,&inserted,cursor,parent,value);
 result->inserted=1;result->node=inserted;return result;
}
