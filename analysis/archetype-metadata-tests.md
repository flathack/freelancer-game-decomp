# FLA-246: Test- und Handoffbericht v1

Feste Basis `8f44ff91f1086f33fd81ca1c4f65f637a9733bf2`. Candidate-SHA wird nach Commit unveränderbar auf dem Issue dokumentiert.

## Tatsächlich ausgeführt

P2: 6506 Original/Rekonstruktionspaare und 13012 unabhängige Reader-Oracleprüfungen. Zusätzlich 600 Readerpaare in 30 gemischten Sequenzen. 128 gekoppelte P1-Paare, 256 ABI- und 256 Destruktoraufrufe. 12 zusätzliche Lookup-Grenzpaare, 5 zusätzliche Low-address-Faultpaare. Fünf unerlaubte Original-P2-Einstiege tatsächlich durch Fallback-Hook abgebrochen. Keine echte DB-/Loaderprobe (0).

Vollständige unveränderte P1-Regression: 6696 Paare, 13296 erfolgreiche ABI- und 13296 Destruktoraufrufe; 6696 unabhängige Oraclefälle. Faultfälle sind separat gezählt, keine erfolgreichen Returns. Alle sechs bisherigen P1-Defektkontrollen erkannt. Lookup: 96000 Equipment-Vergleiche/Fehlerlogs, 48000 Alias-Aufrufe.

Die neuen technischen Reports und Dokumente sind keine Apollo-Abnahme. Die zwei neuen Tests verwenden reale rekonstruierte CreateID/StringCache-Dienste, P1-Bestandsregression behält unveränderte kontrollierte Dienste. Mengen nicht als neue Rekonstruktionsquote addieren.

## A01–A18

| Kriterium | Implementierer-Evidenz |
|---|---|
| A01 | 118 all-key pairs, direct/slot+4; independent field/AL/getter traces; no duplicate base getters |
| A02 | 80 reader ID-vector pairs, null/empty/case/255 bytes, real CreateID; existing pinned vectors unchanged |
| A03 | 12 additional existing/null-payload/missing unsigned boundary pairs and 96000 unchanged lookup calls |
| A04 | 108 integer-boundary pairs; repeated ids_name and 128 coupled own/fallback metadata cases |
| A05 | 29 original token/value entries, mixed case in all three types: 174 pairs plus 6 unknown-type pairs |
| A06 | 3584 pairs: all 256 raw bytes phantom_physics across 3 types, use_count/lootable across 2; adjacent bytes unchanged |
| A07 | raw units_per_container/toughness signed/dword boundaries; independent exact write set, no clamp |
| A08 | 2352 float80 pairs plus 24 full-ST0 discriminator pairs, 12 CWs, older live registers and CW/SW/tag/binary80; emulator NaN contract only |
| A09 | 18 cache pairs plus 30 sequences: flags 1/1/0, local clear, counters, private handles/intern aliases/old handles; no free |
| A10 | 24 callback pairs, raw Root AL 0/1/0x80/0xff, derived normalization and visible ids_info side effect |
| A11 | 12 inherit pairs: diagnostics 2/1/0, dispatch 0/0/1, target/source and visible service side effect; copy body remains controlled |
| A12 | 4 is_attached pairs with Equipment/Attached tables swapped; independent false/true and unchanged this/storage |
| A13 | 128 reader-created metadata -> reconstructed accessor/lookup -> unchanged P1 pairs, categories 0/1 and 2/3; actual virtual bool bodies; string alias through teardown |
| A14 | 5 extra low-address fault pairs at 0x14/0x18/0/0x48, null page unmapped; full P1 additionally reports its fault cases separately |
| A15 | 6506 pairs with nonvolatile registers/RET4, random storage/guards, 600 mixed-sequence reader pairs; P1 RET8/ABI and teardown independently checked |
| A16 | fresh complete unchanged Lookup and P1 suites; P1 6696 pairs /13296 successful ABI/destructors/6 defect categories; no quick acceptance |
| A17 | all 10 separate compiled defects rejected at named discriminators after passing original pair and independent expectations |
| A18 | technical handoff hashes/commands/isolated candidate and rights verified; independent Athena review and exact-SHA Apollo approval PENDING; no integration |

## Zehn wirksame kompilierte Defektkategorien

