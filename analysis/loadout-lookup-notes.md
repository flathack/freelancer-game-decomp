# Loadout::Get

Original export VA 0x06311620 uses the internal lower-bound helper at 0x062fd190
on the tree at 0x063fc2a8. Tree prefix is allocator bytes, head pointer and nil
pointer. Node prefix is left/parent/right pointers and unsigned key; Map payload
starts at node+16. Head.parent holds the root. Search retains the first candidate
whose key is >= requested ID, returns null for end or strictly greater candidate,
and returns node+16 only for exact equality. Empty tree returns null.

28,354 differential lookups across 300 empty/randomly shaped ordered trees pass.
Zero, UINT_MAX, sign-boundary keys, existing IDs and random missing IDs compare
exact pointers. Complete tree-memory snapshots remain unchanged. Original/rebuilt
lookups execute actual code, with no lookup-result dependency model. Tree creation,
balancing, insertion/deletion, Map payload lifecycle and global initialization
are not reconstructed by this change. The new tree-prefix global is an explicit
integration placeholder; standalone native runtime and exact matching are open.
