# Loadout node erase and Free recovery

Internal erase at VA 0x06312060 computes successor first, physically transplants
the in-order successor for two-child removal, swaps color bytes, repairs the
black-height through mirrored rotations/recoloring, and updates head/root/edge
pointers. Nil.parent is written when needed. Map vector and erased node are freed,
size decremented modulo 32 bits, and the successor written to the caller output.
Only color byte at node+40 changes; is_nil at +41 remains intact.

3600 sequential erases over 180 initially perfect black trees pass. Cases delete
all nodes in ascending, descending and shuffled order. Complete 64KiB tree/payload
memory, complete tree prefix, successor pointer and exact free sequence agree.
Sequences create additional colored shapes through the original/rebuilt balancing.
Insertion-generated arbitrary starting colors, native heap and exception failures,
malformed pointer graphs and instruction matching remain unverified.

Free's zero-size/nonempty fallback is now connected to reconstructed iterator and
erase. 180 recovery calls compare complete memory and free order against original.
The size underflows to -node_count modulo 32 bits, rather than being reset to zero;
this original behavior is preserved. The 300 regular Free cases still pass.
Full Loadout tree creation/insertion/loading and native runtime remain incomplete.
