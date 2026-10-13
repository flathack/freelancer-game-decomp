# GoodInfo destruction

Original destructor VA `0x06270330`, reconstructed in `src/good_info_destroy.cpp` using a 192-byte storage view.

The destructor installs the GoodInfo vtable, clears the three lists at offsets 148, 160 and 172 in forward order, then frees their sentinels in reverse order. Each node is unlinked before its deallocation, and the list size is decremented after the allocator returns. Head pointers and sizes are reset after freeing each sentinel. Payload bytes and unrelated object fields remain untouched.

500 differential cases populate each list with zero to fifteen nodes and random size counters, including wrapping counters. The verifier compares complete guarded object/heap state and the same state at every deallocation callback, plus the free order. Freed memory is retained by the controlled allocator to expose write differences.

The vtable pointer is bound to the original image; native dispatch, full polymorphic layout, native CRT, exceptions and malformed/aliased lists remain unverified. This is a lifecycle reconstruction, not complete Goods database loading or exact code matching.
