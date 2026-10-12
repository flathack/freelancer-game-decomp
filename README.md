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

## String parameter getters

Both get_value_string ABI entries are reconstructed. 1,557 comparisons pass for
indexed formatting, shared-buffer lifetime, parameter joins, diagnostics, the
direct text-buffer path and one controlled reproduction of the original join
buffer overflow. Formatter/MessageBox dependencies remain explicit test models.

```bash
.venv/bin/python tests/verify_ini_strings_x86.py
```

Authentic CRT formatting, indexed text parsing and arbitrary malformed/overlapping
buffers remain unverified. See `analysis/ini-strings-notes.md` for scope.

## Text parameter indexing

`src/string_index.cpp` reconstructs comma selection, the original seven-bit
whitespace classification and shared scratch-buffer writes. 3,812 comparisons
pass, including all byte-edge cases and full buffer footprints. Text bool/int
getters and indexed string getters now use this source implementation; their
suites pass 2,340 and 1,577 calls respectively. Invalid text-bool logging arguments
are also compared under explicit logging models.

```bash
.venv/bin/python tests/verify_string_index_x86.py
```

Text line/header/value iteration and text floating-number parsing remain open.
See `analysis/string-index-notes.md` for exact scope.

## Text line/header reading

`src/text_file.cpp` reconstructs the original 1023-byte line chunking, CR/LF pair
handling and line counter behavior. 41,919 line-read comparisons pass. The text
INI header helper is implemented in `src/ini_text_header.cpp`; 2,966 header-search
comparisons pass with full state and buffer-footprint checks.

```bash
.venv/bin/python tests/verify_text_file_x86.py
.venv/bin/python tests/verify_ini_text_header_x86.py
```

Text value/token iteration and text floating-number parsing remain open. Details
and intentionally retained legacy edge cases are in `analysis/text-reading-notes.md`.

## Text entry navigation

`src/ini_text_value.cpp` reconstructs names/values and the section-boundary rewind.
3,957 direct comparisons pass. Alternating header/value and State APIs additionally
pass 1,559 integrated calls over 13 supplied text INI files (47 sections, 1,358
entries). Input paths/hashes and selection limits are recorded in the report.

```bash
.venv/bin/python tests/verify_ini_text_value_x86.py
```

Text ParseNumber/float and full reader lifecycle/native runtime remain open.
See `analysis/ini-text-value-notes.md`.

## ParseNumber and text float values

`src/parse_number.cpp` reconstructs numeric syntax selection and baseline tables.
Its x87 accumulation remains an explicit temporary assembly boundary. 1,533
comparisons pass for full 80-bit returns, decimal dispatch and warning arguments.
The text float getter now uses reconstructed StringIndex/ParseNumber; its suite
passes 1,178 cases including 30 text lookups.

```bash
.venv/bin/python tests/verify_parse_number_x86.py
```

Native CRT/locale/FPU effects and removal of the arithmetic boundary remain open.
See `analysis/parse-number-notes.md`.

Reader lifecycle: `src/ini_reader_lifetime.cpp` reconstructs active-mode close,
filename lookup, and line-number lookup, including the binary-mode warning.
`tests/verify_ini_lifetime_x86.py` compares 144 calls against original x86
instructions (complete object state, metadata and resource/diagnostic effects).
This is behavioral reconstruction; complete game reconstruction remains unfinished.

`INI_Reader::open_memory` now copies and takes ownership of the input through the
reconstructed FileMap. Its original unconditional text-mode selection and limited
parser reset are preserved. 320 differential calls pass, including BINI-looking
input, existing resources, shared COW names, invalid arguments and copy boundaries.

`INI_Reader::get_line_ptr` reconstructs text and BINI line formatting using the
existing parameter converters. 2403 integrated string/line differential calls
pass, including full output-buffer write footprints within tested ranges.
Original static-buffer extents and oversized-line overflow adjacency remain to
be reconstructed; see `analysis/ini-line-notes.md`.

BINI line and numeric output now share the original observed +256-byte address
relationship through COFF aliases. 2445 integrated comparisons pass, including
21 overflow/reuse sequences and comparison of the complete 512-byte region.
Static storage beyond that region and text-buffer allocation extents remain open.

`INI_Reader::is_number` now reproduces the original lexical predicate, including
permissive exponent, hex-prefix and character-literal cases. 10,716 differential
calls pass with exact signed `tolower` arguments and unchanged reader state.
This predicate is intentionally separate from the reconstructed ParseNumber.
