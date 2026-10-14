# P1 Goods blockreader: original boundaries (14.10.2026)

Implementation scope fixed BEFORE source changes. Base: published commit
20a5883c71f57891f7151a4d000c6c854f68ccd0. Private original common.dll SHA256:
e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483.

Observed with GNU objdump against ORIGINAL PE bytes:

    objdump -d -Mintel --start-address=0x062708c0 --stop-address=0x062710f0 original/.../EXE/common.dll

Function entry 0x062708c0; RET 8 at 0x062710ea; exclusive code end
0x062710ed (three following NOPs precede load at 0x062710f0).
Half-open original spans:

- prologue/read first value: 0x062708c0..0x062708f5
- nickname/duplicate early return: 0x06270900..0x06270954
- equipment resolution: 0x06270954..0x06270989
- free_ammo: 0x06270989..0x062709d1
- name aliases: 0x062709d1..0x062709f7; handler 0x0627101b..0x0627102c
- info aliases: 0x062709f7..0x06270a1f; handler 0x0627100a..0x0627101b
- four-category table/unknown diagnostic: 0x06270a1f..0x06270a9c
- ship resolution: 0x06270a9c..0x06270ad0
- price dispatch/handler: 0x06270ad0..0x06270b69 (REUSE published handler)
- multiplier dispatch/handlers: 0x06270b69..0x06270bf1 (REUSE published handlers)
- jump_dist: 0x06270bf1..0x06270c10
- cached visual strings/HP_child: 0x06270c10..0x06270d1a
- hull lookup and UNCHECKED pointer read at 0x06270d61: 0x06270d1a..0x06270d6f
- addon parse, signed count clamp, truncated class, list append: 0x06270d6f..0x06270fe3
- combinable raw AL: 0x06270fe3..0x06270fff
- unknown-key virtual dispatch at GoodInfo vtable+8: 0x06270fff..0x0627100a
- read next value: 0x0627102e..0x06271041
- metadata/category finalization, unchecked GetEquipment result, vtable+0x24:
  0x06271041..0x062710ca
- shop_archetype fallback alias: 0x062710ca..0x062710e0
- epilogue: 0x062710e0..0x062710ed

Category table at 0x063e96c0 contains Commodity=0, Equipment=1, ShipHull=2,
Ship=3. Resolver at 0x062f11d0 is labeled GetAsteroidID by Ghidra, but shared
aliases are not proof of semantic database creation; keep it an explicit
runtime dependency. Getter/traversal dependencies: read_value 0x06310200,
is_value 0x063104a0, is_value_empty 0x063105f0, bool 0x06310640,
int 0x06310850, full-ST0 float 0x06310980, indexed string 0x06310ac0,
whole string 0x06310c00. Hash 0x0630d470, tree query 0x063015d0,
GetEquipment 0x062f9370, StringAlloc 0x06333bd0, CacheString clear
0x06333d60, operator new 0x06391abc.

Addon helper inspection: EquipDesc constructor 0x06309990; copy helper
0x0626c400 copies ONLY defined members, NOT padding. Node size 40; links
at +0/+4 and descriptor at +8. Append preserves seeded node padding. Lists
in GoodInfo: low head/count +0x98/+0x9c, mid +0xa4/+0xa8, high +0xb0/+0xb4.
Internal hardpoints use the shared BAY cache pointer at global 0x063fbf0c.
Descriptor subobject ID is read from global 0x063a4a74 (not guessed).

## Executed candidate evidence

Reproduction (all shell commands start at the project root):

    cd /opt/data/projects/Freelancer-Decomp
    source tools/paperclip-env.sh
    .venv/bin/python build/worktrees/fla-124-p1/tests/verify_good_block_reader_x86.py

The source/test/fixture/report live ONLY in isolated worktree
`build/worktrees/fla-124-p1`, branch `codex/fla-124-p1-blockreader`, on the
published base. `original`, `.tools` and `.venv` are ignored private runtime
input directories with links to the root inputs; no original bytes are staged.
A separate reviewer must use her OWN fixed-commit copy and link private inputs,
not rebuild or overwrite this implementation worktree. Exported block ABI is
thiscall (ECX=list, reader/good on stack, RET 8), storage extent 192 bytes.

