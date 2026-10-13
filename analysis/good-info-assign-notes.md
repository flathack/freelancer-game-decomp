# GoodInfo assignment

Original export `??4GoodInfo@@QAEAAU0@ABU0@@Z`, VA 0x06264300. The reconstruction uses a storage view pending the full class declaration.

The name is scanned, truncated to 63 bytes, terminated and its stored length updated. Numeric and CacheString pointer fields are copied individually. The vtable and padding remain untouched. Each of the three lists reuses existing nodes with a complete 32-byte payload copy, removes surplus destination nodes, and appends missing source nodes using field-wise EquipDesc construction that preserves padding. Self-assignment skips list mutation. Final fields at offsets 184 and 188 are copied last.

Validation: 1,000 differential assignments with random names (including truncation), zero to eleven nodes per list, arbitrary counters and 100 self-assignments. Full guarded objects and 16 KiB heap, returned pointer and allocation/free sequence match. Allocations are deterministic and preserve seeded padding.

Native heap/CRT, partially overlapping objects or shared lists, allocation exceptions and exact instruction matching remain unverified. This does not complete Goods loading.
