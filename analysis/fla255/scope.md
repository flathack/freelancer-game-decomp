# FLA-255 – Goods-P3-Scope und notwendiges P2-Restpaket, Revision 1

Stand: 14.10.2026. Auftrag ausschließlich Originalanalyse und Scope-Handoff unter FLA-129. Keine Spielimplementierung, keine Implementierungsfreigabe, keine main-Veröffentlichung. Native Athena-Review und danach Apollo-Scope-Abnahme stehen noch aus. Gesamtspiel bleibt offen.

## 1. Feste Grundlage und genau ein nächster Vorschlag

Referenzcommit: `bf555cdc5e177cb3a2485d98e6bca18ffabe5db2` (veröffentlichte P2-Integration aus FLA-253). Der feste Scope-Commit wird nach dem Commit auf FLA-255 dokumentiert; dies vermeidet einen unmöglichen selbstreferenziellen SHA im Dokument.

Arbeitsplatz: `/opt/data/projects/Freelancer-Decomp`. Scope-Artefakte ausschließlich im Worktree `/opt/data/projects/Freelancer-Decomp/build/worktrees/fla-255-scope`, Branch `codex/fla-255-goods-scope`. Gemeinsamer main-Checkout bleibt auf seinem bestehenden HEAD, mit allen lokalen Setup-Änderungen. P1/P2-Quellen, Berichte und FLA-126-Historie werden nicht neu rekonstruiert oder umgeschrieben.

Empfohlener EINZIGER nachfolgender Implementierungsmeilenstein:

**P2-Rest: vollständiger Equipment-inherit-Kopier-/Ownership-Kern einschließlich Root/Equipment/Attached-Konstruktion und -Lebenszyklus sowie realem GoodInfo-CommReferrable-Callback.**

Warum vor P3: Die aktuelle P2-Abnahme belegt vorbereitete Metadatenobjekte und einen kontrollierten inherit-Dispatcher, keine echte Kopierwirkung, Produktionskonstruktion oder file-populierte Archetype-DB. Das Original verknüpft inherit mit Root-Containerkopie, Client-Referenzmanagement, 26 Klassendispatch-Einträgen und acht geteilten/abgeleiteten Zuweisungskörpern. Nur die Klassen 8/9 zu kopieren oder den Dispatcher mit einem sichtbaren Fixture-Seiteneffekt zu ersetzen wäre keine Schließung dieser Restschuld. Der Goods-Callback ist ebenfalls nicht bloß ein beliebiger AL-Rückgabestub.

Dieses Paket schließt die konkrete Kopier-/Ownership-/Callback-Restschuld, **nicht die gesamte reale DB-/Goods-Ladekette**. Archetype::LoadEquipment mit allen tatsächlich benötigten Subtype-Readern/Factories, realer DB-Population, Ships/Hulls und der Goods-Dateilader bleiben danach offen und benötigen eigene, spätere explizite Freigabe. Es wird hier kein paralleler Implementierungsauftrag, zweiter Scopeauftrag oder vorweggenommener P3-Start erzeugt.

## 2. Originalanker und reproduzierbare Grenzen

Privater Originalpfad:
`/opt/data/projects/Freelancer-Decomp/original/_FL Fresh Install-deutsch/EXE/common.dll`

SHA256: `e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483`.
PE32/i386, bevorzugte ImageBase `0x06260000`; Hash frisch über tatsächliche Datei bestätigt. Die genauen Größen, Funktionsspans, Hashes, Callsite-VAs, direkte/indirekte Kanten und Tabellen stehen in:

- `analysis/fla255/original-evidence.json` (maschinenprüfbar);
- `analysis/fla255/original-spans.md` (vollständige VA/Span/SHA-Tabelle);
- `tools/scope_fla255.py` (selbst verfasster, lesender Evidenzsammler).

