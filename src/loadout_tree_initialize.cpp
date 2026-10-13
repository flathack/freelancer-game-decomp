#include "loadout_tree.hpp"
extern "C" void* loadout_map_allocate(unsigned int);
extern "C" Loadout::LookupTree* __thiscall loadout_tree_initialize(Loadout::LookupTree* tree,const unsigned char* comparator,const unsigned char* allocator){
 tree->allocator[0]=*allocator;tree->allocator[1]=*comparator;tree->flags[0]=0;
 auto* nil=static_cast<Loadout::LookupNode*>(loadout_map_allocate(44));
 nil->parent=nullptr;reinterpret_cast<unsigned char*>(nil)[40]=1;reinterpret_cast<unsigned char*>(nil)[41]=1;
 tree->nil=nil;nil->left=nullptr;nil->right=nullptr;
 auto* head=static_cast<Loadout::LookupNode*>(loadout_map_allocate(44));
 head->parent=nil;reinterpret_cast<unsigned char*>(head)[40]=0;reinterpret_cast<unsigned char*>(head)[41]=0;
 tree->head=head;head->left=head;head->right=head;tree->size=0;
 return tree;
}
