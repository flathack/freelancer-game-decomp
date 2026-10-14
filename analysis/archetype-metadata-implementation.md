# FLA-246: P2-Archetype-Metadatenreader — Implementierung v1

Feste Basis: `8f44ff91f1086f33fd81ca1c4f65f637a9733bf2`.
Abgenommener Scope: Revision `80fd52f4-adfd-4368-aa6b-160b41cddfe7`, SHA256 `ccfa7f72b4104eec69917073b582d11227c7870e9848396504b85c94276252e7`.
Projektbezug `/opt/data/projects/Freelancer-Decomp`; isolierter Candidate `/opt/data/work/fla246/repo`, Branch `codex/fla-246-p2-metadata`.

## Lieferumfang

`src/archetype_metadata.cpp/.hpp`: Root/Equipment/AttachedEquipment-Reader mit Roh-AL-Callback, rohen Boolbytes, originaler Basistreffervorrangregel, lokalen Cache-Temporaries und getrennten inherit-Missing/Null-Payload-Zweigen. Originale Objektgrößen 0x5c/0x70/0x88 werden statisch geprüft. Reader sind x86-thiscall mit RET 4. Floatgetter liefern ST0; der Assembly-Speicherhelfer führt unmittelbar FSTP binary32 aus, ohne C++-double-Spill. Rotation inertia wird zuerst in drei lokale Werte gelesen.

Reader-slot +4 und Equipment/Attached-slot +0x24 sind in partiellen Tabellen gebunden. Alle anderen Slots sind null und ausdrücklich nicht implementiert. Root bietet keine Equipment-is_attached-Bindung. Diese partiellen Tabellen sind keine produktive vollständige Klassenhierarchie.

`tests/fixtures/archetype_metadata_runtime.cpp`: explizite Emulator-Dienstbindung. Neue Reader benutzen unveränderte rekonstruierte CreateID-/StringCache-Körper. INI, erfolgreicher Allokator, ASCII-CRT, inherit-Query/Dispatcher und Clientkörper bleiben kontrolliert. inherit-Dispatcheraufrufe einschließlich deterministischem Seiteneffekt belegen ausschließlich den Aufrufvertrag, keine rekonstruierte Kopierwirkung.

`tests/verify_archetype_metadata_x86.py`: getrennte Original-/Rekonstruktionsmaschinen, ursprüngliche vtables auf der Originalseite, eigene rekonstruierte Tabellen auf der neuen Seite; unabhängige bytegenaue Schreibmengen-/AL-/Getter-/Integer-/Float-Oracle. ID-Erwartungen stammen unverändert aus den bestehenden CreateID-Vektoren. Vollständige Original-Typentabelle wird erneut direkt aus dem gehashten PE geprüft. Cachepointer werden ausschließlich in fachlich bekannten Cachefeldern als arena-relative Handles normalisiert, nicht beliebig in zufälligen dwords.

`tests/verify_archetype_metadata_coupled_x86.py`: Wiederholung/Last-write-wins, private Kopien vs. HP-Interning, alte Stringhandle-Lebensdauer, gemischte Reihenfolgen, Lookup-Grenzen und gekoppelte P1-Finalisierung. Archetype-Nickname/ids_name/ids_info/Archetype-/HP-Pointer werden von den Readern erzeugt, nicht als Metadaten vorab eingesetzt. Der Index ist synthetisch vorbereitet; vorhandener ID-Accessor und GetEquipment werden tatsächlich ausgeführt. P1-Quelle, Preise, Destruktor und Lookup-Suite bleiben unverändert.

## Beweislage und Grenzen

Dies ist synthetische x86-Emulatorevidenz mit echten Originalkörpern im Originalvergleich, NICHT reale DB-/Dateiladeevidenz. Anzahl realer Loader-/DB-Fälle: 0. Native Windows/CRT, Produktionskonstruktion und Ownership, GoodInfo-Callback, tatsächlicher inherit-Kopierkörper, malformed-Sentinel-Vervollständigung, unmaskierte x87-Ausnahmen und das Gesamtspiel bleiben offen. FLA-126 und P1-Historie werden nicht umgeschrieben. README/Fertigstellungsquote wird nicht vor positiver Commitfreigabe verändert.

NaN-Erwartung für verschwindende Payloadbits ist ausdrücklich Unicorn-Softfloat-Vertrag, keine native x87-Behauptung. Unabhängige Referenz: Unicorn 2.1.4, `qemu/fpu/softfloat-specialize.inc.c`, Funktion commonNaNToFloat32: bei verschwindender Zielmantisse default_nan. Die Kontrollwortmatrix wie P1 umfasst PC 24/53/64 und alle vier Rundungsmodi; CW/SW/tag/live binary80 werden verglichen, Code-/Datenpointer und leere Registerreste nicht als ABI-Ergebnis behandelt.

## Gates

Candidate nur lokal, kein Push, main-Merge oder Integration. Athena prüft genau den auf FLA-246 übergebenen Commit read-only in eigener fester Kopie, ergänzt fremde Grenzprobe und führt gezielte Defektkontrollen selbst aus. Danach native Apollo-Approvalstufe auf exakt denselben SHA. Jede nachfolgende Änderung erfordert neuen Commitreview. Integration darf nur später separat aktiviert werden.

Für jede folgende Zuweisung, einschließlich Review, verpflichtend: exakter Projektpfad `/opt/data/projects/Freelancer-Decomp`; nur bei bekannt strikt MEHR ALS 30% Codex-Wochenrest arbeiten/delegieren; geschützter Start plus 60-Sekunden-Wächter. Bei <=30% oder unbekannt stoppen, Dateien erhalten, keine Credits/Resets.
