#include "loadout_tree.hpp"
extern "C" { Loadout::LookupTree EquipmentArchetypeTree; }
extern "C" void archetype_lookup_error(unsigned int);
namespace Archetype {
struct Equipment;
Equipment* GetEquipment(unsigned int id) {
    auto* candidate=EquipmentArchetypeTree.head;auto* node=candidate->parent;
    while(node!=EquipmentArchetypeTree.nil) {
        if(node->key<id)node=node->right;
        else {candidate=node;node=node->left;}
    }
    if(candidate==EquipmentArchetypeTree.head || id<candidate->key) {
        archetype_lookup_error(id);return nullptr;
    }
    return *reinterpret_cast<Equipment**>(reinterpret_cast<unsigned char*>(candidate)+16);
}
}
