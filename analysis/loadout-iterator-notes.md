# Loadout tree iterator increment

Reconstructed internal helper VA 0x063126d0. Iterator is a pointer to a node
pointer in ECX; right-child nil flag is at node+41. For a real right subtree it
descends to the leftmost node. With no real right child it walks parent/right
relationships and preserves the original special head transition. It changes
only the iterator pointer, not tree nodes or ownership.

11,693 successor steps pass across 300 randomly shaped ordered trees. Every live
node is tested, including maximum-to-head transitions. Exact original/rebuilt
successor pointers and complete 64KiB tree-memory snapshots agree. There are no
modeled dependencies in this helper. End-iterator increment, invalid/cyclic trees,
native execution and instruction matching remain unverified. This is a prerequisite
for the still-open iterator-erase recovery branch of Free, not that branch itself.
