# Loadout / reader / CreateID / StringAlloc integration

The cache-enabled fixture links the reconstructed Loadout line handlers, INI
reader, CreateID and StringAlloc red-black index/arena into one DLL. Its Loadout
adapter calls reconstructed StringAlloc directly. The original baseline executes
original hash/cache/reader code. Only allocator, string comparison/lowercasing,
conversion and diagnostics are modeled. Cargo-bay initialization now runs the
compiled CRT callback, which interns BAY through reconstructed StringAlloc.
The baseline initializes its cargo-bay pointer through original StringAlloc. No intern-result model remains.

All four supplied Loadout files pass: 17,130 handler calls, 38,544 navigation/name
calls and 618 synthetic cases. Descriptor pointers are normalized by their arena
offset because original/rebuilt DLLs own separate arenas. All other descriptor
bytes, full reader state, cache front/back/count values and every used arena byte
agree after each handler call. This establishes shared-cache reuse and output
contents under the existing CRT models. Full cache-tree topology was previously
verified separately, and is not re-compared here. Shutdown integration, native CRT/OS and complete Loadout list lifecycle remain
unverified. Full game reconstruction and instruction matching remain incomplete.

The callback count is recorded in the report. Internal hardpoint pointers now
normalize to the actual BAY arena offset rather than a controlled external
pointer. All four-file corpus and synthetic comparisons pass after this change.
The callback is executed by the emulator harness, not by a native Windows loader.
