#pragma once
namespace Loadout {
struct Map;
struct LookupNode {LookupNode *left,*parent,*right;unsigned int key;};
struct LookupTree {unsigned char allocator[4];LookupNode *head,*nil;unsigned char flags[4];unsigned int size;};
}
extern "C" Loadout::LookupTree LoadoutLookupTree;
