# INI_Reader binary bool/int conversion

`src/ini_reader_values.cpp` reconstructs binary get_value_bool and get_value_int.
The ABI entries use the original member symbols with ECX=this and one stack index.
The bool entry is expressed as a raw unsigned-byte return under the original
symbol, because original tag-0 values are returned directly in AL. This avoids
silently canonicalizing malformed/noncanonical bool payloads to 0/1.

Observed cases:

- Tag 0: bool returns payload byte; int zero-extends that byte.
- Tag 1: bool tests the full 32-bit word; int returns the exact word as signed int.
- Tag 2: bool is false for signed zero and true for nonzero/NaN; int invokes the
  external legacy x87 _ftol conversion and uses EAX (the low conversion word).
- Tag 3: bool recognizes true/false case-insensitively, otherwise tests atoi;
  int invokes atoi on the string-table-relative address.
- Unknown tag or absent current entry: return zero.
- Missing index with a current entry: format a header/value/index diagnostic,
  invoke MessageBoxA, then return zero.

The external _ftol path is kept separate from a modern direct float-to-int32 cast:
large finite inputs can produce different low-word results. The test binding loads
the argument into ST0 and jumps to the original import slot. This is an emulator
fixture, not a production import binding.

`tests/verify_ini_bool_int_x86.py` passes 2,280 calls on 1,136 parameter cases:
all 256 raw bool bytes, word boundaries and seeded random integers/floats, signed
zero, subnormals, infinities, NaNs, recognized/non-numeric strings, every unknown
tag, missing parameters and null current-entry state. Returned AL/EAX, unchanged
parser fields and diagnostic texts agree with the original instructions.

The test explicitly models ASCII stricmp, decimal-prefix atoi, _ftol's integer
result from the actual emulated 80-bit ST0 representation, and sprintf/MessageBox.
Real CRT/OS execution, FPU exception/control-word behavior, invalid memory payloads
and text-mode getter paths are not verified. The text-side logic is present, but
its string indexing/logging dependencies remain open; the invalid-text-bool test
adapter traps rather than pretending that path is complete.

```sh
.venv/bin/python tests/verify_ini_bool_int_x86.py
```

Build/source hashes, complete parameter/result vectors and scope are recorded in
`analysis/ini-bool-int-x86-behavior.json`. Float/string/wstring/vector getters and
full text INI parsing still remain part of the full Freelancer objective.