Die privaten Ghidra-Indizes sind nur Lokalisierungshilfen. Jede verwendete Instruktionsbytefolge wird gegen das gehashte Original-PE geprüft; Körpergrößen zusätzlich gegen den privaten Funktionsindex. Der Instruktionskörper kann mehrere halb-offene Spans besitzen. Paddinglücken sind ausdrücklich kein rekonstruierter Code. SHA256 der vollständigen Funktion bedeutet hier die Verkettung ihrer tatsächlichen Instruktionsspans in VA-Reihenfolge; jeder Einzelspan hat zusätzlich einen eigenen Hash. Jumptables werden separat gehasht, nicht als Code disassembliert und gezählt. Kein Modulname/Ghidra-Alias allein beweist eine Semantik.

Wichtige Originalgrenzen:

- Goods-Blockreader, bereits P1: `0x062708c0..0x062710ed`.
- GoodInfoList::load: `0x062710f0..0x062712f9` und `0x06271300..0x06271466`, Instruktionskörper 879 Bytes; RET4 bei `0x06271463`. Voller äußerer VA-Bereich enthält eine Paddinglücke.
- GoodInfoList::destroy: `0x06270740..0x062708bc`; globaler GoodList_destroy `0x06271600..0x06271709`; GoodList_load beginnt `0x06271710`.
- Equipment-inherit-Dispatcher: `0x062f3e20..0x062f4170`, 848 Bytes, cdecl mit zwei Zeigern und RET ohne Stackargumentbereinigung.
- Zugehörige 26-Einträge-Tabelle: `0x062f4170..0x062f41d8`, SHA256 `90dff599687699450e3d52b953a92721a3cc1bd8a355e288fcfd1a4b02b92d19`. Index = Klassenwert minus 8; unsigned Grenzvergleich schickt Werte außerhalb 8..33 in den Defaultarm.
- Root::operator=: `0x062f0340..0x062f054a`, 522 Bytes; SHA256 `8676ca4a39b6eeb7774df0cd02a3ac772b460d89d8aaf00801916ef3b882af2c`.
- Equipment::operator=: `0x0626ddb0..0x0626dde3`, 51 Bytes. AttachedEquipment::operator=: `0x0626e070..0x0626e0d3`, 99 Bytes. Exporte anderer Klassen können denselben Körper aliasieren; nicht mehrfach zählen.
- GoodInfo-CommReferrable-Callback: `0x0632e6a0..0x0632e71a`, 122 Bytes; SHA256 `4e81089306d646644bd84eb2e9921fec4cec9ae18f9641739af1b99a4aea1809`.
- Reale Archetype::LoadEquipment: `0x062f7bd0..0x062f7d8e` und `0x062f7d90..0x062f9362`, 6032 Instruktionsbytes; nicht durch die P2-Reader rekonstruiert.
- DataConfig::startup beginnt `0x06308d00`; seine vollständigen überprüften Spans/Kanten stehen ebenfalls im Manifest. Keine erfundene Endadresse oder pauschale Behauptung, Datei-Inventar sei ein ausgeführter Startup-Test.

DACOM.dll und DALib.dll sind als lokale importierte Module ebenfalls frisch gehasht; Namen, Größen und SHA256 im `imported_modules`-Abschnitt. Windows-System-/CRT-Module sind in dieser Original-EXE-Kopie nicht vorhanden: SHFOLDER, WINMM, ADVAPI32, GDI32, MSVCP60, MSVCRT, USER32, ole32, OLEAUT32, KERNEL32. Deshalb keine geratenen Versionen/Hashes und keine native Windows-Behauptung.

## 3. Callgraph und offene Abhängigkeiten

### 3.1 Tatsächlicher äußerer Goods-Ladepfad

