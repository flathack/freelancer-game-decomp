# Full supplied Loadout loader corpus

All four supplied loadout*.ini files now enter original and reconstructed
Loadout::Load, including file acquisition through modeled APIs, BINI recognition,
reader iteration, nickname hashes, Map insertion, Equipment vectors/IDs, line
parsers and cleanup. Each comparison starts with an initialized empty Loadout
tree, controlled empty Goods tree and independently initialized original/rebuilt
hash/cache contexts. The bool argument is zero; its two-value behavior is already
covered by synthetic tests.

Four paired full-file calls pass (eight binary invocations):
- SHIPS/loadouts.ini: 358 Maps, 7980 Equipment/Cargo entries.
- SHIPS/loadouts_special.ini: 75 Maps, 1552 entries.
- SHIPS/loadouts_utility.ini: 61 Maps, 1095 entries.
- SOLAR/loadouts.ini: 309 Maps, 6503 entries.
Total: 803 Maps and 17,130 entries. Per-file paths/SHA256/lengths, return deltas and
counts are recorded in loadout-loader-corpus-x86-behavior.json. Actual reconstructed
reader/tree/vector/CreateID/StringAlloc code executes, not scripted loader results.

Comparison covers return tree-size delta and sorted semantic Map snapshots:
Map key/ID/counter, Equipment IDs/archetypes, hardpoint text, status bits, count,
equipped/temporary bytes, owner and unknown_00 field. It does not compare raw
heap pointers/padding, full tree topology or allocation traces in this suite.
CRT/heap/file mapping/conversion dependencies remain controlled models. Goods
metadata is empty, so Goods-driven merging is not exercised here. Files are
loaded separately, not cumulatively; cross-file replacement remains open. Native
execution, exception paths, malformed record ordering and exact machine-code
matching remain unverified. These results do not establish full game completion.
