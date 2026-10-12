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

## Binary INI navigation

`src/ini_reader.cpp` reconstructs 15 binary navigation/name/state methods and the
internal BINI recognition helper. Packed header/section/entry/parameter fields are
now defined from the original instructions. The all-files differential run visits
the supplied DATA BINI corpus plus forty synthetic inputs and recognition edges.

```bash
.venv/bin/python tests/verify_bini_reader_x86.py --all-files
```

The final input paths, hashes and totals are in `analysis/bini-reader-x86-behavior.json`.
Text iteration is an explicit pending dependency, and typed parameter getters and
reader open/close/lifecycle are not implemented/verified by this step. This remains
an intermediate binary-navigation component. See `analysis/bini-reader-notes.md`.

The complete BINI navigation run passed 5,140,903 calls over 70,330 sections and
515,921 entries. All 1,241 supplied BINI files were checked, including the two
header-only files rejected by the original recognition helper, plus 40 synthetic
files. This proves the tested navigation/state behavior; numeric/string value
conversion, text-INI iteration and full reader lifecycle remain open.

## Binary bool/int parameter conversion

`src/ini_reader_values.cpp` adds the original ABI entries for get_value_bool and
get_value_int. 2,280 comparisons pass over 1,136 synthetic parameter cases, including
raw bool bytes, floating special values, missing-parameter diagnostics and unknown
tags. CRT conversion/diagnostic operations are explicit models in this check.

```bash
.venv/bin/python tests/verify_ini_bool_int_x86.py
```

Production binding, actual CRT/FPU execution and text-mode getter behavior remain
open. Numeric float/string/wstring/vector accessors are not completed by this step.
See `analysis/ini-bool-int-notes.md` for the precise boundaries.

## Binary float parameters

`src/ini_reader_float.cpp` implements get_value_float with a C++ double-return ABI
view under the original float member symbol. This preserves its unrounded x87
return without assembly in the getter. 1,148 full 80-bit return comparisons pass,
including integer/float special values, diagnostics and injected atof precision
beyond binary64.

```bash
.venv/bin/python tests/verify_ini_float_x86.py
```

Real CRT/FPU execution and the text-mode float path remain unverified. Scope and
ABI details are in `analysis/ini-float-notes.md`.