DataConfig::startup `0x06308d00`
  -> sequenzielles INI-[Data]-Traversal; pro tatsächlichem Eintrag Dispatch, keine Sortierung/Dictionary-Zusammenfassung
  -> equipment: GetFileSysPath -> Archetype::LoadEquipment `0x062f7bd0`
  -> ships/solar: jeweils eigene Archetype-Lader
  -> goods: GoodList_load `0x06271710`
       -> GoodInfoList::load `0x062710f0`
            -> GetFileSysPath `0x06302db0` mit IFileSystem/Data-Bindung
            -> INI_Reader ctor/open/read_header/is_header
            -> für [Good]: new(0xc0) -> GoodInfo ctor `0x062701e0`
            -> P1 read_Good_block `0x062708c0`
            -> Listenappend `0x0627f640`
            -> Indexpopulation `0x063221d0` und `0x0626b770` für beide Indexstrukturen
            -> Close/Reader-/FileMap-/String-/OS-Cleanup und CRT/SEH

Der Lader liefert void, kein erfundener bool-Erfolgsvertrag. [GoodType] hat einen eigenen Diagnostikpfad; unbekannte Header werden nicht pauschal als [Good] geladen. Allocation-Nullpfade und noch folgende ungeschützte Zugriffe sind aus Originalbytes zu erhalten, nicht als freundliche Fehlermeldung umzudeuten. Der P1-Duplikat-Return beweist allein weder Listen-/Index-Duplikatpolitik noch Objektfreigabe des äußeren Laders: dieser fährt anschließend mit Append/Indexarbeiten fort.

Die Basiskomponenten INI/FileMap, Hash, Cache, GoodInfo-Initialisierung/-Zerstörung, Listen-/Indexmechanik und P1-Blockreader existieren bereits als storage-level Rekonstruktionen mit expliziten Dienstgrenzen. Das ist nicht dasselbe wie ihre echte vollständige Bindung an den äußeren Dateilader und eine reale Archetype-DB.

### 3.2 P2-inherit-Kopierpfad

Equipment::read `0x062f41e0`
  -> CreateID(whole-string)
  -> ArchDB-Query `0x063015d0`, Equipment-DB-Anker `0x063fbad4` / Sentinel `0x063fbad8`
  -> fehlender Knoten vs null Payload: getrennte Diagnostikpfade
  -> gültige Payload: Dispatcher `0x062f3e20`
       -> target/source class getter, jeweils vtable+0x10
       -> bei Klassenungleichheit früher Return
       -> Client-/Nickname-Sicherung und Client-Callbacks
       -> vollständiger 26-Wege-Klassendispatch, acht subtype assignment bodies und ggf. Vektorkopie
       -> Root::operator= einschließlich tatsächlicher Containerkopie/Teardown
       -> Zielnickname/Zielclient-Wiederherstellung mit korrekten Client-Referenzereignissen

Die acht zu rekonstruierenden Assignment-Einstiege sind `0x0626ddb0`, `0x0626e070`, `0x0626eaf0`, `0x0626dbb0`, `0x0626e2c0`, `0x0626f660`, `0x0626f870`, `0x0626fa10`. Sie und die Vektorkopie `0x062fb660`, Root-Kopie/-Zuweisung und die aufgelösten direkten Containerhelfer sind exakt im Manifest erfasst. Die direkte Kernel-Abhängigkeitsmenge wird reproduzierbar aus dem privaten Callindex bestimmt und byteverifiziert. Bereits rekonstruierte String-/ID-/INI-Dienste und CRT bleiben explizite Blätter. Indirekte Client-/Factory-/Runtime-Kanten sind **keine automatisch geschlossene dynamische Abhängigkeit**; ihre Original-Slotverträge bleiben im Scope sichtbar.

Beispiele tatsächlich notwendiger Root-Containerhelfer: `0x062fc530`, `0x062fd350`, `0x06319960`, `0x062fc150`, `0x06319400`, `0x06280e50`, `0x062fd090`, `0x062fd110`. Nur leere Container zu testen oder all diese Körper mit einem fertigen Fixture-Ergebnis zu ersetzen erfüllt den vorgeschlagenen Meilenstein nicht. Gefüllte Container, unterschiedliche Quell-/Ziellängen, unabhängige Ownership und echte Kopier-/Freigabepfade sind verpflichtend.

