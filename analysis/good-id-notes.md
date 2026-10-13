# Goods ID lookup and ID conversions

Reconstructed GoodList::find_by_id at VA 0x06271730, Good2Arch at 0x06271850 and
Arch2Good at 0x062718b0. ID lookup searches its separate tree at 0x063fab80 and
returns the GoodInfo pointer stored in node+16 only for an exact unsigned key.
Good2Arch reads GoodInfo+0x50 from that lookup, or zero. Arch2Good uses the verified
archetype lookup and reads GoodInfo+0x48, or zero. These values come from metadata,
not the tree key. Full GoodInfo layout remains unrecovered beyond observed fields.

138,051 combined comparisons across 300 controlled tree shapes pass. Each queried
key exercises ID lookup, both conversions, prior archetype lookup and Cargo flag;
all raw Cargo flag bytes are also checked. ID/archetype indexes share a seeded
shape in this test while metadata ID fields are independently randomized, so
returning a key instead of the observed metadata value would fail. Exact pointers,
scalar words, raw AL and complete unchanged memory agree. Combined counts include
previous lookup/flag behavior, not only newly reconstructed logic.

Real Goods database construction/index population, cross-index real-data
consistency, native startup/runtime and exact instruction matching remain open.
