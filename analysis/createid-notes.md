# CFLIDMaker / CreateID reconstruction

Baseline: common.dll SHA-256 recorded in `flid-x86-behavior.json`.
Original exported methods: protected constructor at RVA `0x43da0`, destructor
`0xad0b0`, assignment `0xc7f0`, AllocateObjectID `0x43d90`, GetInstance `0xad070`,
Initialize `0xad0f0`, CreateStaticID `0xad270`, Shutdown `0xad0c0`.
CreateID is at `0xad470`; the internal CRC byte update is at `0xad3b0`.

`src/cfl_id_maker.hpp` defines the observed 8-byte x86 maker object and 0x41c-byte
CRC object, with checked remainder offset 0x418. `src/create_id.cpp` reconstructs
singleton allocation, initialization, destructor/freeing, shallow assignment,
30-bit object-ID masking/wrap, CRC table generation and all four update paths.
The original unchecked 256-byte stack copy is retained. The CRC configuration
is width=30, polynomial=0x8005, initial/final XOR=0, reflected/direct=true and
32-bit storage. Finalization reverses bytes, shifts right two, and sets bit 31.

Runtime allocation, freeing, `_strlwr` and allocation-failure logging are declared
as binding interfaces. Their production bindings remain open. The test fixture
binds allocator/freeing/lowercasing to original addresses under emulation;
allocation-failure logging is deliberately unimplemented in that fixture.
No original game binary is loaded as executable code by the host OS.

Native differential check: 636 null/ASCII vectors against original instructions,
with CRC table/configuration/remainder compared after every case. Two CRC padding
bytes are excluded because the original leaves them unwritten.

Compiled x86 differential check: Clang's i686/MSVC target plus lld-link produces
a test DLL. Its exported class methods and internal Update method run alongside
the original in Unicorn. Passing checks cover 505 hashes and complete CRC states,
28 counter boundary/wrap cases, 400 byte updates across all reflected/direct
branches, constructor, shallow assignment, initialization caching/failure/retry,
destructor, shutdown/free order/idempotence, singleton allocation failure/retry.
The synthesized Update export is a test access mechanism, not an original export.

This is behavioral and x86 ABI evidence, not exact instruction matching, full
CRT/locale verification, or a complete game build. Exact-byte matching remains
at two CSimple getters. ASCII inputs of at most 255 bytes are the string domain.
Allocation failure logging through CreateID and non-ASCII lowercasing are unverified.

Run:

```sh
.venv/bin/python tests/verify_create_id.py
.venv/bin/python tests/verify_flid_x86.py
```

Full commands, source hashes and compiled DLL hash are saved in
`analysis/flid-x86-behavior.json`.
