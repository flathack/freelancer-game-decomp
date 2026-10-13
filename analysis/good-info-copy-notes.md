# GoodInfo copy construction

Original export `??0GoodInfo@@QAE@ABU0@@Z`, VA 0x062640c0. Implemented alongside assignment to reuse reconstructed list insertion.

The copy constructor copies all 68 bytes of reference metadata/name storage at offset 4, without assignment's name truncation or length recalculation. It copies numeric fields and CacheString pointers, preserves destination padding, and allocates a new sentinel plus field-wise constructed nodes for each of three lists. List allocator bytes come from the source, and resulting sizes count the actual nodes rather than copying source counters. The final GoodInfo vtable is installed after list construction.

1,000 differential copy/destruction sequences compare guarded source and destination storage, a seeded 16 KiB heap, returned pointer, allocation/free order and final destruction state. Source lists contain zero to eleven nodes, arbitrary size counters and randomized payload/padding. The existing 1,000 assignment comparisons also pass after sharing the list helper.

Vtable pointers use original-image bindings; transient CacheString constructor writes are collapsed into final pointer assignment. Native virtual dispatch, native CRT, allocator exceptions, overlapping source/destination or shared lists, intermediate callback observations and instruction-identical compilation are not verified. Complete Goods loading remains unfinished.
