# Goods nickname and Loadout ID access

GoodList::find_by_nickname (VA 0x06271790) hashes its input through CreateID then
performs Goods ID lookup. Loadout::GetID (VA 0x06311670) delegates to the same ID
maker/hash implementation. Both are now reconstructed using actual CreateID and
Goods ID search code, rather than a hash-return dependency model.

1017 differential accesses pass: 507 names through GetID and nickname lookup,
plus three missing-name lookups. Cases include null/empty inputs, case variants,
255-byte ASCII input and 500 deterministic random ASCII names. Original/rebuilt
hash words agree. A controlled balanced Goods tree contains these hash keys with
some null records; exact returned pointers agree for found/missing/null entries.
Case-folded collisions map to the same record, as expected from the hash result.

Allocator and ASCII CRT _strlwr remain modeled. Full real Goods database loading,
non-ASCII/native locale, ID-maker allocation-failure logging, native runtime and
exact instruction matching remain incomplete. This unit fixture does not yet
add these accessors to the full loader integration fixture export list.
