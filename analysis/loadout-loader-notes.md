# Loadout file loader: initial reconstruction

The reconstructed export Loadout::Load at VA 0x06311680 now connects the reader,
nickname CreateID, Map construction/copy/emplace, Equipment defaults, equipment/
cargo line parsers, vector append/merge, Cargo combination lookup and ID counters.
Existing nickname insertion returns inserted=false; its stored list is cleared by
end=begin (capacity is retained), and Equipment IDs reset. New entries set Map.id
to the nickname hash. Cargo combination is disabled for non-internal hardpoints.
The return is tree-size delta. Reader cleanup runs at function exit.

Disassembly shows no read of the exported bool argument in this installation.
The branch at 0x063117ee tests the insertion result byte, not that argument. The
reconstruction deliberately ignores the bool. Missing open logs severity 0x100001,
Loadout.cpp line 0xb3, filename. It opens the reader with fatal=false.

The loader-enabled fixture links 48 original method/export names, including the
39 reader methods. Stack probing is bound to the pinned original CRT in the test
adapter. Equipment default fields mirror the previously reconstructed constructor;
the isolated fixture supplies only that constructor, avoiding unrelated equipment
lookup dependencies. This is not a standalone native replacement DLL.

64 original/rebuilt Load calls pass for empty input, an unrelated text section,
bare BINI header and zero-entry BINI, acquisition/mapping failures and both bool
values. Return delta, modeled heap ownership, resource/callback events and exact
file-error diagnostic arguments agree. This verifies actual loader entry/open/
parse/cleanup behavior, not populated Loadout handling. Populated file comparisons,
Goods/startup integration, opaque stack allocator bytes, native CRT/OS, exception
paths and exact instruction matching remain open. The newly implemented populated
control flow is provisional until differential tests establish it.

Full-file semantic comparisons have since passed for all four supplied Loadout
INIs (803 Maps / 17130 Equipment entries); see loadout-loader-corpus-notes.md.
Those runs retain a controlled empty Goods database and do not compare raw heap
layout or native runtime. Goods-driven combining remains pending.
