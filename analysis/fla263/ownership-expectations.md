# FLA-263 – vor Implementierung fixierte Originalerwartungen

Grundlage unverändert analysis/fla255/original-evidence.json und original-spans.md,
Scope c93583dcdca63e257d9a18dd9d51aa62905f5042. Original-common.dll frisch
SHA256 e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483.
Dies sind selbst formulierte Semantik-/Testvorgaben, keine Raw-Ausgaben.

Root-Zuweisung 062f0340: zuerst bisheriger Client Slot4, dann Source-Client
installieren und Slot0. Auch self und gleiche Clientpointer erzeugen diese
Ereignisse. Danach Container neu aufbauen, außer bei identischer Containeradresse.
Allocatorbyte49 wird übernommen, Byte48 bleibt Ziel-eigen. Head/nil bleiben
eigenständig; alte Nodes samt Payload-Vektoren werden zerstört. Neue Nodes werden
wurzel-links-rechts allokiert, Farben/Schlüssel/Payloadfelder kopiert, Padding nicht.
Payload kopiert DWORD+0, Byte+4, DWORD+8, sechs DWORD+0xc..+0x20,
Byte+0x24 und einen separat allokierten Pointervektor+0x28/+0x2c/+0x30.
Der externe Payloadhandle+8 aliasiert entsprechend Original, seine Zerstörung
benutzt die Headeradresse an handle-4. Kein erfundenes Deep-Copy dieses Handles.
Die Baumfreigabe läuft rechte Teilbäume vor linkem Abstieg und aktuellem Payload.
Die unabhängigen ursprünglichen Object-/Heapbytes sind vollständig zu vergleichen.

Root-Metadatenwritefolge nach Container: 08,0c,10,14,18,1c,20 DWORD;
39 Byte; 24,28,2c,30,34 DWORD; 38 Byte; 3c,40,44 DWORD. vptr bleibt unverändert.
Equipment ergänzt 5c DWORD,60 Byte,64/68 DWORD,6c Byte.
Attached ergänzt 70/74/78/7c/80/84 DWORD.

Default Root 062eff70: client04, ID08=0, cache0c=empty-cache;
10/14/18=0,1c=42c80000,20=3f800000,24=0,28=3f800000;
2c/30/34=0,38/39=0,3c=0,40/44=ffffffff. 48/49=client low byte,
54=0. Nil zuerst 44 Bytes, dann eigener Head 44 Bytes; kein Client-AddRef.
Nil: left/parent/right=0,color40=1,nil41=1; Head: left/right=self,
parent=nil,color40=0,nil41=0. Count58=0. vptr wird erst danach gesetzt.
Root-Kopierkonstruktor 062f0170 allokiert leeren Container, Allocator48/49
stammen aus Lowbyte des Sourcearguments. Wichtig: bisheriges client04 im
Destination wird vor Root::operator= NICHT auf Null gesetzt. Testseed dort
muss einen definierten validen/null Client enthalten; ungeprüfte uninitialisierte
Pointer sind keine neue Safe-Null-Garantie.
Equipment default setzt volume0,use_count1,units1,tractoredID0,lootable1,
Equipment-vptr,hitpoints3f800000. Attached ergänzt IDs70/74=0,
impulses78/7c=0,cache80=empty,toughness84=0,Attached-vptr.
Root-/Equipment-/Attached-Kopie muss beobachtbare Zwischen-vptrs erhalten.

