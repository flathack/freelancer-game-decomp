# decomp.dev integration

The `Decompilation progress` Actions workflow publishes an objdiff v2 JSON report
as `de_1.0_report/report.json`. Once the workflow succeeds on `main`, a repository
admin can register https://github.com/flathack/freelancer-game-decomp at
https://decomp.dev/manage/new. Display name: Freelancer (German installation),
short name: Freelancer, platform: PC (x86). The GitHub App is optional:
https://github.com/apps/decomp-dev.

Run locally with Python, pefile and clang++:

```sh
python tools/decomp_dev_report.py --out build/report.json
```

The report groups all 34 scoped code modules into module units/categories.
The code denominator is the sum of executable PE section virtual sizes in the
committed inventory, including padding and bytes not yet classified as functions.
It is a conservative executable-section coverage metric, not proof of full game
reconstruction. Function totals are the committed raw discovery snapshot; function
discovery is incomplete and these counts may change. Only pinned original function
bytes in `analysis/matches.json` which match a freshly compiled `src/csimple.cpp`
are credited. Currently these are two functions / 14 bytes. If source/compiler
changes stop matching, those functions receive no credit. Original installation
hashes and section boundaries are checked against the scope inventory; CI does
not re-read the original binaries. Data coverage and complete/linked progress
remain zero/unreported because no full matching link has been established.

Raw Ghidra output and differential behavior tests do not count as binary matching.
See `analysis/progress.md` for those separate results. Original binaries, archive,
raw exports and build products are excluded from Git. CI needs no game files.
Future matches in other sources require extending the compilation/evidence mapping;
the generator fails on unsupported evidence rather than claiming unchecked matches.

Integration contract: https://decomp.wiki/tools/decomp-dev
Report schema: https://github.com/encounter/objdiff/blob/main/objdiff-core/protos/report.proto
