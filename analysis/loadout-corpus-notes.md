# Supplied loadout corpus comparison

The complete four loadout*.ini files supplied under DATA/SHIPS and DATA/SOLAR
are mapped into the x86 emulator. Original and reconstructed reader navigation
execute independently against the same mapped bytes. Header/value/name methods
compare their returns (AL for booleans) and the complete reader image after each
call. equip/cargo entries then enter original and reconstructed Loadout handlers,
comparing descriptor bytes, reader image and diagnostic/hash/intern call sequences.

All four files pass: 803 sections, 18,467 total entries, 16,087 equipment lines,
1,043 cargo lines (17,130 Loadout calls), and 38,544 reader navigation/name calls.
The existing 618 synthetic reader/Loadout cases run first and pass too. Per-file
paths, SHA256 hashes and counts are saved in loadout-corpus-x86-behavior.json.

This test seeds an initialized binary mapping; it does not acquire files through
the native OS. Reconstructed reader and Loadout code execute together, while
CreateID/StringAlloc and CRT functions retain controlled models. A matching
nickname/hash call sequence does not establish authentic resulting archetype IDs,
interned pointer identities or world-level loading. Reconstructed hash/cache
integration, native CRT/OS, full Loadout list allocation/lifecycle and byte matching
remain open. Counts describe this corpus and do not establish whole-game coverage.
