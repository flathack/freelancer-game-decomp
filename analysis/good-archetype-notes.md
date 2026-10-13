# Goods archetype lookup and Cargo combination decision

GoodList::find_by_archetype (VA 0x062717f0) performs unsigned exact-key lookup on
its tree at 0x063fab94. Node+16 stores a GoodInfo pointer, unlike Loadout nodes
which embed a Map at that offset. Missing key, strictly greater lower-bound, or
null stored pointer returns null. arch_is_combinable (VA 0x0630a810) returns zero
for null and otherwise the raw byte at GoodInfo+0x70. It does not normalize to 1.
The ABI reconstruction uses an unsigned-byte return under the original bool symbol.

57,012 differential calls across 300 empty/random tree shapes pass. Key boundaries,
missing keys, null Goods pointers, randomized metadata bytes and all 256 raw flag
bytes are covered. Exact GoodInfo pointers and AL results agree; complete tree/
Goods memory snapshots remain unchanged. Actual original/reconstructed lookup
instructions execute without modeled lookup results. GoodInfo is deliberately
forward-declared; only the observed flag offset is accessed, without inventing its
unrecovered full class layout. Goods database creation, global startup, loader
integration, native runtime and machine-code matching remain unverified.
