# Loadout / reconstructed reader integration

The optional Loadout build of build_ini_fixture links the 39 reader methods plus
ReadEquipLine/ReadCargoLine, with adapters calling reconstructed reader string,
empty, float, integer and boolean getters directly. Production Loadout source is
unchanged. CreateID/StringAlloc and cargo-bay cache initialization remain controlled
dependencies; their original-image addresses are confined to the test adapter.

618 differential calls compare both Loadout exports against original common.dll
using nine text value lists and 300 binary parameter lists. BINI tags 0..3,
counts 0..5, numeric/nickname IDs, numeric/named hardpoints, NaNs, status and raw
boolean bytes are included. Complete descriptor bytes, complete reader bytes and
diagnostic/hash/intern call sequences agree under CRT models. The reader getters
execute reconstructed code rather than scripted return values. Acquisition and
line iteration are not part of this test. Real loadout-file corpus, reconstructed
hash/cache integration, native CRT and exact instruction matching remain open.
