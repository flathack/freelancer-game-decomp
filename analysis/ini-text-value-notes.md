# INI_Reader text entry decoding

`src/ini_text_value.cpp` supplies the text read_value provider formerly left pending.
The implementation follows original assembly at VA 0x0630f570, reached by the
exported INI_Reader::read_value text branch. The raw decompiler had removed much
of this control flow as unreachable, so assembly was the primary evidence.

Empty/NUL/comment lines are skipped after leading space/TAB trimming. A line
beginning with `[` returns false and restores that line's pre-read cursor and line
counter, allowing the next read_header to consume it. EOF clears only name byte
zero. Names are copied bytewise up to '=' or ';', then trailing space/TAB is trimmed;
the untrimmed copied tail is preserved. A name without '=' still returns true with
an empty value. Values skip leading space/TAB after '=', end at ';' or explicit
line length, and trim trailing space/TAB before copying. Quote characters do not
protect semicolons. Embedded NUL does not stop length-based copying.

`verify_ini_text_value_x86.py` passes 3,957 text-entry comparisons across 313 inputs,
including repeated section-boundary rewinds, comments, orphan/empty keys, extra
'=', quoted semicolons, embedded zeros, chunk edges and seeded sequences. Entire
INI reader images agree, so cursor/counter/buffer-tail effects are covered.

An additional 1,559 integrated API calls traverse 13 supplied non-BINI text INI
files smaller than 64 KiB: 47 sections and 1,358 entries. Original/rebuilt
read_header/read_value alternate, with State snapshot/restoration comparisons.
Each tested path and SHA-256 is recorded. Larger files and other extensions are
not implicitly covered by this selected text corpus.

No external function is executed by the checked text navigation paths. The linked
fixture still models unused compare/index boundaries; authentic OS acquisition,
reader constructors/open/close, text ParseNumber/float and exact byte matching
remain open. The legacy pending-provider names are retained for linkage, but both
text header and value provider implementations now exist in source.

```sh
.venv/bin/python tests/verify_ini_text_value_x86.py
```

Evidence: `analysis/ini-text-value-x86-behavior.json`.
