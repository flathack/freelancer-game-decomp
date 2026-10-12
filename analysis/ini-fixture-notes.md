# Complete INI Reader export fixture

`tools/build_ini_fixture.py` discovers the 39 exports owned by INI_Reader from
the original pinned common.dll and links every one against reconstructed code.
It verifies exact equality of original/rebuilt export name sets; all source
translation units and adapters link together without missing symbols. This is
an integration fixture with test adapters bound to original image addresses,
not a standalone replacement DLL or a native Windows runtime verification.

log_link at original VA 0x0634c430 is a no-op shared by multiple original exports.
The reconstructed function matches its entire 3-byte body (ret 4). Sixteen
original/rebuilt ABI cases accept arbitrary/null reader and text pointers without
accessing them, and the stack-cleanup checks pass. This shared no-op must not
inflate substantive unique logic coverage.

The existing narrow machine-code report still covers its two CSimple functions;
the independent log_link match is recorded in this fixture report. Full reader
runtime paths, authentic CRT/OS behavior, neighboring static storage overflow,
exception unwinding and instruction matching for other methods remain incomplete.

## Shared-DLL differential integration

`tools/verify_ini_integrated.py` builds the complete fixture once, then redirects
reconstructed-image loads in 17 existing differential suites to that same DLL.
The original pinned common.dll still supplies every baseline. Narrow suites still
compile their historical DLLs, but those DLLs are not executed in integrated
mode. This explicit loader substitution is scoped to the runner and restored
when it exits. Detailed JSON reports are redirected to analysis/ini-integrated;
their compiled-DLL hashes identify the actual shared fixture. Original narrow
reports are preserved. Commands in detailed reports describe the historical
suite builds; the shared build commands/source hashes are in ini-fixture-build.

All 17 suites pass: lifecycle, ownership, file open, text iteration, modern and
legacy numeric/string/vector accesses, line formatting and wide conversion.
Five data exports expose reconstructed buffers for test inspection, in addition
to the 39 original reader methods. This is integration evidence under existing
external dependency models, not full corpus navigation coverage, native runtime
validation or full game completion.
