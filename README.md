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
von Git ausgeschlossen. Es wurde kein Spielprogramm ausgeführt.

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
