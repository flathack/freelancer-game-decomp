# Freelancer (2003) – Decompilierung

Stand: **13.10.2026**. Ziel ist rekonstruierter, überprüfter Quellcode des vollständigen Spiels.

| Fortschritt | Stand |
|---|---|
| Roh-Decompilierung | **34/34 Code-Module**, 54.832 erkannte Funktionen ausgegeben |
| Kompilierbarer, verhaltensgeprüfter Code | Teilbereiche: INI-Reader (39 Exporte), FileMap, IDs, String-Cache, EquipDesc und Teile von Loadout |
| Byteidentische Treffer im Dashboard | **21 von 8.021.343 Code-Bytes ≈ 0,00026 %** |
| Vollständig rekonstruiertes, spielbares Spiel | **Noch nicht erreicht** |

Die Roh-Ausgaben sind kein fertiger Quellcode. Für die gesamte verhaltensgeprüfte Rekonstruktion gibt es noch keinen belastbaren Prozentwert. Zusätzlich ist der 3-Byte-No-op `INI_Reader::log_link` separat byteidentisch bestätigt.

Zuletzt: Goods-Suche auf befüllten Indizes mit **96.000 Vergleichen** geprüft, nach 8.000 Original-/Rekonstruktions-Einfügungen. Der Loadout-Dateilader besteht die vier Originaldateien (803 Maps / 17.130 Einträge). Vollständiges Goods-Laden und native Windows-Ausführung bleiben offen.

- [Detaillierter Fortschritt](analysis/progress.md)
- [Rekonstruktionsnotizen](docs/reconstruction-notes.md)
- [decomp.dev-Anbindung und Messumfang](docs/decomp-dev.md)

Codex-Decompilierung pausiert; Übergabe an Paperclip auf `hermes-srv`. [Übergabe und nächste Schritte](docs/PAPERCLIP-HANDOFF.md). Nach jedem Fortschritt committen und auf `origin/main` pushen.
