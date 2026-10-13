# GoodInfoList initialization and loader dependencies

Original constructor VA 0x062704f0, export `??0GoodInfoList@@QAE@XZ`. Storage extent 52 bytes: an owning pointer list at offset 0, a goods-ID index at offset 12 and an archetype index at offset 32. Each tree uses 24-byte nodes with color at offset 20 and nil flag at offset 21, unlike the Loadout tree's 44-byte nodes.

Allocation order is one 12-byte list sentinel, then nil/head pairs for each tree. List links point to its sentinel; tree heads have self left/right links and nil parents. Nil children are null. Counts and multi flags are zero; unwritten padding/payload bytes remain unchanged. Three allocator/comparator byte pairs derive from the same entry ESP minus 17 byte, preserved through a temporary assembly boundary.

768 comparisons cover all 256 opaque byte values and three object alignments, with complete guarded storage, seeded allocated heap, returned pointer and allocation sequence comparison. Native CRT, allocation exceptions, stack/storage aliasing and instruction matching remain open.

The original read_Good_block at VA 0x062708c0 reads nickname, category, equipment, free_ammo, names/info IDs, ship, price multipliers, jump distance, visual strings, hull, addon and combinable. It resolves equipment/ship IDs through an Archetype helper; equipment/commodity categories also read Equipment name/info metadata and invoke its virtual method at vtable offset 0x24. Hull resolves an existing GoodInfo via the goods ID index. Addons allocate EquipDesc nodes in low/mid/high lists. Unknown keys forward to GoodInfo's virtual reader. Therefore full real Goods loading requires Archetype lookup/metadata and virtual reader behavior as well as the two index insertions; empty stubs would not establish complete behavior.
