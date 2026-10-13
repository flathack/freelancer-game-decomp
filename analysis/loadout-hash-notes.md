# Loadout / reader / CreateID integration

The hash-enabled integration fixture links reconstructed Loadout handlers,
all reader methods and CreateID/CFLIDMaker/CRC code. loadout_create_id calls
reconstructed CreateID directly; the original baseline executes its own original
hash code. The former constant hash-return model is removed. Allocation and
ASCII _strlwr remain modeled CRT dependencies, and StringAlloc/cargo-bay cache
remain controlled dependencies pending cache integration.

The full four-file Loadout corpus passes again: 17,130 equipment/cargo handler
comparisons, 38,544 navigation/name comparisons and 618 synthetic cases. Descriptor
archetype IDs now result from actual original/reconstructed hash calculations and
match, together with complete descriptor/reader bytes and intern/diagnostic call
sequences. Per-file hashes and counts are recorded in loadout-hash-x86-behavior.
The build report pins all compiled sources and the integrated DLL. Native locale,
heap and OS execution, reconstructed interning, full Loadout list lifecycle and
machine-code matching remain incomplete. This is not whole-game completion.