### 3.3 GoodInfo-Callback

GoodInfo vtable `0x063993e8..0x063993f4` ist eine drei-Slot-CommReferrable-Bindung:
  +0 -> `0x0632e690`
  +4 -> `0x062bd490`
  +8 -> `0x0632e6a0` (read_comm_ini_data)

Der danach im Datenbereich liegende DWORD ist **kein vierter Callbackslot**. Der reale Slot+8 erkennt msg_id_prefix und benutzt INI is_value/whole-string. Null leert Länge und erstes Zeichen; sonst scannt er bis zum vollständigen NUL, begrenzt erst danach auf 63 Zeichen, kopiert und terminiert. Er schreibt Länge an +4 und String an +8. Unbekannter Schlüssel gibt AL=0 zurück; bekannter AL=1. Ein unterminierter Quellstring kann beim vollständigen Scan faulten. Die bisher kontrollierten virtuellen P1-Callbacks schließen diesen Originalkörper nicht.

## 4. Layout, vtable, ABI, Ownership und x87

### Layout und Defaultkonstruktion

Root: Größe `0x5c`. vptr+0, client+4, nickname+8, DA/attachment CacheString+0x0c, type+0x10, ids_name+0x14, ids_info+0x18, hit_pts+0x1c, mass+0x20, explosion ID+0x24, resistance+0x28, inertia[3]+0x2c/+0x30/+0x34, presence+0x38, phantom byte+0x39. Bisher als opaque betrachteter Bereich enthält zusätzlich +0x3c, Indizes +0x40/+0x44 und den originalen Container an +0x48 mit head+0x4c, nil+0x50, Zustand+0x54 und count+0x58.

Original Root-Konstruktor `0x062eff70` allokiert zwei getrennte 0x44-Byte-Head/Nil-Speicher. Hitpointsbits `0x42c80000`; mass/resistance `0x3f800000`; engine/script-Indizes -1. Die Container-Allocatorbytes +0x48/+0x49 stammen in diesem Körper aus dem niederwertigen Byte des übergebenen Clientarguments, **nicht aus einer geratenen konstanten Null oder der GoodInfo-ESP-17-Grenze**. Padding und ungeschriebene Speicher bleiben erhalten.

Equipment: Größe `0x70`, volume+0x5c, raw use_count+0x60, units+0x64, tractored_explosion+0x68, raw lootable+0x6c. Original Konstruktor überschreibt hit_pts mit `0x3f800000`, setzt use_count/lootable=1 und units=1. AttachedEquipment: Größe `0x88`, separation/debris IDs+0x70/+0x74, impulses+0x78/+0x7c, HP_child CacheString+0x80, toughness+0x84.

GoodInfo: bereits rekonstruierte storage extent `0xc0`. CommReferrable-Präfix+4/+8 bis vor nickname+0x48; category+0x4c; Archetype+0x50. Drei Addonlisten mit head/count +0x98/+0x9c, +0xa4/+0xa8, +0xb0/+0xb4. GoodInfoList: 52 Byte Speicher; Hauptliste +4/+8, zwei 20-Byte-Indexstrukturen +0x0c und +0x20. Vollständige native C++-Klassen-/Runtime-Integration weiterhin nicht bewiesen.

### Vtables und calling conventions

Root original vtable `0x063a11c0`; Equipment `0x06399860`; Attached `0x06399af4`. Original Slots umfassen deleting destructor+0, read+4, redefine+8, load+0x0c, class getter+0x10, free_resources+0x14; Equipment/Attached zusätzlich is_attached+0x24. Vorliegende rekonstruierte Tabellen sind ausdrücklich **partielle Tabellen** mit Nullslots, kein vollständiges polymorphes Objektmodell. Das nächste Paket darf ausschließlich von ihm wirklich rekonstruierte Slots als funktionierend publizieren; load/redefine/engine physical-resource paths sind trotz gehashter Originalanker nicht automatisch implementiert.

