# CreateID reconstruction

Original export: `?CreateID@@YAIPBD@Z`, common.dll RVA `0xad470`.
The export invokes a lazy singleton helper at RVA `0xad070`, then the hash method
at `0xad270`. The table initialization is at `0xad0f0`, byte update at `0xad3b0`.

Observed CRC configuration: 30-bit width, polynomial `0x8005`, reflected input
and output, zero initial remainder, zero final XOR, 32-bit output storage.
The result reverses the four bytes, shifts right by two and sets bit 31.
A null input yields zero; an empty string yields `0x80000000`.

`src/create_id.cpp` reconstructs the hashing algorithm. It computes a local
table rather than preserving the original allocator/singleton object. It is
not a drop-in binary ABI replacement or a machine-code match at this stage.
The original `_strlwr` import is explicitly confirmed from the PE import table.
ASCII lowercasing is modeled; other bytes and CRT locale behavior remain open.

`tests/verify_create_id.py` emulates the original x86 instructions in Unicorn,
including lazy object and table initialization, byte update, and finalization.
The allocator succeeds with a deterministic heap, and `_strlwr` is mocked for
ASCII. No game EXE or DLL is loaded by the operating system. The reconstructed
C++ is compiled as a native shared library and called through ctypes.

636 differential cases pass: null, empty, known-style nicknames, all nonzero
ASCII one-byte inputs, 255-byte boundary inputs and 500 seeded random ASCII
strings. Full vectors and input/source hashes are in `createid-behavior.json`.
This provides behavioral evidence for the stated domain, not a proof over all
inputs. Allocation failure, logging, non-ASCII bytes and complete PE linking are
not tested. Inputs over 255 bytes overflow the original stack copy and are not
part of this test domain.

Run: `.venv/bin/python tests/verify_create_id.py`.
