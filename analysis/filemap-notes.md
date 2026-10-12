# FileMap memory/BINI reconstruction

`src/file_map.cpp` reconstructs 12 exported methods: default constructor,
open_memory, get_file_name, get_file_length, eof, tell, seek, request_pointer,
read and three typed read_ptr overloads. Copy/assignment/destructor and OS-backed open/close/handoff have now been
implemented separately; see `filemap-lifetime-notes.md`. Original MSVCP60 COW
operations remain imported external dependencies.

The observed x86 object is 36 bytes: 16-byte MSVC6 string state followed by file
handle, mapping handle, data pointer, length and cursor. Tests compare the defined
32-byte suffix, normalizing the independently allocated data pointers. The first
four allocator/padding bytes are intentionally excluded: the original constructor
stores an indeterminate allocator byte, so no deterministic value is claimed.

Memory opening succeeds only with non-null input and nonzero size, allocates a
copy, and sets cursor zero. It does not close old handles or free prior data.
That behavior is retained and checked on reopening; invalid open inputs leave
existing state untouched. Malloc failure remains unverified.

Seek clamps to length only when data exists. Tell returns zero when data is null.
Requesting zero bytes before EOF returns the current data pointer without advancing;
at EOF or without data it clears the requested length and returns null. Reads
advance by the clamped available length and copy data forward in 4-byte chunks
plus trailing bytes as observed in the original.

BINI_Header, BINI_Block and BINI_Value retain sizes 12, 4 and 3 bytes. Their
fields have since been reconstructed from the INI_Reader instructions; see
`bini-reader-notes.md`. Failed typed reads consume a short
remaining tail, then null the output pointer; there is no automatic rollback.

`tests/verify_file_map_x86.py` builds a Windows x86 DLL and compares it with original
instructions in Unicorn. 3,298 calls across all 12 methods pass, with object state,
returned pointer offsets, requested lengths and destination bytes checked. Cases
include unsigned boundary offsets/sizes, empty/null state, 1..256-byte maps,
seeded random operations, 16 explicit truncated typed reads and reopening with
existing handles. The allocator succeeds and the CRT empty string is controlled.
No host OS file APIs or game processes are executed.

This report covers only the memory-reader subset, not the full game or INI parser.
Filename refcounting and resource methods now have separate modeled-import tests.
Exact instruction matching, overlapping buffers, allocation failure and real
CRT/OS runtime verification remain open.

Run: `.venv/bin/python tests/verify_file_map_x86.py`.
Report and build/source hashes: `analysis/filemap-x86-behavior.json`.
