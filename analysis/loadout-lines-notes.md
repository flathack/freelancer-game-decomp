# Equipment and cargo loadout lines

Original common.dll exports at VA 0x06311c10 and 0x06311cd0. Equipment sets
equipped=true and count=1, obtains archetype ID from atoi(parameter0) or CreateID
when atoi is zero, sets hardpoint from parameter1 or cargo-bay cache, and updates
status from optional parameter2. Cargo sets equipped=false, obtains the same ID,
updates optional count, and processes parameter2 as hardpoint only if atof gives
zero. Nonzero or unordered (NaN) atof results return early, retaining old hardpoint,
status and temporary byte. Optional status and temporary raw AL byte follow.
The apparent GetAsteroidID call in raw output is just a DWORD dereference of the
CreateID result, not an archetype database lookup.

960 differential calls compare the full 32-byte descriptor, return AL and exact
sequence of external getter/atoi/atof/CreateID/interning calls. Cases cover every
combination of five empty flags, numeric/hash ID selection, zero/nonzero/NaN cargo
parameter2, random count/raw bool values and float range edges. Getter values,
CreateID and StringAlloc are controlled models. Integration with the reconstructed
reader/hash/cache, native CRT and machine-code matching remain unverified. Source
uses runtime getter adapters pending that integration rather than treating original
entry addresses as production dependencies.
