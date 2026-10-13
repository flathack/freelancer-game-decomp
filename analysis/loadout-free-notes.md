# Loadout tree bulk release

Reconstructed the regular Free path at VA 0x06311b50 and subtree release helper
0x06312440. The tree prefix now includes flags and size at offsets 12 and 16.
Release visits each node's right subtree, destroys its Map payload at node+16,
frees the node, then follows the left chain. Map destruction frees its vector
begin pointer even when null and clears the vector pointer triplet. Head and nil
remain allocated. After nonempty bulk release head.parent=nil, size=0, and
head.left/head.right point to head. Valid empty trees return without other writes.

300 complete original/rebuilt Free comparisons pass across empty/randomly shaped
trees. Entire 64KiB guarded tree/payload memory, tree globals and exact free-pointer
sequence agree; the allocator free operation is modeled without poisoning memory.
The refactored lookup still passes 28,354 comparisons. Tree insertion/balancing,
native heap and exact matching remain open.

The zero-size/nonempty iterator-erase fallback has since been reconstructed and
verified separately in 180 comparisons; see loadout-erase-notes.md. This regular
suite retains its 300 well-formed-tree scope. Full Loadout creation/insertion,
native runtime and whole-game reconstruction remain incomplete.
