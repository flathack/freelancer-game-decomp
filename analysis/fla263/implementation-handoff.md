# FLA-263 Implementierungskandidat – unabhängige Abnahme ausstehend

Arbeitsplatz /opt/data/projects/Freelancer-Decomp; eigener Worktree
build/worktrees/fla-263-equipment-ownership; Branch codex/fla-263-equipment-ownership.
Fester Kandidat ist der Commit, der dieses Dokument enthält; exakter SHA und
Remote-Readback gehören auf FLA-263, nicht in eine selbstreferenzierende Datei.
Hermes bleibt alleiniger Integrator. Kein main-Push, Amend oder Force-Push.

## Rekonstruierte Grenze

- cdecl Equipment-inherit 0x062f3e20..0x062f4170, vollständige 26er-Tabelle
  8..33 einschließlich Defaultklasse30, Mismatch und außerhalb des Bereichs.
- Acht Assignment-Körper 0x0626ddb0/0x0626e070/0x0626eaf0/0x0626dbb0/
  0x0626e2c0/0x0626f660/0x0626f870/0x0626fa10; Root-Zuweisung
  0x062f0340..0x062f054a; realer Pointervektor 0x062fb660.
- Root-/Equipment-/Attached-Defaults, Kopierkonstruktion, Client-Ownership,
  feldweise gefüllte Baum-/Payload-/Vektorkopie, Freigabe und deleting/cookie.
  Originale Helperspans aus dem unveränderten Scope-Manifest werden referenziert.
- Echter unsigned Lookup 0x063015d0 und Kopierdispatcher am vorhandenen Reader.
  Basistyp-Classgetter liefern korrekt 0/6/7; Klassen8/9 sind Subtyparme.
- GoodInfo-CommReferrable Slot+8 0x0632e6a0..0x0632e71a, voller Stringscan
  VOR min(length,63), realer GoodInfo-Konstruktor-/P1-Callbackanschluss.
  Base-/Derived-Tabellen sind unterscheidbar; keine feste Rückgabefixture.

Scope unverändert c93583dcdca63e257d9a18dd9d51aa62905f5042 auf Basis
bf555cdc5e177cb3a2485d98e6bca18ffabe5db2, Planrevision
50ba5c40-d2b3-4127-8347-2466925156bf. analysis/fla255 wurde nicht regeneriert.
common.dll SHA256 e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483.
Exakte Originaladressen/Spans/Hashes: analysis/fla255/original-evidence.json,
original-spans.md; Provenienzaudit bestätigt 84 vorhandene Spans frisch.

## Dateien

