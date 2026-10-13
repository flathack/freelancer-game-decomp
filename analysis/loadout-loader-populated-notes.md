# Populated Loadout loader comparison

16 paired original/rebuilt Load calls (32 binary invocations) pass across four
synthetic text files, both bool argument values, and two consecutive loads in each
context. Tests cover numeric/nickname archetypes, internal/external hardpoints,
status, Cargo count/temporary fields, multiple sections, unrelated sections,
repeated nickname replacement and repeated whole-file loading. Actual reader,
Loadout loader/tree/vector, CreateID and StringAlloc code execute in both images.

Compared results are return tree-size delta and ordered semantic Map snapshots:
key, Map ID, Equipment counter, every defined Equipment field, and hardpoint text.
Both flags yield identical outcomes, supporting the disassembly finding that the
bool argument is unused. Replacement clears Equipment entries and resets IDs.
Raw object padding, opaque allocator bytes, heap pointers and allocation traces
are not compared here, because stack layouts and image arenas differ. This is not
a full heap-equivalence claim. The Goods lookup tree is controlled empty, so these
cases do not yet exercise Goods-driven combining. CRT/OS/heap remain modeled.

The loader fixture exports 48 original method names plus explicit test-only data
and initialization helpers, now counted separately. Real Loadout corpus, Goods
metadata, malformed ordering and native runtime are still pending. The earlier
64 empty/error comparisons remain separately scoped.
