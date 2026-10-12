# String cache reconstruction

Original exported `StringAlloc`: common.dll RVA 0xd3bd0. CacheString::clear is
at 0xd3d60. Original arena VA 0x06409810 has 0x180000 (1.5 MiB) bytes, with
front cursor starting at 1, back cursor at capacity, normal count at 1 and
private count at zero. Byte zero is the shared empty string.

`src/string_cache.cpp` reconstructs forward arena allocation for interned strings,
backward allocation for private copies, case-insensitive lookup, table insertion
and red-black rotations/recoloring. It models the observed 20-byte tree and
24-byte nodes on x86, including separate nil and head sentinels. Runtime allocation,
comparison and logging are binding interfaces; successful allocator and ASCII
stricmp substitutes are used in tests. No STL container is substituted for the
observed tree layout. `CacheString::clear` stores the shared empty-string pointer.

The original first spelling of a string is retained. Subsequent case-insensitive
hits return the same pointer without consuming arena space. Private copies are
not interned and consume back space for every call. Both modes account for the
terminating byte, and both overflow paths return the shared empty-string pointer
and report the original diagnostic line (0xa9 / 0xb9).

`tests/verify_string_cache_x86.py` builds a Windows x86 DLL and compares 407
sequential requests against the original instructions. Returned arena offsets,
actual text, both cursors, both counts, complete tree shape, colors, values,
parent relationships, and head min/max pointers agree. Eight controlled free-space
boundary cases check exact-fit and overflow behavior; clear() is also checked.
Original and reconstructed pointers are normalized to their respective arena
base addresses. Unwritten padding and tree allocator bytes are not asserted.
The tests do not establish all possible string/order/locale behavior.

`EquipDesc::CARGO_BAY_HP_NAME` now initializes through StringAlloc("BAY",false).
The original initializer at VA 0x06309a60 and reconstructed CRT callback both run
in the equipment test; the string content and field identity are checked.
The previous fake BAY pointer and constant-provider fixture have been removed.
SUBOBJ_ID_NONE is defined from the original readonly exported value (zero).

Remaining work: production allocator/CRT/logging bindings, locale/non-ASCII
comparison, allocation-failure/SEH semantics, index destruction and broader
CacheString APIs. Exact instruction matching and a full game rebuild remain open.

Run: `.venv/bin/python tests/verify_string_cache_x86.py`.
Commands, hashes and counts are in `analysis/stringcache-x86-behavior.json`.
