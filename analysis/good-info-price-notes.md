# Goods pricing branches (2026-10-13)

Scope: `src/good_info_price.cpp/.hpp` reconstruct the base-price and four
buy/sell multiplier branches inside `GoodInfoList::read_Good_block`, original
common.dll entry `0x062708c0`. They are callable arithmetic handlers, NOT a
complete reconstruction of that member function, a Goods file loader, or a
polymorphic `GoodInfo` class. The temporary inline-assembly arithmetic boundary
is explicit; these helpers are not counted as additional whole-function exact
matches.

## Original evidence

Private original input: `original/_FL Fresh Install-deutsch/EXE/common.dll`,
SHA-256 `e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483`.
Ghidra function: `analysis/raw/common.dll/raw.c`, `read_Good_block`. Inspection
of original assembly confirmed the pricing branch at `0x06270ae4..0x06270b64`
and the four multiplier branches at `0x06270b79..0x06270bec`; decompiler float
casts alone are insufficient to establish their precision.

The signed integer base price is loaded with FILD. FST stores its rounded
binary32 view at offset `0x58`, but the original unrounded value remains in
ST0 for the defaults. Only values comparing equal to zero (including negative
zero) receive defaults; unordered NaNs are retained. The binary32 constants are
`0x3f733333` and `0x3f866666`, not decimal-double 0.95 and 1.05. The first applies
to good-buy (`0x5c`) and bad-sell (`0x68`); the second to bad-buy (`0x60`) and
good-sell (`0x64`). Nonzero existing prices are retained, so input order matters.

The four explicit multipliers consume the getter's full ST0 result, multiply
by the stored base-price word, and round only at FSTP. A binary64 spill can
change a binary32 result near a halfway tie. `good_price_value_float` is a
runtime ABI dependency, with thiscall ECX/stack index and full ST0 precision;
the fixture binds it to a controlled original-address getter. A future native
binding must not replace it by a rounded ordinary C++ float-returning getter.

## Executed differential evidence

Run from the project root after `source tools/paperclip-env.sh`:

    .venv/bin/python tests/verify_good_info_price_x86.py

Latest result: 10,704 paired original-block/handler comparisons, 892 cases for
each of twelve x87 control words (24/53/64-bit precision, all four rounding
modes). Category `ShipHull` and a nonempty shop string provide a valid context
that bypasses unrelated Archetype fallback and final cache writes. Reader
traversal and integer returns are controlled dependencies; floating returns
are genuine 80-bit ST0 fixture inputs, including binary64 values, 80-bit values
on both sides of a binary32 halfway tie, denormals, infinities and NaNs.

The test compares a complete 320-byte guarded storage region containing the
192-byte object at three alignments, including random padding. An independent
write-set assertion permits only the five pricing words to change. CW, SW,
full tag word and live 80-bit registers are compared, with either zero or two
preexisting x87 values. FPU instruction/data pointers and empty-register
residual bytes are intentionally excluded. 20,340 handler calls check CDECL
stack cleanup and preservation of EBX/ESI/EDI/EBP for the real reconstruction.
1,744 additional expected-value/retention assertions do not use the original
block as their value oracle.

Two deliberately incorrect source variants are compiled outside tracked
source and tested separately:

- Early binary32 rounding: 576 mutant handler checks; 243 stored-price
  mismatches, zero additional x87-state mismatches.
- Getter binary64 spill: 96 paired mutant blocks / 192 mutant handler checks;
  eight stored-price mismatches, zero additional x87-state mismatches.

These are repeated observations of TWO mutation types, not hundreds of
independent defects, and their calls are not included in the 20,340 real
reconstruction ABI checks. The JSON report pins all four source/fixture/test
hashes. The generated negative-control files and DLLs are ignored working
artifacts, not original game files.

## Review and limitations

Original and rebuilt disassembly were reviewed for register/stack conventions,
field offsets, padding preservation, exact constant bits and x87 instruction
order. Independent Paperclip read-only review FLA-126 reported no findings in
the final source/test/report state. Its delta verdict pins test SHA-256
`58d9e68d01bd6d7ac0adc2b1dc1a81379b9807cd0b3464ba7665375940b6e46c` and report
SHA-256 `0e2a0d4d839fbe01a3939125e75d4c96fd7c9bf73ef57fbabb676b262080600d`.
The review was static: the reviewer did not rerun builds/tests or modify any
files. The 1,744 independent assertions comprise 16 numerical sample checks
and 1,728 retention checks, not a separate numerical oracle for all cases.
No second agent edits the pricing source or tests in this checkout.

This does NOT verify complete Goods key dispatch, nickname/duplicate handling,
addon ownership, Archetype database construction/metadata fallback, actual
Goods file corpus, native Windows/CRT execution, unmasked x87 exceptions,
stack exhaustion or whole-function machine-code identity. No raw-function
percentage is promoted to a complete-game reconstruction percentage.

Next integration milestone: implement the remaining Goods block key dispatch,
metadata finalization and addon ownership, using these price handlers; then
compare real Goods files with reconstructed reader/hash/cache/index mechanics
and a genuinely populated Archetype database. Full loader lifecycle and the
entire game remain unfinished.
