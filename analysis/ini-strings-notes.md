# INI_Reader string parameter access

`src/ini_reader_strings.cpp` reconstructs both original get_value_string exports:
the indexed getter and the comma/space-joined getter. Original mangled member
symbols are retained under explicit x86 thiscall ABI entries.

Indexed binary behavior: type 0 formats the raw unsigned byte with %d; type 1
formats the signed 32-bit word with %d; type 2 promotes float32 to binary64 for
%g; type 3 returns the string-table pointer directly. Unknown tags return the
existing shared formatter buffer without clearing it. Numeric returns therefore
share one mutable buffer across calls/readers. Null entries or missing indices
return an empty literal. Missing indices format the original diagnostic and invoke
MessageBoxA. The assembly confirms the index is passed: the raw decompiler output
had omitted that argument, so it was not copied blindly.

The non-indexed binary getter clears the per-reader buffer at offset 0x1464 and
joins values with `, `. It uses binary decoding throughout the loop, rather than
rechecking mode after each append. This matters because the original unchecked
256-byte buffer can overwrite the adjacent mode byte. The observed forward-copy
word/tail order and absence of a length limit are retained.

`tests/verify_ini_strings_x86.py` passes 1,557 comparisons: 722 indexed parameter
cases and their joined forms, 100 additional sequences, shared-buffer invalidation
and unknown-tag reuse, diagnostics, null/empty entries, a controlled overflow and
the direct text-buffer return of the non-indexed getter. Text output, buffer identity
category, formatting argument bytes/call order and join/mode/tail side effects
agree. The overflow case also confirms later parameters still use binary decoding
after the mode byte is overwritten.

The printf fixture is an explicit integer/general-float formatting model. %g output
is not claimed to match authentic MSVCRT locale/exponent/NaN spelling; instead the
exact supplied binary64 argument bytes are compared alongside modeled output.
MessageBox is modeled. Indexed text StringIndex, arbitrary oversized/overlapping
joins, real CRT/OS/FPU effects and exact instruction matching remain unverified.

```sh
.venv/bin/python tests/verify_ini_strings_x86.py
```

Commands, source/DLL hashes and indexed vectors are in
`analysis/ini-strings-x86-behavior.json`. This does not complete text INI processing,
wide strings, vector access or the full reader/game lifecycle.

Update: reconstructed StringIndex is now used by the indexed text getter. Twenty
additional text index cases pass, bringing this suite to 1,577 comparisons.
Authentic CRT formatting and full text-INI iteration remain unverified.