Konstruktion/Kopie/Zuweisung/Reader sind überwiegend thiscall, ECX=this, ein Stackargument und RET4; nicht aus dem Namen, sondern aus den Originalret-Stellen prüfen. P1-Blockreader: ECX=Liste, Reader/Good auf Stack, RET8. Dispatcher `0x062f3e20`: cdecl(target, source), Caller bereinigt Argumente. Destruktor ohne Argument RET, deleting Varianten benötigen flag-/array-cookie-spezifische Prüfung. EBX/ESI/EDI/EBP, ESP, Rückgabepointer/AL, sämtliche Guard-/Paddingbytes gehören zur Abnahme.

### Ownership und Floating point

Root-Zuweisung führt Client Release vor Installation/AddRef des Quellclients aus. Der inherit-Dispatcher kompensiert dies, um Zielclient und Zielnickname zu behalten. Ein schneller self==source-Return, umsortierte Clientereignisse oder eine sizeof-Memcpy ändern den Vertrag. Containerhead/nil/nodes gehören den einzelnen Objekten; CacheString/ID/pointer-elements können dagegen gemäß Original aliasieren. Destruktion gibt Client und die tatsächlich eigenen Containerressourcen in Originalreihenfolge frei. Deleting Varianten sind nicht einfach free(this); Array-Cookies/CRT sind eine explizite Grenze.

Published P1/P2 benutzen x87-Getter ST0 und unmittelbaren FSTP binary32. Neue Kopierkörper kopieren rohe DWORD-/Bytefelder und dürfen keine zusätzlichen float/double-Konversionen oder NaN-Normalisierung einführen. x87 CW/SW/tag/live binary80 und bereits belegte Double-Rounding-Discriminators bleiben Regressionen. Native unmaskierte x87-Ausnahmen und native CRT/SEH sind noch nicht ausgeführt; Emulator-NaN-Verhalten ist kein Hardwarebeweis.

## 5. Reale lokale Korpora, ohne Inhaltsupload

`analysis/fla255/corpus-inventory.json` enthält ausschließlich aktive relevante Dateipfade, SHA256, Größen, Formate, Header-/inherit-Zahlen und Original-Konfigurationsreihenfolge. Keine Nutzwerte, vollständigen INIs, Nickname-/Spielstandlisten, Archive oder Roh-Decomp-Dumps. Dateiinhalt wird zum Inventarisieren lokal gelesen, nicht veröffentlicht.

Original-Deutschkopie unter `original/_FL Fresh Install-deutsch`: relevante Dateien sind BINI-v1. HD-Referenz `/opt/data/projects/Freelancer/Installations/Freelancer-HD`: entsprechende Dateien sind TEXT. Jede Konfiguration referenziert 15 relevante Dateien; alle vorhanden. Je Corpus sieben equipment-, zwei ships-, eine solar- und fünf goods-Dateien. Die fünf goods-Dateien umfassen 855 [Good]-Header; engine_good ist im Original ein echter 12-Byte-BINI-Leercontainer, kein fehlender Testinput. light_equip enthält 58 inherit-Einträge – dieser reale Corpus zeigt unmittelbar, dass inherit nicht optional wegdefiniert werden darf.

Relevante Reihenfolge je Konfiguration:
solararch; light_equip; select_equip; misc_equip; engine_equip; ST_equip; weapon_equip; prop_equip; shiparch; rtc_shiparch; goods; engine_good; misc_good; st_good; weapon_good. Nichtrelevante [Data]-Einträge dazwischen sind nicht wegzudenken: das Inventar nummeriert nur diesen gefilterten Ausschnitt, keine vollständige Startup-Ereignisliste. Die tatsächliche Startup-Schleife wird aus dem Original an `0x06308d00` abgeleitet; sie ist hier statisch analysiert, nicht ausgeführt.

