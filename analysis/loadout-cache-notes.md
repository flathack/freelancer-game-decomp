# Loadout / reader / CreateID / StringAlloc integration

The cache-enabled fixture links the reconstructed Loadout line handlers, INI
reader, CreateID and StringAlloc red-black index/arena into one DLL. Its Loadout
adapter calls reconstructed StringAlloc directly. The original baseline executes
original hash/cache/reader code. Only allocator, string comparison/lowercasing,
conversion and diagnostics are modeled; cargo-bay global initialization still uses
a controlled pointer. No intern-result model remains.

All four supplied Loadout files pass: 17,130 handler calls, 38,544 navigation/name
calls and 618 synthetic cases. Descriptor pointers are normalized by their arena
offset because original/rebuilt DLLs own separate arenas. All other descriptor
bytes, full reader state, cache front/back/count values and every used arena byte
agree after each handler call. This establishes shared-cache reuse and output
contents under the existing CRT models. Full cache-tree topology was previously
verified separately, and is not re-compared here. Cargo-bay initialization,
shutdown integration, native CRT/OS and complete Loadout list lifecycle remain
unverified. Full game reconstruction and instruction matching remain incomplete.