Dispatcher 062f3e20: cdecl(target,source). Classgetter target vor source,
bei Mismatch keinerlei weitere Wirkung. Bei Match targetclient Slot0, dann
Slot1c(sourceclient), sofern Targetclient vorhanden. Nickname erst danach sichern.
Dispatchzuordnung nach der separat gehashten 26er-Tabelle:
8 Equipment; 9 Attached; 10 Equipment+70/74/78; 11 Equipment+70/74/78/7c;
12 Equipment+70/74/78/7c/80 DWORD,84 Byte,88 DWORD; 13 Attached;
14 Attached+88..a4 DWORD und echter Vektor+a8;
15 Attached+88/8c; 16 Attached+88..9c;
17 Equipment+70..9c DWORD, a0/a4/a8/ac/b0/b4 DWORD,
b8/b9/ba Byte, echter Vektor+bc,cc Byte,d0 DWORD;
18 Equipment+70..9c DWORD; 19 wie18 plusa0;
20 wie10; 21 Equipment+70/71 Byte; 22 Equipment+70/74 DWORD;
23 Equipment;24/25/26/27 Equipment+70 DWORD;
28 Equipment+70..98 DWORD;29 Equipment;30 keine Assignmentwirkung;
31 Equipment+70/74 DWORD,78/79 Byte,7c..a8 DWORD,ac Byte;
32 Equipment+70/74 DWORD,78/79 Byte,7c..90 DWORD;
33 Equipment+70/74 DWORD,78/79 Byte,7c..88 DWORD.
Auch Klassen außerhalb8..33 durchlaufen Match-Clientprolog/-epilog ohne Assignment.
Danach gespeicherten Nickname restaurieren, aktuellen Client Slot4,
erst dann gespeicherten Targetclient installieren. Kein nachträgliches AddRef.

Vektor 062fb660: self bleibt unverändert. Byte0/Padding bleiben Ziel-eigen.
Wenn Sourcegröße<=Zielgröße: vorhandene Elemente überschreiben, Endpointer verkürzen.
Wenn Sourcegröße<=Zielkapazität: überschreiben, Rest fieldwise konstruieren.
Sonst zuerst alte Allocation freigeben, exakt Sourcegröße neu allokieren,
Element-DWORDs kopieren, end=capacity setzen. Pointerelemente bleiben flach,
Owned-Buffer nicht. Null-Allocator in Construction-Schleifen wird nur beim
jeweils aktuellen Zielpointer übersprungen, Pointer trotzdem erhöht; keine
erfundene durchgehende OOM-Behandlung.

Destruktor setzt Root-vptr, Client Slot4, Containerpayloads/Nodes, dann Head,
dann Nil; Containerhead/nil/count werden auf0 gesetzt. Keine Cachefreigabe.
Deleting flags lowbyte: Bit2 bedeutet Cookie=this-4,count am Cookie,
CRT-Arraydestruktor mit Stride5c/70/88 und Root-/gemeinsamem Base-Destruktor.
Bit1 gibt skalaren Pointer bzw Cookie frei; Return entspricht diesem Pointer.
CRT/SEH bleiben explizite modellierte Dienste, kein Nativeclaim.

N07-Classgetter-Zusatz, frisch vor Korrektur am Original überprüft:
Root Slot10 -> 06325240 liefert0; Equipment 0626d520 liefert6;
Attached 0626dff0 liefert7. Die Dispatcherarme8/9 sind NICHT die Basistypen.
Basistyp-Inherit mit identischer Klasse6/7 durchläuft nur Clientprolog/-epilog,
keine Assignmentwirkung. Zusätzliche Subtyp-Classgetter8/9 als expliziter
Kontrolldienst erlauben den echten Assignmentkörper zu erreichen. Keine
Umdeutung von6/7 auf8/9, um einen Kopierclaim zu erzwingen.

N07-Query-Zusatz, aus frischem Originalspan 063015d0..0630163a vor
Implementierung: unsigned Lower-Bound über links/parent/rechts/key, Beginn
head->parent, Abbruch am eigenen nil. Bei keinem exakten Schlüssel head
zurückgeben (einschließlich Kandidat mit größerem Schlüssel), sonst Kandidat.
Der Query schreibt nur seinen Ausgabeparameter, niemals die Eingabebaumknoten.
Test mit 0/80000000/ffffffff, fehlend/Nullpayload/valid und echten Readerpfaden;
neue Seite darf 063015d0 nicht als kontrollierten Queryersatz ausführen.

Diese Erwartungen sind noch keine bestandenen N01–N15-Tests. Der
Gesamtmeilenstein bleibt offen, solange eine Pflichtzeile nicht belegt ist.
