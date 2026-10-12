# INI_Reader BINI navigation reconstruction

`src/ini_reader.hpp` models observed fields through mode byte offset 0x1564.
The reconstructed x86 view has field extent/alignment 0x1568. The binary FileMap
begins at 0x1428, with file-header/string-table/current-block pointers at
0x144c/0x1450/0x1454, signed 16-bit entry index at 0x1458, entry pointer at 0x145c
and parameter pointer at 0x1460. Unknown regions are explicit placeholders.
This is not a claim that every private class field or lifecycle is reconstructed.

The BINI structures are now named packed layouts: 12-byte header (magic, version,
string-table offset), 4-byte section (16-bit name offset and entry count), 3-byte
entry (16-bit name offset and 8-bit parameter count) and 5-byte parameter (tag and
32-bit payload). The existing FileMap read_ptr ABI sizes remain unchanged.

## Implemented and tested binary paths

15 original exported methods are reconstructed for navigation/name/count/state:
read_header, read_value, find_header, header/name pointers, parameter count/empty
query, section/entry comparison, end query, seek/tell/reset, get_state/set_state.
The internal initializer at original VA 0x0630fc60 is also reconstructed and
exposed under a synthetic test-only helper name.

Initialization validates magic and string-table offset < mapped file length; the
observed helper does not validate version. A twelve-byte BINI file with table
offset equal to its length is rejected by the original helper, and the tests
record this rejection rather than filtering those supplied files out.

Reading a new section skips unread entries and their count*5 parameter bytes.
A complete entry header can succeed even when its payload request is short/null;
this permissive original behavior is retained. State snapshots preserve relative
pointer offsets, including unsigned wrap for null pointers, and leave binary
snapshot padding untouched. Text snapshot copying is implemented from observed
buffer offsets but is not covered by the binary corpus check.

## Validation and remaining work

`tests/verify_bini_reader_x86.py` compiles the reconstructed reader with FileMap and
runs original/rebuilt x86 methods on identical mapped bytes. It compares defined
parser fields after every call, case-insensitive names, complete State buffers and
seek/state restoration. The only executed external comparison is an ASCII stricmp
model. Original and rebuilt mappings share the same data base so pointers can be
compared directly.

The report records each actual tested input path and SHA-256. `--all-files` selects
every supplied BINI `.ini` in DATA, rather than the default twenty smallest files;
40 seeded synthetic files and four recognition edge cases are included.

```sh
.venv/bin/python tests/verify_bini_reader_x86.py --all-files
```

Text read_header/read_value are explicitly pending dependencies whose test adapters
trap if executed. Typed int/float/bool/string getters, INI open/close/lifecycle,
malformed-record memory trust, non-ASCII comparison and exact instruction matching
are not verified here. The binary navigation component is not a full INI parser
or complete game reconstruction. The completed all-files run passes 5,140,903 differential calls
over 70,330 sections and 515,921 entries. All
1241 supplied BINI files and forty synthetic files are recorded;
2 original header-only files are rejected by both recognition helpers as
expected. No typed parameter conversion is implied by these navigation counts.
Build/source hashes and totals are in `analysis/bini-reader-x86-behavior.json`.

Long section searches exceed the generic one-million-instruction emulator budget.
The BINI check uses a twenty-million-instruction per-call limit so complete original
searches can finish; it still requires return to the sentinel and exact state/ABI
agreement. Source/test/hash-guarded per-file checkpoints are saved only after a
file comparison completes. They do not stand in for a live-process check.
