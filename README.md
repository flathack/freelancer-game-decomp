# Freelancer matching decompilation

Arbeitsbasis ist die bereitgestellte deutsche Installation aus `_FL Fresh Install-deutsch.7z`.
Das Ziel ist rekonstruierter C/C++-Code mit nachgewiesenem Maschinencode-Matching.
Dies ist der Projektstart, noch kein vollständiger oder spielbarer Neubau.

## Nachgewiesener Stand

- 8.456 Originaldateien mit SHA-256 erfasst.
- 46 EXE/DLL-Kandidaten mit PE-Metadaten erfasst.
- 5.644 Export-Einträge dokumentiert. Diese Zahl ist **keine Funktionsanzahl**:
  Aliase, Datenexporte und Forwarder können enthalten sein; interne Funktionen fehlen.
- Zwei rekonstruierte `CSimple`-Methoden aus `common.dll`: je 7 Bytes passen exakt.
- `CreateID` in C++ rekonstruiert; 636 ASCII/Null-Testfälle stimmen mit dem emulierten Originalcode überein. Noch kein Maschinencode-Match für diese Funktion.
- `Freelancer.exe`, `common.dll` und `content.dll` melden Dateiversion `1.0.1223.11`.
  Die Versionsressource beweist weder Originalzustand noch Patchstatus.

## Wiederholen

Voraussetzungen: Python 3 mit `pefile` (siehe `requirements.txt`), `clang++`, GNU `objdump`.
Für einen noch nicht entpackten Bestand: `7z x '_FL Fresh Install-deutsch.7z' -ooriginal`.

```bash
python3 tools/inventory.py
python3 tools/verify_matches.py
.venv/bin/python tests/verify_create_id.py
python3 tools/disassemble_export.py \
  'original/_FL Fresh Install-deutsch/EXE/common.dll' \
  '?CreateID@@YAIPBD@Z' --bytes 128
```

`verify_matches.py` kompiliert für x86/Windows mit der Microsoft-C++-ABI und prüft
gegen die festgehaltene Prüfsumme der Original-DLL. Der Vergleich umfasst die
beiden bekannten Funktionskörper bis einschließlich `ret`, nicht das Alignment
oder einen gelinkten PE-Build. Clang ist damit für diese zwei Methoden geeignet;
die ursprüngliche Compiler-Version ist noch nicht abschließend bestimmt.

## Dateien

- `original/`: entpackte Spieldateien, von den Analysewerkzeugen nur gelesen.
- `src/csimple.cpp`: selbst rekonstruierte Methoden und partielles Layout.
- `analysis/inventory.md`: lesbare Modulübersicht.
- `analysis/files.json`: Dateiliste und Prüfsummen.
- `analysis/modules.json`: Sektionen, Versionsressourcen, Imports und Exports.
- `analysis/targets.json`: ausgewählte Symbole, Adressen und Codegrößen.
- `analysis/matches.json`: reproduzierbare Matching-Ergebnisse.
- `analysis/*-original.asm`, `analysis/*-compiled.asm`: Vergleichsbelege.
- `reference/Liberty/`: separat geklonte Referenz, kein Bestandteil unseres Quellcodes.

## Nächste Arbeit

1. Weitere `common.dll`-Klassen anhand benannter Exports und Aufrufstellen rekonstruieren.
2. `CreateID`-Rekonstruktion an Original-ABI und Allokation anpassen und Richtung
   Maschinencode-Matching weiterentwickeln; Verhaltenstest ist bereits vorhanden.
3. Compiler und Build-Konfiguration anhand mehrerer nichttrivialer Funktionen eingrenzen.
4. Funktionen in Objektdateien rekonstruieren und Relokationen/ABI systematisch prüfen.
5. Erst nach Funktions- und Linkerarbeit einen vollständigen PE-Build vergleichen.

Prozentzahlen für das Gesamtspiel bleiben aus, bis der Umfang zuverlässig definiert
ist. Export-Aliase werden beim späteren Fortschritt nach Adresse zusammengefasst.

## Referenz