Produktion: src/archetype_ownership.cpp/.hpp, src/good_info_comm.cpp/.hpp.
Neue Tests: verify_archetype_ownership_x86.py,
verify_archetype_lifecycle_x86.py, verify_archetype_ownership_edges_x86.py,
verify_archetype_ownership_defects_x86.py, verify_good_info_comm_x86.py,
run_fla263_regressions.py, verify_fla263_evidence.py und zwei Leaf-Runtimefixtures.
Eigene Evidenz: analysis/fla263/*.json, ownership-expectations.md und
resumption-handoff.md. Veröffentlichte P1/P2-/FLA-126-Dateien bleiben bytegleich.
Originaldateien, Archive, Raw-Decomp-Ausgaben, .tools/.venv und build bleiben lokal
und gehören NICHT in den Commit oder zu GitHub.

## Reale Ausführung / getrennte Zählung

Wiederverwendete abschließende Exit0-Läufe (Testhash und private Logdatei geprüft):
  .venv/bin/python tests/verify_archetype_lifecycle_x86.py
  .venv/bin/python tests/verify_archetype_ownership_x86.py
  .venv/bin/python tests/verify_archetype_ownership_defects_x86.py
  .venv/bin/python tests/verify_archetype_ownership_edges_x86.py
Befehle, Exitcodes, Zeiten, Testhashes und Logpfade: execution-current.json.
Callback: verify_good_info_comm_x86.py; vollständiges final-run.log passt exakt
zum comm-verification.json; drei aufgezeichnete Build/Link-Schritte Exit0,
384 reguläre Callback-RET4-Paare, 24 Faultpaare und vier verworfene Mutanten.

Dieser Wake hat NICHT erfolgreiche Vergleiche erneut gestartet. Neu ausgeführt:
  PATH="$PWD/.tools/bin:$PATH" .venv/bin/python tests/run_fla263_regressions.py --supplemental
  Exit0: sieben zusätzliche vollständige Dependency-/Lookup-Suiten, alle Exit0,
  ursprüngliche Berichte erhalten. Einzelbefehle/Exitcodes/Zeiten/Logs im
  regression-supplemental-verification.json. Vorheriger vollständiger
  13-Suiten-Lauf unverändert in regression-verification.json.
  .venv/bin/python tests/verify_fla263_evidence.py
  Exit0: saved-real-execution-Provenienzaudit PASS, kein neuer Differentiallauf.

Gruppierte tatsächlich ausgeführte Szenario-Paare, keine Rekonstruktionsquote:
  Ownership: 11946 regulär, 0 Fault.
  Lifecycle: 720 regulär, 12 Fault.
  Edges: 267 regulär (inklusive sechs tatsächlicher Nullallocator-Returns), 30 Fault.
  Callback: 384 regulär, 24 Fault.
  Summe: 13317 reguläre Szenario-Paare und 66 Faultpaare; Nullallocator-Returns
  nicht zu Faults umetikettiert. Ein Szenario kann mehrere ABI-Aufrufe enthalten.
  Lifecycle separat: je Seite 1620 tatsächliche äußere ABI-Returns,
  Root-Destruktor 288, GoodInfo-Destruktor 72 und 162 deleting-RET4-Aufrufe.
  Verschachtelte CRT-Iterator-Destruktoren nicht als äußere ABI-Returns gezählt.
  20 vollständige Baseline-Suiten (13+7), keine quick Runs.
  19 tatsächlich kompilierte und verhaltensseitig verworfene Defektkontrollen.
  35 Original-Denialspans im neuen Image aktiv und explizit geprobt.

N01–N15-Zuordnung mit konkreten unabhängigen Erwartungen/Testfunktionen:
acceptance-evidence.json. Status jeder Zeile: evidence_ready_for_independent_review,
NICHT approved. Reguläre/Fault-Paare, ABI-/Destruktorreturns, Quell-/Test-/Loghashes
und modellierte Dienste werden dort getrennt geführt. Scope-Matrix bleibt als
historischer abgenommener Plan unverändert, einschließlich ihres damaligen
planned_not_executed-Status; neue Ausführung steht ausschließlich in neuer Evidenz.

Modelliert bleiben Allocator/free mit Poisoning, externe Client-/Payload-Dienste
und Faultinjektion, INI-/ASCII-CRT-Blätter, TEB/FS sowie CRT-Arrayiteration.
Kopie/Dispatch/Query/Callback/Container-/Destruktionswirkungen sind echte
kompilierte Rekonstruktion; Originalkörper auf neuer Seite gesperrt.

## Grenzen und nächster Schritt

Reale Archetype::LoadEquipment/DB/Factories/Ships/Hulls, kompletter Goods-Dateilader,
native Windows/CRT/SEH/unmasked x87 und universelle Korruptions-/Überlappsicherheit
nicht beansprucht. P01–P08/W01 und P1-malformed 0x06270e80/0x06270ef5/0x06270f51
bleiben offen. Native Runs: 0; tatsächliche Datei-/DB-Laderfälle: 0; Gesamtspiel offen.

Athena 6101f6df-1da1-4e58-8069-52c95b43f4e5 ist der bestehende unabhängige Reviewer,
kein NASA-Conan. Native Athena-Review erst mit isolierter read-only Kopie am festen
Commit, keinerlei Schreibrechten am Integrationscheckout, eigener Herleitung
Original-/ABI-/Testerwartungen und Befunden auf DIESEM Issue; Findings an Hermes.
Danach explizite Apollo-Approval und gesonderter Integrationsauftrag.

Aktueller Startblocker: Athena ist codex_local, öffentliche Agentantwort enthält
keine Adapterconfig; configuration-Endpunkt HTTP403. Der vorhandene Helfer
/opt/data/paperclip-guards/codex_quota.py prüft vor Codex-Start und alle60s,
sein tatsächlicher Einsatz durch Athena ist aber nicht belegt. Keine Rechte
umgehen, keine Agent-/Setup-Änderung. Berechtigter Verantwortlicher muss den
Schutzstart verifizieren, bevor die native Reviewstufe ausgelöst wird.

Pflicht für jede Folgezuweisung: exakter Projektpfad
/opt/data/projects/Freelancer-Decomp; nur bekannt strikt MEHR ALS30% Codex-
Wochenrest, geschützter Start und 60-Sekunden-Wächter für ALLE Rollen.
Bei <=30% oder unbekannt stoppen, Dateien erhalten, keine Credits/Resets.
Hermes-Elternlauncher in diesem Wake geprüft, frische Quote31%, keine Delegation
unter unbekanntem Schutz. DailyTasks-/Vault-Nebenarbeit aus diesem Wake ausgeschlossen;
DailyTasks-ID keine (vorher dokumentiert, kein neuer Bezug erfunden).