- wrong_ids_name_offset: gezielte Probe {"key": "ids_name", "integer": 2147483648}; erkannt. Build SHA256 2e8b6fa717ec8301eeca58b57653a993cedbd119456ddb5e40a56ad150534eef; kompilierter Mutationsquellhash 668beb8ab357cc6aad30ba2053b5210f6fa7f56c14e0758f2fa392140171946d.
- normalize_raw_field_bool: gezielte Probe {"key": "phantom_physics", "integer": 254}; erkannt. Build SHA256 b48d82624ac5353de61a3cfc28b6504e3f398a5db91200719179296d2e9353bf; kompilierter Mutationsquellhash 5f852164dec46a123e7afd5891ad1340a70617c577909b127c493e6c26829af7.
- constant_true_is_attached: gezielte Probe {"slot": "0x24", "table": "Equipment"}; erkannt. Build SHA256 2110c4073e9372bf50685be5006c245fe5e8e36ccdf0f08ddff801cfd01f47c3; kompilierter Mutationsquellhash 542f8b101ea7bcd26a3c1bce00510a9cdbb9c312834cc4070a072f6fb6f2b2f5.
- skip_root_base_hit: gezielte Probe {"key": "ids_name", "integer": 42}; erkannt. Build SHA256 77b406b1a2725c910b75d2c19bf6a9c9e299b9a07043464bc6333a99383904a8; kompilierter Mutationsquellhash 37477286869128325e759fb9e7822eb246defd768f4b0932e7796df759b03f8c.
- normalize_root_callback_al: gezielte Probe {"key": "not-a-key", "client": true, "callback": 128}; erkannt. Build SHA256 6b75a2759ef9cacc07a077b22a8c87ba68f924c595708c4f125175e78e732fca; kompilierter Mutationsquellhash abbfe5a197d7d8eacd74be171fe4aede184e7a706a39874322a793f378231a0c.
- root_string_flag_zero: gezielte Probe {"key": "DA_archetype", "text": "MixedCase"}; erkannt. Build SHA256 79a9b7e2d2d7e2e70f5d56c6884f13e7d931f4f7241a09f43ac21e8c1efb2dd8; kompilierter Mutationsquellhash b6796ccf784c8be5c064f9406d468f3dba6696cb7a91d84a563384b9c82920fe.
- free_old_cache_handle: gezielte Probe {"key": "DA_archetype", "text": "MixedCase"}; erkannt. Build SHA256 51efda6390752b632f3beee6a0dbfbef85be060650c5909882b83399d8b20050; kompilierter Mutationsquellhash 368fabd970ae16688153df1d32e5703553ce77d850347af6e370d5d0a69b24db.
- merge_inherit_missing_null: gezielte Probe {"key": "inherit", "text": "li01", "entry": "missing"}; erkannt. Build SHA256 ac25b52f7a694975421c1abb6f157e53a8ccb0664a87c9060a9c646128624f73; kompilierter Mutationsquellhash af4de04f3af39fdc2db67c116bf10b3ef9447dc79516975cf2dae872b56c4b2a.
- swap_dispatch_arguments: gezielte Probe {"key": "inherit", "text": "li01", "entry": "valid"}; erkannt. Build SHA256 a9a8ddf62bd497ec5cbb2da5b60b3bf070093fcc744e25f3a1c240fb49d4b25f; kompilierter Mutationsquellhash a792e0cfcc61018f2353dd1e3b47c14563bcf673088fe1f39cd17f0183c6c96f.
- early_binary64_spill: gezielte Probe {"key": "hit_pts", "floats": ["0100000080000080ff3f", "0100000080000080ff3f", "0100000080000080ff3f"]}; erkannt. Build SHA256 9a498b439e83532995d67223dc5e54069377bfac747ab726851b23d5e7408526; kompilierter Mutationsquellhash fb8c039efa601e7edd335a93187cec9b89aae9a36ba49ecb15daeeb0164d7c36.

## Reproduktion und unveränderter Scope

Projektpfad `/opt/data/projects/Freelancer-Decomp`. Nur bei bekannt strikt MEHR ALS 30% Codex-Wochenrest starten/arbeiten/delegieren, geschützter Start plus minütlicher Wächter. <=30%/unbekannt: stoppen, Dateien erhalten; keine Credits/Resets. Review read-only in EIGENER fester Kopie.

    export PATH="/opt/data/projects/Freelancer-Decomp/.tools/bin:$PATH"
    /opt/data/projects/Freelancer-Decomp/.venv/bin/python tests/verify_archetype_metadata_x86.py
    /opt/data/projects/Freelancer-Decomp/.venv/bin/python tests/verify_archetype_metadata_coupled_x86.py
    /opt/data/projects/Freelancer-Decomp/.venv/bin/python tests/verify_archetype_lookup_x86.py
    /opt/data/projects/Freelancer-Decomp/.venv/bin/python tests/verify_good_block_reader_x86.py

Diese vier Befehle wurden tatsächlich mit Exit 0 ausgeführt. Alle tatsächlichen Builds/Exitcodes stehen in den JSON-Berichten und audit-commands.jsonl; frühere fehlgeschlagene Diagnostikläufe bleiben dort sichtbar, werden nicht als bestandene Abnahme gezählt. Voller P1-Bericht separat fla246-p1-regression.json, historischer P1-Bericht unverändert.

Original-/Rekonstruktionsmaschinen laden getrennte Images. Auf der neuen Seite sind alle fünf P2-Originalspans und der P1-Originalspan verboten. Nur explizite kontrollierte Dienstgrenzen und bereits rekonstruierte Abhängigkeiten sind zugelassen.

Native Windows/CRT, echte DB-/Dateiladung, inherit-Kopierwirkung, GoodInfo-Callback, malformed-Sentinel, unmaskierte x87-Ausnahmen und Gesamtspiel bleiben offen.

DailyTasks: context und OpenAPI gelesen; q=Paperclip&limit=100 ergab tasks=[], nextOffset=null. Keine DailyTasks-Aufgaben-ID, keine Mutation oder Ersatzaufgabe. Vault-Pull --rebase scheiterte an HTTPS-Authentifizierung; relevante lokale Seiten gelesen, kein erfolgreicher Sync behauptet.

Schutzstart durch Elternprozess /opt/data/paperclip-guards/freelancer_quota.py, INTERVAL=60 geprüft. Liveproben 47%, 46%, 45% Rest im ursprünglichen Implementierungslauf; Wiederaufnahme am 14.10.2026: frisch 44% Rest (alle >30%). Zwei P2-Suiten nach ausschließlich Testhilfs-/Hashkorrektur erneut mit Exit 0 ausgeführt; Implementierungsquelle unverändert übernommen. Sechs Setup-Dateien und Hauptcheckout HEAD/Status vor/nach identisch. Keine Arbeit im Integrationscheckout, kein Commit/Push dort.
