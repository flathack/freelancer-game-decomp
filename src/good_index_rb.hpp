#pragma once
#include "loadout_tree.hpp"
using Node=Loadout::LookupNode;
using Tree=Loadout::LookupTree;
static unsigned char& color(Node* n){return reinterpret_cast<unsigned char*>(n)[20];}
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
