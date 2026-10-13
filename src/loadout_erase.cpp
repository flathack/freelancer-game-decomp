#include "loadout_tree.hpp"
#include "loadout_map.hpp"
extern "C" void __fastcall loadout_tree_next(Loadout::LookupNode**);
using Node=Loadout::LookupNode;
using Tree=Loadout::LookupTree;
static unsigned char& color(Node* n){return reinterpret_cast<unsigned char*>(n)[40];}
static void rotate_left(Tree* t,Node* x){
 Node* y=x->right;x->right=y->left;if(y->left!=t->nil)y->left->parent=x;
 y->parent=x->parent;
 if(x==t->head->parent)t->head->parent=y;
 else if(x==x->parent->left)x->parent->left=y;else x->parent->right=y;
 y->left=x;x->parent=y;
}
static void rotate_right(Tree* t,Node* x){
 Node* y=x->left;x->left=y->right;if(y->right!=t->nil)y->right->parent=x;
 y->parent=x->parent;
 if(x==t->head->parent)t->head->parent=y;
 else if(x==x->parent->right)x->parent->right=y;else x->parent->left=y;
 y->right=x;x->parent=y;
}
extern "C" void __thiscall loadout_tree_erase(Tree* t,Node** out,Node* z){
 Node* next=z;loadout_tree_next(&next);
 Node* y=z;Node* x;
 if(y->left==t->nil)x=y->right;
 else if(y->right==t->nil)x=y->left;
 else {y=y->right;while(y->left!=t->nil)y=y->left;x=y->right;}
 if(y!=z){
  z->left->parent=y;y->left=z->left;
  if(y==z->right)x->parent=y;
  else {x->parent=y->parent;y->parent->left=x;y->right=z->right;z->right->parent=y;}
  if(t->head->parent==z)t->head->parent=y;
  else if(z->parent->left==z)z->parent->left=y;else z->parent->right=y;
  y->parent=z->parent;unsigned char c=color(y);color(y)=color(z);color(z)=c;y=z;
 }else{
  x->parent=y->parent;
  if(t->head->parent==z)t->head->parent=x;
  else if(z->parent->left==z)z->parent->left=x;else z->parent->right=x;
  if(t->head->left==z){if(z->right==t->nil)t->head->left=z->parent;else {Node* n=x;while(n->left!=t->nil)n=n->left;t->head->left=n;}}
  if(t->head->right==z){if(z->left==t->nil)t->head->right=z->parent;else {Node* n=x;while(n->right!=t->nil)n=n->right;t->head->right=n;}}
 }
 if(color(y)==1){
  while(x!=t->head->parent && color(x)==1){
   if(x==x->parent->left){
    Node* w=x->parent->right;
    if(color(w)==0){color(w)=1;color(x->parent)=0;rotate_left(t,x->parent);w=x->parent->right;}
    if(color(w->left)==1 && color(w->right)==1){color(w)=0;x=x->parent;}
    else {
     if(color(w->right)==1){color(w->left)=1;color(w)=0;rotate_right(t,w);w=x->parent->right;}
     color(w)=color(x->parent);color(x->parent)=1;color(w->right)=1;rotate_left(t,x->parent);break;
    }
   }else{
    Node* w=x->parent->left;
    if(color(w)==0){color(w)=1;color(x->parent)=0;rotate_right(t,x->parent);w=x->parent->left;}
    if(color(w->right)==1 && color(w->left)==1){color(w)=0;x=x->parent;}
    else {
     if(color(w->left)==1){color(w->right)=1;color(w)=0;rotate_left(t,w);w=x->parent->left;}
     color(w)=color(x->parent);color(x->parent)=1;color(w->left)=1;rotate_right(t,x->parent);break;
    }
   }
  }
  color(x)=1;
 }
 reinterpret_cast<Loadout::Map*>(reinterpret_cast<unsigned char*>(y)+16)->~Map();
 loadout_map_free(y);--t->size;*out=next;
}
