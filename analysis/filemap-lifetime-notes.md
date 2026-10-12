# FileMap completion of method implementation and external bindings

All 18 original FileMap export names now link from reconstructed source. This is
component implementation progress, not completion of Freelancer or exact matching.
The six added methods are copy constructor, assignment, destructor, handoff_to,
OS-backed open and close. The 16-byte filename layout is retained; the original
MSVCP60 Grow/Split/Tidy/Assign methods remain external CRT dependencies.

## Observed ownership and filename behavior

Nonempty filename copies share the buffer when its byte reference count is below
254, incrementing that count; 254 and 255 use a grown copy. Self-assignment invokes
Split and preserves resources. Closing a shared filename detaches it before
clearing the name, so another object's name stays valid. Destructor closes the
resources and then releases filename storage.

Raw file/mapping/data fields are shallow-copied. Handoff transfers them and clears
only source handles/data, retaining source length/position. Handoff to self clears
its own handles/data and leaves length/position; this original behavior is retained.
Overwriting a receiver does not implicitly close its previous resources.

Open uses the original CreateFileA access/share/disposition arguments, creates a
readonly mapping and view, and cleans up in original order on acquisition failure.
Failure after GetFileSize but before a valid view can retain a nonzero length,
which is explicitly checked rather than normalized away.

## Differential validation

`verify_file_map_lifetime_x86.py` passes 101 comparisons of original/rebuilt x86
methods. Checks include defined object state, COW sharing/detachment, reference
counts 0/1/253/254/255, Win32 arguments and call order, all three acquisition failure
stages, repeated close/destructor, assignment/handoff and self operations.

External MSVCP60 operations are a **semantics model**, not the actual CRT. Allocator,
free/memmove and Win32 file APIs are controlled substitutes. The tests therefore
verify FileMap's own code under those imports, not authentic CRT allocation-size,
SEH, heap failure or real Windows mapping behavior. The memory-reader check still
passes all 3,298 cases after integration.

## Named-import Windows build

`src/runtime/file_map_windows.cpp` binds to genuine named MSVCRT/MSVCP60/KERNEL32
imports, with original mangled private string symbols and data import. It contains
no fixed original-image addresses. `tools/build_filemap_windows.py` generates
import libraries from the baseline's names and builds
`build/filemap-windows/freelancer-filemap.dll`. All 18 exports and 13 imports are
checked against the expected baseline-derived sets.

The production-binding DLL also passes the 101 emulator comparisons after its IAT
is supplied with the same explicit external models. That verifies wrapper ABI and
argument passing, not actual Windows execution. The component DLL has no entry
point because it has no dynamic global initializers. It is not a drop-in common.dll.

```sh
.venv/bin/python tests/verify_file_map_lifetime_x86.py
.venv/bin/python tests/verify_file_map_lifetime_x86.py --production-bindings
python3 tools/build_filemap_windows.py
```

Next required work: authentic external-runtime execution, exception/allocation-
failure behavior, overlapping/aliased name inputs, compiler matching, and integration
into the complete game reconstruction. Hashes, commands and evidence are recorded
in the corresponding lifetime, production-ABI and Windows-build JSON reports.