Final full run (14.10.2026):

- 6,696 paired original/reconstructed blocks across twelve x87 control words.
- 13,296 successful real ABI calls (both sides combined), checking RET 8 and
  preservation of EBX/ESI/EDI/EBP. Faulting blocks are not counted as ABI returns.
- 13,296 original/reconstructed destructor calls (both sides combined), linking
  the EXISTING reconstructed GoodInfo destructor without rewriting it. Full
  object/heap/free-callback states and order compare exactly.
- Each of the 6,696 blocks additionally passes an independent expectation oracle:
  field values, raw bool byte, ID/reference results under the service contract,
  category/default/metadata/cache fallback, unknown callback, duplicate stop,
  three addon lists, signed count clamp, internal BAY handle, defined descriptor
  fields, seeded padding and node/sentinel free order. These are oracle CASES,
  not a claim of 6,696 unique expectations or independently reviewed tests.
- Full 320-byte guarded object region and 4,096-byte seeded heap compare; random
  object padding/guards and seven padding bytes per allocated node are retained.
  Reader/service call ORDER compares. The rebuilt side is prohibited by a code
  hook from entering original blockreader addresses.
- x87 CW/SW/tag and live binary80 values compare, with zero or two preexisting
  stack values. FPU pointers and empty-register residual bytes are excluded.
  Published price source/headers remain byte-for-byte unchanged.
- 48 paired FAULT cases: missing hull read at 0x48; missing equipment metadata
  read at 0x14; missing equipment vtable read at 0; unterminated addon-level
  source read at the unmapped page boundary. Twelve repetitions of each; these
  are preserved original faults, NOT successful missing-reference handling.
- Original instruction-address observation: 617 of 620 decoded instructions
  executed. Unexecuted 0x06270e80, 0x06270ef5, 0x06270f51 are the null-previous
  list-link fallback for malformed sentinels. Do not call this full coverage.

Six intentionally wrong rebuilt variants, 260 probe pairs EACH, all rejected:
raw-bool normalization (254 mismatches), wrong addon list (1), node-padding
zeroing (1), skipped duplicate early return (1), safe missing-hull replacement
(1), and bounded addon-level scan (1). Repetitions are not unique defect counts.
Negative-control calls are excluded from the 13,296 real ABI/destructor totals.
Source, fixture, test, imported harness/helpers, original span and build hashes
are pinned in `analysis/good-blockreader-x86-behavior.json`.

A real red/green edge-case test found that a bounded 63-byte level scan would
hide the original fault: original scans the FULL source to NUL BEFORE truncating.
The final reconstruction does the same, and a compiled bounded-scan mutation
is now explicitly rejected. Builds use `-Wall -Wextra -Werror` without warnings.

## Explicit service/stub limits

Reader traversal/getters, hash IDs, cache allocation, ID-to-Archetype resolver,
Goods-index lookup, GetEquipment metadata objects, diagnostics and virtual
callbacks are controlled fixtures. The ID fixture is CRC32-based and explicitly
NOT the game's CreateID. Real reconstructed hash/cache/reader/index services
are NOT integrated by this test. Original helper executions on the ORIGINAL
side do not count as reconstructed implementation; the new side links only
the new blockreader, existing price code and existing destructor plus fixture.

No real Goods corpus, full file-loader lifecycle, Archetype database creation,
virtual subtype reader implementation, native Windows/CRT/heap execution,
allocation failures/exception unwinding, malformed-list completeness, arbitrary
stack/storage aliasing, unmasked x87 exceptions or whole-function byte identity
is verified. Null input strings beyond the explicit addon-level case remain
outside the valid fixture contract. The full game remains unfinished.

Athena must independently inspect the fixed commit AND run her own original
comparison in a separate working copy. Apollo's NEW P1 approval follows. No
main integration, README/global progress refresh or main push before that gate.
Next dependency work after P1 approval: connect actual reconstructed reader,
hash/cache/index services and recover required Archetype metadata/virtual reader
functions before the real Goods file-loader/corpus milestone.
