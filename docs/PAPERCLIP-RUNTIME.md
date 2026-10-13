# Paperclip runtime on hermes-srv

Project directory: `/opt/data/projects/Freelancer-Decomp`. Paperclip company FLATHACK-CORP, project Freelancer (2003) Decompilation. Responsible agent: Hermes (Hermes-SRV). Routine: Freelancer: Decompilierung fortführen, every 15 minutes, coalesce if active, skip missed windows.

```sh
cd /opt/data/projects/Freelancer-Decomp
source tools/paperclip-env.sh
.venv/bin/python tools/verify_matches.py
.venv/bin/python tests/verify_good_index_lookup_x86.py
```

Python venv rebuilt on the server with pefile and Unicorn. Ubuntu Clang/LLD 21.1.8 are extracted under `.tools/ubuntu-runtime` and invoked through `.tools/bin` wrappers (no sudo or global system changes). The original development machine used Clang 23; recheck byte matching and ABI when changing compiler. Current three exact matches pass with server Clang 21. Git push credentials already available for Hermes; dry-run push succeeded.

All source, Git history, original game archive/extraction, Ghidra program/project/raw outputs, analysis reports and build artifacts were transferred. Original local Python environment was replaced with a server-native environment. Read docs/PAPERCLIP-HANDOFF.md for reconstruction scope, remaining work and test limits.

Workflow: choose next concrete milestone → original-code reconstruction → differential test → review → update concise README and evidence → commit and push → record next milestone in Paperclip. The 15-minute trigger coalesces work instead of parallel edits to main. For several editing agents use distinct worktrees and one integrator. Never force-push over other work. This local Codex goal remains paused; Paperclip owns the continuation.

Paperclip project: https://hermes-srv.tail2b5c2.ts.net:3101/FLA/projects/freelancer-2003-decompilation
Routine: https://hermes-srv.tail2b5c2.ts.net:3101/FLA/routines/34df3d50-f7c7-4964-9aba-7fcded82076b

OpenJDK 25 is extracted alongside the compiler. Source tools/paperclip-env.sh before running builds or Ghidra. Source/original files and raw outputs passed rsync checksum comparison; server git status was clean before the first Paperclip run.
