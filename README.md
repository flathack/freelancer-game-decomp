# Freelancer (2003) – Decompilierung

Stand: **13.10.2026**. Ziel ist rekonstruierter, überprüfter Quellcode des vollständigen Spiels.

| Fortschritt | Stand |
|---|---|
| Roh-Decompilierung | **34/34 Code-Module**, 54.832 erkannte Funktionen ausgegeben |
| Kompilierbarer, verhaltensgeprüfter Code | Teilbereiche: INI-Reader (39 Exporte), FileMap, IDs, String-Cache, EquipDesc und Teile von Loadout |
| Byteidentische Treffer im Dashboard | **14 von 8.021.343 Code-Bytes ≈ 0,00017 %** |
| Vollständig rekonstruiertes, spielbares Spiel | **Noch nicht erreicht** |

Die Roh-Ausgaben sind kein fertiger Quellcode. Für die gesamte verhaltensgeprüfte Rekonstruktion gibt es noch keinen belastbaren Prozentwert. Zusätzlich ist der 3-Byte-No-op `INI_Reader::log_link` separat byteidentisch bestätigt.

Zuletzt: Loadout-ID-Suche mit **28.354 Vergleichen** geprüft. Reader, Loadout-Parser und echte rekonstruierte ID-Erzeugung bestehen Vergleiche über **17.130 Einträge** aus allen vier mitgelieferten Loadout-Dateien. Native Windows-Ausführung bleibt offen.

- [Detaillierter Fortschritt](analysis/progress.md)
- [Rekonstruktionsnotizen](docs/reconstruction-notes.md)
- [decomp.dev-Anbindung und Messumfang](docs/decomp-dev.md)

Nach jedem Fortschritt wird committed und auf `origin/main` gepusht.