HD ist ein Modcorpus und kein automatisch identisches Modul-/Native-Oracle. Für beide Korpora sind konkrete Dateihashes fixiert; entsprechende BINI/TEXT-Daten dürfen nicht als verschiedene vollständige Loaderdurchläufe gezählt werden. **Tatsächlich ausgeführte reale Original-/Rekonstruktions-DB-/Loaderfälle auf diesem Auftrag: 0.**

Zusätzlicher gewünschter Originaldatenstand auf nasa-cachy: `/mnt/ai-models/PROJECTS/TASKS/Freelancer-Decomp`. SSH-Verbindungsprobe auf Port22 scheiterte mit Timeout/Exit255; dessen aktueller Bestand wurde daher nicht geprüft. Die benötigte common.dll mit passendem Hash, private lokale Funktions-/Instruktionsindizes und lokale Korpora sind auf hermes-srv vorhanden, sodass die belegte lokale Originalanalyse nicht auf erfundenen Remote-Ergebnissen beruht. Fehlender Remote-Livezugriff wird nicht als vollständige Remote-Datenprüfung ausgegeben.

## 6. Bereits rekonstruiert, nächstes Paket und ausdrücklich offen

| Baustein | Stand an fester Basis | Scopeentscheidung |
|---|---|---|
| P1 Goods Block-/Preisreader | Rekonstruiert und veröffentlicht; Dienstgrenzen dokumentiert | Wiederverwenden, vollständige Regression; kein Neuaufbau |
| P2 Root/Equipment/Attached Reader und is_attached | Rekonstruiert/veröffentlicht, vorbereitete Speicher und kontrolliertes inherit | Wiederverwenden, echte neue Kopierkörper verbinden |
| Hash/Cache/ID/Lookup/INI/FileMap/GoodInfo storage lifetime/Index | Vorhandene rekonstruierte Körper mit jeweiligen offenen Native-/Binding-Grenzen | Reale Körper wiederverwenden; Fixture nicht als DB ausgeben |
| Root/Equipment/Attached Konstruktion/Kopie, gefüllte Root-Container, komplettes inherit | Offen; Originalstruktur jetzt abgegrenzt/gehasht | EIN nächster P2-Restmeilenstein |
| GoodInfo slot8 CommReferrable-Reader | Offen, Originalkörper jetzt bestimmt | Im selben kleinen Abhängigkeitskern rekonstruieren und real binden |
| Reale Archetype::LoadEquipment/Subtype DB/Factory/Ships/Hulls | Offen; Originallader gehasht, Corpusabhängigkeiten sichtbar | Späterer eigener freigegebener Meilenstein; kein Produktions-DB-Claim |
| Voller Goods-Dateilader, globales Free/Reload, echte Corpusfälle | Offen | P3 erst mit realen benötigten Archetype-Referenzen und separater expliziter Freigabe |
| Native Windows/CRT, beliebig korrupte Container, unmaskierte x87, Gesamtspiel | Offen | Separat ausweisen, keine implizite Abnahme |

## 7. Abnahmematrix und negative Kontrollen

Die vollständige maschinenprüfbare Matrix steht in `analysis/fla255/acceptance-matrix.json`. Jede Zeile legt Fixture, Original-Oracle, Rekonstruktions-Oracle, ABI-Prüfung, unabhängig zu fixierende Erwartung und kompilierte Defektkontrolle fest. **Alle Spiel-/Implementierungsfälle haben status=planned_not_executed.**

