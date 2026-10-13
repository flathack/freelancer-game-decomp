#include "loadout_rb.hpp"
#include "loadout_map.hpp"
inline void* operator new(__SIZE_TYPE__,void* p) noexcept{return p;}
struct LoadoutPair {unsigned int key;Loadout::Map value;};
extern "C" void __thiscall loadout_tree_insert(Tree* t,Node** out,Node* marker,Node* parent,const LoadoutPair* value){
 Node* added=static_cast<Node*>(loadout_map_allocate(44));
 added->parent=parent;color(added)=0;reinterpret_cast<unsigned char*>(added)[41]=0;
 added->left=added->right=t->nil;added->key=value->key;
 new(reinterpret_cast<unsigned char*>(added)+16) Loadout::Map(value->value);
 ++t->size;
 if(parent==t->head || marker!=t->nil || value->key<parent->key){
  parent->left=added;
  if(parent==t->head){t->head->parent=added;t->head->right=added;}
  else if(parent==t->head->left)t->head->left=added;
 }else{parent->right=added;if(parent==t->head->right)t->head->right=added;}
 Node* x=added;
 while(x!=t->head->parent && color(x->parent)==0){
  if(x->parent==x->parent->parent->left){
   Node* uncle=x->parent->parent->right;
   if(color(uncle)==0){color(x->parent)=1;color(uncle)=1;color(x->parent->parent)=0;x=x->parent->parent;}
   else {
    if(x==x->parent->right){x=x->parent;rotate_left(t,x);}
    color(x->parent)=1;color(x->parent->parent)=0;rotate_right(t,x->parent->parent);
   }
  }else{
   Node* uncle=x->parent->parent->left;
   if(color(uncle)==0){color(x->parent)=1;color(uncle)=1;color(x->parent->parent)=0;x=x->parent->parent;}
   else {
    if(x==x->parent->left){x=x->parent;rotate_right(t,x);}
    color(x->parent)=1;color(x->parent->parent)=0;rotate_left(t,x->parent->parent);
   }
  }
 }
 color(t->head->parent)=1;*out=added;
}
