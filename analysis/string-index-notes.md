# StringIndex and text-parameter integration

`src/string_index.cpp` reconstructs original common.dll StringIndex at RVA 0xbbcc0.
The original exported C++ symbol is retained. Parameters are selected by commas,
without quote awareness, and returned through one shared scratch buffer.

The baseline class table's whitespace flag is set only for 9/10/13/32. Each input
byte is masked to seven bits before classification, so high-bit aliases such as
0x89 and 0xa0 can be stripped too. Vertical tab and form feed are not stripped.
Leading whitespace is skipped for each traversed field; trailing whitespace is
removed only from the selected field. Missing fields clear only scratch byte zero.
Copying preserves observed forward DWORD-plus-tail writes, including the trailing
terminator and untouched scratch tail.

The 1024-byte scratch view is supported by the next observed global region at
original VA 0x06400750, exactly 0x400 beyond the buffer at 0x06400350. Verification
is bounded to at most 1023-byte inputs; no safe bounds check is added to the code.

`verify_string_index_x86.py` passes 3,812 comparisons over 762 inputs: every nonzero
byte at field edges, whitespace/quote/empty/comma cases, a 1023-byte case, seeded
random byte strings and huge indices. It checks returned-buffer identity, output
and all 1024 scratch bytes after each call. Only original strchr is modeled.

A separate reconstructed-index test runtime now routes INI scalar getters to this
implementation rather than original StringIndex. The bool/int suite passes 2,340
calls, including 30 text index cases; invalid text-bool diagnostics are checked
against original FDUMP argument contents. The string-getter suite passes 1,577
calls, including 20 indexed text cases. The float suite still passes its 1,148
binary cases using the updated linkage; text float conversion remains pending.

Remaining work: text line/header/value iteration, ParseNumber and text floats,
full reader lifecycle, real CRT/logging execution, dynamic class-table edits,
null/oversized/overlapping StringIndex input and exact machine-code matching.
These helper/getter checks do not establish complete text INI parsing.

```sh
.venv/bin/python tests/verify_string_index_x86.py
.venv/bin/python tests/verify_ini_bool_int_x86.py
.venv/bin/python tests/verify_ini_strings_x86.py
```

Hashes, commands and scope are recorded in the corresponding JSON reports.
