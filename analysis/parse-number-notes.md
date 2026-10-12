# ParseNumber reconstruction and text-float integration

`src/parse_number.cpp` reconstructs syntax dispatch from original common.dll
ParseNumber at RVA 0xbba00. The baseline classification/digit tables are preserved,
including seven-bit classification and signed-char digit-table addressing. External
tolower/atof/logging remain imports; test fixtures provide explicit models.

The parser strips an optional '+' followed by an optional '-', then removes leading
zeros and recognizes x/X as a hex prefix. It scans hex-class characters for suffix
selection: multi-character runs ending in b/B choose base 2; d/D keeps decimal.
A single scanned digit followed by literal lowercase h chooses base 16, while
uppercase H or longer h-suffixed runs do not receive the same treatment. Character
literals return the next signed byte immediately, ignoring the prior sign.
Examples such as '+-3', '--3', 'ABh' and illegal binary digits are retained as
observed rather than normalized into a modern number grammar.

`src/parse_number_x87.cpp` is an explicit temporary arithmetic boundary. It keeps
base-N accumulation and fractional divisors in extended x87 precision. On an
illegal digit, the accumulated result is rounded through binary64 before the
original warning call, then sign is applied. Pure double accumulation would change
large/fractional results; this assembly portion is not counted as a full C++ match.

`verify_parse_number_x86.py` passes 1,533 comparisons: complete 80-bit return bytes,
atof dispatch strings and warning arguments agree. Tests include character byte
edges, high-bit digit-table behavior, hex fractions, suffix quirks, signs, large
hex values and seeded mixed syntax. The ASCII tolower, decimal-prefix/binary64 atof
and FDUMP imports are models, so native locale/CRT and FPU flag/control-word effects
are still unverified.

`src/ini_text_float.cpp` now routes text float lookup through reconstructed
StringIndex and ParseNumber. The float getter suite passes 1,178 comparisons,
including 30 new text lookups with full x87 return/diagnostic comparison. The former
text-float trapping adapter has been removed. Reader construction/open/close,
wide-string/vector accessors, real runtime and complete-game/compiler matching
remain open.

```sh
.venv/bin/python tests/verify_parse_number_x86.py
.venv/bin/python tests/verify_ini_float_x86.py
```

Evidence: `parse-number-x86-behavior.json` and the updated float-getter report.