N01–N15 sind verbindliche Abnahme des nächsten Kopier-/Ownership-/Callback-Kerns: Defaultkonstruktion; gefüllte Container; self/alias/client order; alle 26 Dispatcherarme und Klassenmismatch; tatsächliche Reader-inherit-Verbindung; subtype-owned vectors; realer Callback einschließlich voller Stringscan-Faults; Destruktor-/deleting Varianten; wiederholter Lebenszyklus; x87/ABI/Failure-Grenzen; unveränderte komplette P1/P2-/Lookup-Regressionssuiten. Ein reiner leerer Container-Smoke oder kontrollierter Dispatcher erfüllt den Scope nicht.

P01–P08 planen ausdrücklich spätere echte DB/Loader-, Ladefolge-, Duplikat-, Defaults-/Metadata-, fehlende Referenz-, Fehlerpfad-, Free/Reload- und malformed-Sentinel-Abnahmen. Wo Loaderzustände noch nicht dynamisch ermittelt sind, verlangt die Zeile zuerst eine feste Original-Ereignis-/Ownership-Erwartung, bevor implementiert wird; sie gibt keine unbeobachtete Duplikat-/Rollbackpolitik als Fakt aus. W01 ist native Windows/CRT, offen.

Athena leitet vor einem künftigen Implementierungsreview eigene Erwartungen und Discriminators aus den Originalbytes ab, statt Implementiererausgaben als Oracle zu verwenden. Je Test: unterschiedliche Speicher-/Heap-Seeds, vollständige Byte-/Eventvergleichbarkeit, Original-/Rekonstruktionsimages getrennt, auf neuer Seite sämtliche neu beanspruchten Originalspans gesperrt. Kompilierte Negativvarianten müssen konkrete Discriminators treffen; erfolgreiche Paarfälle, Faultpaare, Destruktor-/ABI-Returns, dienstmodellierte Grenzen und native Runs getrennt zählen. Keine geplante Prüfung als gelaufen markieren.

Bekannte P1-malformed-Lücke: `0x06270e80`, `0x06270ef5`, `0x06270f51` waren in der veröffentlichten normalen Suite nicht ausgeführt. Dieser Scope verändert P1 nicht und behauptet nicht, die Lücke geschlossen zu haben. Ein P3-Plan muss gezielte neue Fault-/Zustandsproben anlegen; auch deren Bestehen wäre nicht universelle Korruptionssicherheit.

## 8. Tatsächlich ausgeführte Scope-Prüfungen und Ausführungsgrenzen

Frische Befehle/Exitcodes/Resultate und Hilfs-/Quellhashes werden in `analysis/fla255/scope-verification.json` und `source-hashes.json` gespeichert. Dieser Auftrag führt den lesenden Original-/Corpus-Evidenzsammler, dessen Metadaten-/Format-Unitchecks, Reproduzierbarkeit, Quellen-/Dateierhalt und Git-Scope-Prüfungen tatsächlich aus. Er kompiliert/implementiert keine neuen Spielkörper und startet keine P1/P2-Abnahmesuiten. Bestehende veröffentlichte P1/P2-Testergebnisse sind Provenienz aus bf555cdc, keine frischen Tests dieses Scopelaufs.

Ergebnis der endgültigen frischen Scopeprüfung: 80 Originalfunktionskörper, 8347 gegen das PE geprüfte Instruktionen und fünf separat gehashte Tabellen; 38 Körper im indizierten direkten Kernel-Abhängigkeitsabschluss. Zweiter unabhängiger Sammellauf erzeugte Original-/Corpus-Metadaten byteidentisch. Zehn Scope-/Inventar-Unitchecks bestanden; `git diff --check` Exit0. Alle 390 an bf555cdc vorhandenen versionierten Dateien waren byteidentisch, ebenso gemeinsamer HEAD/Index/Status und sechs lokale Setup-Dateien. Die 24 Spiel-Abnahmefälle (15 nächstes Paket, acht spätere P3-Fälle, ein Native-Fall) sind ausdrücklich nur geplant; reale DB-/Loaderfälle und native Läufe bleiben null.

