# GoodInfo default initialization

Original common.dll constructor: VA `0x062701e0`. The reconstructed initializer operates on a 192-byte storage view; it does not yet declare a complete polymorphic GoodInfo class.

The constructor initializes reference metadata, five empty CacheString pointers, three circular list sentinels (40 bytes each), IDs, flags and numeric defaults. Unwritten bytes remain unchanged. All three list allocator bytes originate from entry ESP minus 17; a temporary assembly boundary preserves this observed ABI behavior. CreateID(NULL) uses the reconstructed hash implementation.

Validation: 768 original/reconstructed constructor comparisons, covering every allocator byte and three object alignments. Tests compare the guarded object, allocated heap, returned pointer and allocation sequence, including CRC initialization.

The fixture binds vtable addresses and the empty-string pointer to the original image. It does not establish native vtable dispatch, a complete C++ class, native CRT behavior, allocation failures, intermediate callback observations, stack/storage aliasing or instruction-identical compilation. Goods database population remains unfinished.
