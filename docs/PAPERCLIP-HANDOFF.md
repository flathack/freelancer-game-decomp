# Freelancer transfer to Paperclip

User request (2026-10-13): pause this Codex decompilation goal, transfer all project material to hermes-srv, and continue through the existing Paperclip company. The Codex goal is paused; the complete-game objective remains unfinished.

Repository: https://github.com/flathack/freelancer-game-decomp.git (main). Commit and push after each verified progress; keep README concise and honest. Original game binaries, archive and raw outputs are private working inputs, ignored by Git. Never publish them as source.

Latest verified work before pause: 96,000 Archetype::GetEquipment pointer/error-message comparisons and 48,000 calls across six ID accessor aliases, plus a byte-identical 7-byte shared ID accessor. Six aliases refer to ONE original function body; count its bytes once. Equipment trees were populated using the reconstructed Goods index mechanics with synthetic payload pointers. Actual Archetype database creation and Goods loading remain unfinished.

Run differential tests with `.venv/bin/python tests/verify_archetype_lookup_x86.py`. Exact code verification: `.venv/bin/python tools/verify_matches.py`; progress: `python3 tools/progress.py`; dashboard: `.venv/bin/python tools/decomp_dev_report.py`. Test harness uses Unicorn and pinned original common.dll. Source builds need clang++ i686-pc-windows-msvc and lld-link, without native Windows execution.

Current reconstruction: INI reader/FileMap/IDs/string cache/EquipDesc and Loadout parts; supplied Loadout files passed 803 Maps/17,130 entries. Goods lifecycle, list initialization, index insertion and lookup reconstructed. See analysis/progress.md and individual notes/reports for limits. Raw Ghidra outputs are not buildable source. Entire game is NOT reconstructed or playable.

Next work: actual Goods block reader, file loader and ownership; Archetype data/metadata and virtual readers. Inspect original assembly rather than trusting raw decompiler names. Preserve ABI, padding, x87 behavior, duplicate handling and original edge cases; compare against original bytes. Avoid success claims based on narrow fixtures. Native OS/CRT execution, full engine/render/audio/network/gameplay and most modules remain open.

Workflow: coordinator scopes a substantial next milestone; implementation agent reconstructs using original evidence; reviewer checks ABI/state and meaningful original/reconstruction tests; integrator updates README/progress, commits and pushes. Use isolated worktrees when multiple agents edit; one integrator changes main. Start no parallel edits to the same checkout. Stop only for a concrete blocker or user pause, and report the specific evidence.

Mandatory quota gate, including every implementation/review subtask: continue only with a known Codex weekly remaining allowance strictly greater than 30%. At 30% or below, or unknown quota, stop and retain all files. Check before starting and at least every 60 seconds during active work through the existing protected launcher. Include this rule and the exact project path in every future Freelancer task assignment so the launcher recognizes the scope. See docs/PAPERCLIP-QUOTA.md; do not activate reset credits or buy credits without separate approval.