Erste Hilfsdiagnostik scheiterte: capstone ist in der Projektumgebung nicht installiert. Alternative: vorhandenes pefile, private Indizes plus Originalbyteprüfung und GNU objdump, ohne Installation. Erste Sammlerprobe schlug an nicht zugeordneten decoded orphan instructions fehl; zweite Erweiterungsprobe an einem EXTERNAL-Callindexeintrag. Beide wurden als Hilfsparserfehler korrigiert, nicht als bestandene Spieltests gezählt. Die endgültige Sammler-/Scopeprüfversion wird mit echten Exitcodes protokolliert.

Vault-pull --rebase scheiterte an fehlender HTTPS-Authentifizierung (Exit1). Lokale Home-/Freelancer-Wikilinks wurden gelesen; kein erfolgreicher Vaultsync behauptet. DailyTasks `/api/v1/context` und `/api/v1/openapi.json` wurden gelesen; vollständige [Paperclip]-Titelsuche hatte keine zugehörige Aufgabe. DailyTasks-Aufgaben-ID: **keine**; keine Mutation/Erledigung oder Ersatzaufgabe. Eine später ausdrücklich freigegebene passende Aufgabe wäre vor Mutation frisch zu lesen, Notizen zu erhalten und zur Prüfung auf wartend zu setzen; erledigt erst nach Steven.

## 9. Dateierhalt, Schutz und Übergabegates

Vorlauf `fa6c7895-a6d7-4b20-bdef-0d681c1761ad`: API succeeded, Ende 14.10.2026 12:43:32.420 UTC. Gemeldeter Elternlauf `907d88ab-d965-485b-a9ee-d0ab2fe11d93`: API succeeded, Ende 12:45:17.748 UTC. Beide vor Worktree-Mutation beendet. Unter lesbaren /proc-FDs keine Projektdatei schreibend geöffnet; 394 Prozess-FD-Verzeichnisse nicht lesbar, daher kein behaupteter systemweiter Exklusivitätsbeweis. Koordination über festen Commit und isolierte Schreibpfade.

Hauptcheckout-HEAD `05a983b19d9a83363bf41d6657ae4eb10d0268c8`, Index, vollständiger Status und alle sechs Setup-Arbeitsdateien wurden vor Mutation gesichert/gehasht und bleiben erhalten; Vor-/Nachprüfung steht im Verificationbeleg. Weder fremde Setup-Dateien noch Original-/Rawverzeichnisse werden gestaged. Scope-Branch-Publikation ist keine main-Pushfreigabe.

Livequote bei frischen Vorproben 39% Wochenrest, strikt >30. Tatsächlicher Elternlauncher `/opt/data/paperclip-guards/freelancer_quota.py` wurde anhand /proc bestätigt; geschützter Start und INTERVAL=60. Für **jede** Folgezuweisung, einschließlich Athena/Apollo: Projektpfad `/opt/data/projects/Freelancer-Decomp`; nur bei bekannt strikt MEHR ALS 30% Codex-Wochenrest arbeiten/delegieren; geschützter Start und 60-Sekunden-Wächter zwingend. <=30% oder unbekannt: stoppen und Dateien erhalten; keine Credits/Resets. Reviewer prüfen frisch selbst.

Nächster Owner auf DIESEM Issue: Athena prüft den festen Scope-Commit und die feste native Scope-Dokumentrevision read-only in eigener Kopie, mit Referenz bf555cdc und privaten Originaldaten. Befunde und native Reviewentscheidung auf FLA-255 veröffentlichen. Danach Apollo native Scope-Abnahme derselben Revision. Kein parallel angelegter Review-/Scopeauftrag. **Selbst positive Scopeabnahme ist noch keine Implementierungs- oder main-Freigabe**: der vorgeschlagene exakt eine Folge-Meilenstein darf erst nach separater expliziter Zuweisung/Freigabe starten. Hermes alleiniger Integrator; kein main-Push, Amend oder Force-Push in diesem Auftrag.
