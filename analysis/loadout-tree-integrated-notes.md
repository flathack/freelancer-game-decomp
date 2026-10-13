# Complete Loadout tree operation integration

One fixture DLL links tree initialization, unique insertion/duplicate selection,
node insertion/rebalancing, lookup, iterator, erase, bulk/recovery Free, Map copy/
assignment/destruction and SubObjectID classes. Each baseline call executes the
corresponding original export/internal helper against the original tree global.
The reconstructed context uses its own global, with heap addresses kept identical
by restoring controlled allocator state before each comparison.

60 independent sequences pass 7323 comparisons: 60 initializations, 2166 inserts,
4060 lookups, 917 erases and 120 Frees. Unlike earlier hand-seeded tree tests,
sentinels and all nodes are produced by actual original/rebuilt constructors and
insertion code. This includes original nil children initialized to null, arbitrary
insertion-produced red/black shapes, duplicates, missing-key lookups, deletions,
regular and zero-size recovery Free, and repeated Free after either path.

Entire 128KiB heap, full tree prefix, guarded output-result bytes, allocation/free
pointer sequences and allocator cursor agree. Constructor return pointer is
checked separately because the two tree globals have different image addresses.
Allocation remains a controlled success model, not native heap execution. Global
startup, failure/exception handling, complete Loadout file loading and instruction
matching remain incomplete. This is tree-component integration evidence, not a
whole-game completion claim.
