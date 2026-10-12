# TextFile32 line reading and INI text-header search

`src/text_file.cpp` reconstructs TextFile32::read_line and exposes its shared
ReadTextLine core for the INI reader. FileMap occupies the first 36 bytes; the
line counter is at offset 36. LineParser32 has a 1024-byte buffer followed by
length and position words (total 1032 bytes).

Reading requests at most 1023 bytes, then scans for CR/LF. Both CRLF and LFCR pairs
are consumed together when both bytes are in the requested chunk. At a chunk edge
the second byte is left for the next call. Input NUL does not end copying: the
explicit line length can include embedded zeros. The buffer tail remains untouched.
Line count increments even when reading fails at EOF or with no mapping. The mapped
cursor advances only by the consumed bytes; no mapping preserves a stale cursor.

`verify_text_file_x86.py` passes 41,919 comparisons across 214 inputs. Checks cover
reader state, complete parser-buffer footprint, newline pairs/chunk edges, embedded
NUL, long lines, random byte sequences, EOF repetition and counter wrap. No external
function is executed/modeled in this read-path check.

`src/ini_text_header.cpp` supplies the formerly pending text-header helper. It skips
leading spaces/TAB on lines, finds a leading `[`, copies through `]` or line end,
and trims only trailing spaces/TAB inside the name. Leading spaces inside `[` are
retained; empty or unclosed headers can succeed. A parsed name beginning with `;`
is skipped. Header bytes after the copied terminator remain unchanged; exhaustion
clears only the first header byte.

`verify_ini_text_header_x86.py` passes 2,966 calls across 311 inputs, comparing the
whole reader image and header-buffer footprint against original INI_Reader::read_header.
It covers comments, malformed/empty headers, whitespace, embedded zeros, chunk
boundaries, newline variants and seeded sequences. The original header path requires
no mocked external calls; the linked unused text-value helper remains a trap.

The binary-navigation fixture is unchanged, so its historical full-corpus evidence
is preserved separately. Complete text read_value, token parsing, text float numbers,
reader lifecycle, aliased/invalid pointers, native runtime and exact byte matching
remain open. The legacy `ini_pending_read_text_header` provider name remains for
link compatibility even though this provider now has an implementation.

```sh
.venv/bin/python tests/verify_text_file_x86.py
.venv/bin/python tests/verify_ini_text_header_x86.py
```

Evidence: `text-file-x86-behavior.json` and `ini-text-header-x86-behavior.json`.
