# Equipment vector/list searches

Reconstructed vector traversal at VA 0x0630a1f0, list mutable/const traversal at
0x0630a5b0/0x0630a5f0, and both ID find aliases at 0x0630a750. Vector prefix is
16 bytes (allocator, begin/end/capacity), list prefix 12 bytes (allocator, head,
size), list node 40 bytes (next/previous and 32-byte EquipDesc payload).

Traversal matches arch_id. A null previous pointer returns the first match.
A non-null previous pointer is recognized only within matching arch_id entries,
then traversal returns the following match. A foreign/nonmatching previous item
returns null, rather than simply starting after that address. ID find returns the
first 16-bit ID match, including zero and 65535; duplicate IDs are not rejected.

97,416 differential calls across five export names and 250 randomized empty/
nonempty collection shapes pass. Cases cover repeated archetypes and IDs, matching,
nonmatching and foreign previous pointers, unsigned archetype boundaries and
mutable/const aliases. Exact payload pointers and entire collection-memory guards
agree; neither method writes collection state. Alias names do not count as unique
algorithm bodies. Cargo merging, collection creation/mutation/ownership, malformed
pointer graphs, native execution and instruction matching remain open.
