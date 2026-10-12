# EquipDesc reconstruction

Original: SHA-pinned common.dll. All 26 exported member methods of EquipDesc are
implemented (the static-data export is initialized by the reconstructed StringAlloc).
This does not cover EquipDescList, EquipDescVector, their template containers,
CacheString interning, or the complete Archetype::Equipment implementation.

## Layout and behavior

The object is 32 bytes on x86. Observed fields are: unknown byte at offset 0,
16-bit ID at 2, archetype ID at 4, CacheString pointer at 8, equipped byte at 12,
status float at 16, signed count at 20, temporary byte at 24, signed owner at 28.
Padding remains untouched by construction and field-wise copy construction;
assignment copies every byte, including padding. Comparison operators use only
the unsigned 16-bit ID, not the full object. Internality compares interned pointer
identity against CARGO_BAY_HP_NAME. Default hardpoint initialization now runs through the reconstructed StringAlloc
with `BAY`; original and rebuilt global initializers are both executed in the test.

Cargo occupancy calls Archetype::GetEquipment only for an internal hardpoint
and a nonzero archetype ID, then multiplies signed count by the float at offset
0x5c. Missing equipment is not silently converted to zero: the original would
attempt a dereference, and the reconstruction retains that behavior.

## Verification

`tests/verify_equip_desc_x86.py` builds a x86 PE DLL with Clang and lld-link, loads
it and the original in Unicorn and compares original exported methods with the
reconstruction. 2,406 constructor/copy/assignment, setter/getter, comparison,
internality and status calls pass; object bytes including padding are compared.
The harness respects defined return-value widths and ignores undefined EAX
contents for void methods. It verifies callee stack cleanup and pointer results.

200 cargo tests cover branch-dependent equipment lookup and signed count/volume
inputs. Exact 80-bit x87 return bytes are compared, not just host floats. The Archetype lookup remains a controlled test dependency. BAY interning is
reconstructed and independently checked against the original; the actual
equipment database and production runtime bindings remain unverified.

## Compiler precision issue and temporary shim

Ordinary Clang-generated C++ rounded cargo's result to binary32 before returning.
107 of 200 cases differed from the original's extended-precision ST0 value.
Changing ordinary optimization flags did not eliminate that narrowing.

The x86 Clang build therefore uses a temporary assembly ABI boundary which does
FILD/FMUL and returns the unrounded ST0 result. C++ helpers implement the original
branch decision and equipment lookup. The assembly entry uses the exact original
member symbol and ECX=this. All 200 extended-precision comparisons now pass.
This is explicitly **assembly-assisted behavior reconstruction**, not an exact
machine-code match or fully C++ decompilation. Removing the shim through a suitable
compiler configuration remains part of the full matching-decompilation objective.
The non-x86/other-compiler C++ fallback has not been runtime-verified here.

Commands, source hashes, DLL hash and counts are in `equipdesc-x86-behavior.json`.
