# INI_Reader float access and x87 precision

`src/ini_reader_float.cpp` implements the binary get_value_float entry under its
original member symbol. It uses a C++ double-return ABI view: x86 returns both
float and double in ST0, and declaring the implementation as double prevents
Clang from narrowing to binary32 before return. This is not a change to the
original export name or an assertion that the nominal original API returned double.
There is no assembly in the getter implementation.

Tag 0 returns the unsigned payload byte, tag 1 the signed 32-bit integer, tag 2
loads the encoded float32, and tag 3 passes through atof on the string-table
address. Missing/unknown values return zero. Missing-index diagnostics use the
reconstructed diagnostic binding. Integers, bytes and finite float32 values are
exactly representable in binary64; their complete x87 return values agree with
original FILD/FLD instructions. NaN/infinity return representations are also tested.

`tests/verify_ini_float_x86.py` passes 1,148 comparisons: 1,140 parameter cases,
four injected atof return values carrying precision beyond binary64, three
missing-index cases and a null-entry case. Every returned value is compared as
all ten bytes of its 80-bit x87 representation, not as a Python/host float32.
The injected extended-precision results pass through unchanged, confirming that
the compiled return path does not narrow atof's ST0 value either.

The atof fixture supplies a decimal-prefix/binary64 model and optional injected
80-bit ST0 values; sprintf/MessageBox are diagnostic models. These tests establish
argument/return behavior under those imports, not actual CRT execution or FPU
exception/control-word fidelity. Text-mode get_value_float explicitly remains a
pending dependency with a trapping test adapter. Malformed memory access and
exact machine-code matching are also open.

The bool/int suite was rerun after the shared ABI-header addition and still passes
all 2,280 comparisons. Navigation source/layout was not changed by this separate
getter implementation; its full-corpus evidence remains separately recorded.

```sh
.venv/bin/python tests/verify_ini_float_x86.py
```

Build/source hashes, test vectors and scope are in `ini-float-x86-behavior.json`.
The implementation is an ABI-oriented reconstruction; integration with a complete
public INI_Reader API and all callers remains part of the full game objective.
