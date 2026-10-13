namespace Loadout {
struct Map;
struct LookupNode {LookupNode *left,*parent,*right;unsigned int key;};
struct LookupTree {unsigned char allocator[4];LookupNode *head,*nil;};
}
extern "C" { Loadout::LookupTree LoadoutLookupTree; }
namespace Loadout {
const Map* Get(unsigned int id) {
    LookupNode* candidate=LoadoutLookupTree.head;
    LookupNode* current=candidate->parent;
    while(current!=LoadoutLookupTree.nil) {
        if(current->key<id)current=current->right;
        else {candidate=current;current=current->left;}
    }
    if(candidate==LoadoutLookupTree.head || id<candidate->key)return nullptr;
    return reinterpret_cast<const Map*>(reinterpret_cast<const unsigned char*>(candidate)+16);
}
}