[Liberty](https://github.com/HaydnTrigg/Liberty) ist ein bestehendes Freelancer-
Reverse-Engineering-Projekt. Seine README beschreibt den Stand als Excalibur-
Prototyp und kündigt einen delink-basierten Matching-Ansatz an. Der hier geprüfte
Commit steht in `analysis/baseline.json`. Im eigenen `src/` wurde kein Liberty-Code
übernommen. Eine spätere Übernahme muss dessen GPL-3.0-Lizenz berücksichtigen.

Spieldaten, Originalbinärdateien, das Archiv und lokale Referenz-Checkouts sind
von Git ausgeschlossen. Kein Spielprogramm wurde als nativer Prozess gestartet;
Originalinstruktionen werden für Vergleiche im Emulator ausgeführt.

## Roh-Decompilation aller Module

Ghidra 12.1.4 liegt lokal in `.tools/`; Archiv-Prüfsumme und Release stehen in
`analysis/baseline.json`. `tools/decompile_all.py` analysiert die 34 Module mit
Code in `EXE/` und `DLLS/BIN/`, einschließlich mitgelieferter Bibliotheken und
Hilfsprogramme. Reine Ressourcenmodule und Installer sind im Scope-Manifest
separat erfasst. Die Roh-Ausgabe stellt noch keine vollständige Rekonstruktion dar.

```bash
python3 tools/decompile_all.py
python3 tools/progress.py
```

Je Modul: `analysis/raw/<Modul>/raw.c`, `functions.tsv`, `calls.tsv`,
`summary.json`, `provenance.json`. Die Ghidra-Projekte bleiben in
`analysis/ghidra-project/` zur weiteren Typ- und Funktionsanalyse erhalten.
Fehler und laufende Module stehen in `analysis/decompile-run.json`; vollständige
Logs in `analysis/ghidra-logs/`. Ein Prozessstatus in JSON allein beweist nicht,
dass der Prozess noch läuft. Vor einer Fortsetzung den Prozess prüfen.
Die Batch-Dateisperre verhindert zwei gleichzeitige Batchläufe.

Roh-C kann falsche Typen, unerkannte Funktionen, fehlerhafte Kontrollflüsse und
Decompiler-Platzhalter enthalten. Der Bericht `analysis/progress.md` unterscheidet
Roh-Analyse, Verhaltenstests und genaue Maschinencode-Matches. Ein vollständiger
kompilierbarer Build und dessen breite Verifikation bleiben erforderlich.

## Vollständigkeit der Funktionsanalyse

Die Standardanalyse erkennt nicht alle Funktionen. Für `common.dll` lagen anfangs
118.738 bereits disassemblierte Bytes außerhalb jeder erkannten Funktion.
`RecoverOrphanFunctions.java` legt zusätzliche Funktionen nur an, wenn der Beginn
eines solchen Instruktionsbereichs durch einen Aufruf oder Datenzeiger referenziert
wird. Diese Grenzen sind zunächst **abgeleitet**, keine verifizierten Funktionen.
Nach dieser Ergänzung gibt es 8.568 rohe Funktionsausgaben in `common.dll`.

```bash
python3 tools/enrich_analysis.py
python3 tools/audit_context.py common.dll
python3 tools/progress.py
```

Die Ergänzung verarbeitet nur Module mit abgeschlossenem Roh-Export und kann
nach weiteren Batch-Ergebnissen wiederholt werden. Sie exportiert außerdem
`recovered-types.h`, `instructions.tsv`, `defined-data.tsv` und
`unclassified-executable.tsv`. Der Byte-Audit vergleicht jede exportierte
Instruktion mit der Originaldatei. `coverage-summary.json` hält die kompakten
Ergebnisse fest. Padding-Kandidaten sind noch kein Beweis für ungenutzte Bytes.

Ein Export ohne Decompiler-Abbruch kann weiterhin Warnungen, falsche Typen und
fehlende Funktionen enthalten. Insbesondere stellen weder erfolgreiche Roh-
Exports noch hohe Instruktionsabdeckung einen vollständigen Spiel-Build dar.

## Kompilierte CFLIDMaker-Klasse

`src/cfl_id_maker.hpp` und `src/create_id.cpp` enthalten jetzt den vollständigen
hier untersuchten Klassenbereich einschließlich Singleton, CRC-Zustand und
Lebenszyklus. `tests/verify_flid_x86.py` baut eine x86-Windows-Test-DLL und prüft
ihre Methoden gegen die Originalmethoden im Emulator. Die produktiven CRT- und
Logging-Bindungen sind noch offen; die Test-DLL ersetzt nicht `common.dll`.

```bash
.venv/bin/python tests/verify_flid_x86.py
```

505 Hash/Zustandsfälle, 28 Zählerfälle, 400 Byte-Update-Fälle und Lebenszyklus- sowie
Allokationsfehlerprüfungen bestehen. Details stehen in `analysis/createid-notes.md`
und `analysis/flid-x86-behavior.json`. Das wird als Verhaltens- und ABI-Prüfung
gezählt, nicht als exaktes Maschinencode-Matching.

Der Roh-Export und die Ergänzungsanalyse sind für alle 34 Module abgeschlossen.
Es gibt momentan 54.832 rohe Funktionsausgaben und keinen Decompiler-Abbruch.
13.450 Funktionen enthalten jedoch explizite Decompiler-Warnungen; diese sind
in `analysis/reconstruction-backlog.json` verzeichnet. `tools/reconstruction_backlog.py`
priorisiert substanzielle Funktionen vor Import-/Sprungthunks und berücksichtigt
die Zahl ihrer Aufrufer. Das sind Review-Signale, keine vollständige Fehlerliste.

Eine falsche Ghidra-Funktionsgrenze bei VA `0x004b6425` in Freelancer.exe wurde
anhand der Originalbytes korrigiert: Die tatsächliche Instruktion beginnt bei
`0x004b6420`, und `0x004b6425` liegt in deren Adressoperand. Das baselinegebundene
Reparaturskript und die Roh-Export-Metadaten halten diese Änderung fest.

## Equipment descriptor

`src/equip_desc.hpp` und `src/equip_desc.cpp` rekonstruieren die 26 exportierten
Methoden von EquipDesc und dessen 32-Byte-x86-Layout. Der Emulatorvergleich besteht
für 2.406 ABI-/Speicheränderungsfälle und 200 Frachtraumfälle mit vollständig
verglichenen 80-Bit-x87-Rückgabewerten.

```bash
.venv/bin/python tests/verify_equip_desc_x86.py
```

Für die originale erweiterte x87-Rückgabe ist im Clang-x86-Build derzeit ein kleiner
Assembly-ABI-Übergang erforderlich. Dieser zählt als vorläufige Rekonstruktion,
nicht als vollständiger C++- oder Maschinencode-Match. Die Equipment-Datenbank bleibt eine kontrollierte Testabhängigkeit.
CacheString-Interning ist inzwischen rekonstruiert und im Initialisierungstest integriert.
Details: `analysis/equipdesc-notes.md` und `analysis/equipdesc-x86-behavior.json`.

## String cache and integrated equipment initialization

`src/string_cache.cpp` reconstructs StringAlloc, its two-ended 1.5-MiB arena and
original-layout red-black index. The x86 differential check passes 407 sequences
with full tree/cursor/count comparisons, eight capacity boundaries and clear().

```bash
.venv/bin/python tests/verify_string_cache_x86.py
```

EquipDesc now initializes its actual BAY handle through this reconstruction.
Its test executes the original initializer and reconstructed CRT callback;
the previous fake handle has been removed. Production runtime bindings,
non-ASCII/locale comparison and allocation failure/SEH are still open. Cache
destruction and reinitialization have since passed differential checks. See `analysis/stringcache-notes.md` for exact test scope.

## FileMap memory and BINI read paths

`src/file_map.cpp` reconstructs 12 memory-reader methods with 3,298 passing x86
comparisons. Typed short reads consume the remaining tail before returning false.
The remaining FileMap methods have since been implemented and tested under
modeled imports; the full INI parser and native CRT/OS verification remain open.

```bash
.venv/bin/python tests/verify_file_map_x86.py
```

Scope and evidence are recorded in `analysis/filemap-notes.md` and
`analysis/filemap-x86-behavior.json`.

## FileMap resource methods and Windows component DLL

All 18 FileMap exports now compile. The copy/ownership, OS acquisition/cleanup and
COW paths pass 101 differential cases with explicit external-library models.
The named-import Windows build passes the same wrapper-ABI checks and verifies
all 18 exports / 13 CRT and Win32 imports, without fixed original-image addresses.

```bash
python3 tools/build_filemap_windows.py
.venv/bin/python tests/verify_file_map_lifetime_x86.py --production-bindings
```

The result is `build/filemap-windows/freelancer-filemap.dll`, a component DLL rather
than a common.dll replacement. Real Windows/CRT execution, SEH/allocation failure
and exact compiler matching remain unverified. Details and scope are in
`analysis/filemap-lifetime-notes.md`.
