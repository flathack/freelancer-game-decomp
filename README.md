# Freelancer (2003) – Decompilierung

Stand: **14.10.2026**. Ziel ist rekonstruierter, überprüfter Quellcode des vollständigen Spiels.

| Fortschritt | Stand |
|---|---|
| Roh-Decompilierung | **34/34 Code-Module**, 54.832 erkannte Funktionen ausgegeben |
| Kompilierbarer, verhaltensgeprüfter Code | Teilbereiche: INI-Reader (39 Exporte), FileMap, IDs, String-Cache, EquipDesc und Teile von Loadout |
| Byteidentische Treffer im Dashboard | **21 von 8.021.343 Code-Bytes ≈ 0,00026 %** |
| Vollständig rekonstruiertes, spielbares Spiel | **Noch nicht erreicht** |

Die Roh-Ausgaben sind kein fertiger Quellcode. Für die gesamte verhaltensgeprüfte Rekonstruktion gibt es noch keinen belastbaren Prozentwert. Zusätzlich ist der 3-Byte-No-op `INI_Reader::log_link` separat byteidentisch bestätigt.

Zuletzt: Der **P1 Goods-Blockreader** ist nach Athena-Review und Apollo-Freigabe unverändert integriert. Der bereits geprüfte Nachweis umfasst **6.696 Original/Rekonstruktionspaare**, je 13.296 ABI-/Destruktoraufrufe (beide Seiten zusammen), sechs erkannte Defektvarianten und 48 separat gezählte Originalfaults. Das sind frühere Abnahmenachweise, keine neuen Integrationstests. Kontrollierte Dienste ersetzen Reader/Hash/Cache/Index/Archetype-Abhängigkeiten; drei malformed-Sentinel-Pfade bleiben ungeprüft. Kein realer Goods-Korpus, vollständiger Dateilader oder nativer Windows/CRT-Nachweis. [Umfang und Grenzen](analysis/good-blockreader-notes.md). Preiszweige, Goods-Indexsuche und Loadout-Dateilader behalten ihre bisherigen Nachweise; Archetype-Datenbank und das Gesamtspiel bleiben offen. P2 bleibt bis zur Prüfung der Veröffentlichung durch Athena und Apollo inaktiv.

- [Detaillierter Fortschritt](analysis/progress.md)
- [Rekonstruktionsnotizen](docs/reconstruction-notes.md)
- [decomp.dev-Anbindung und Messumfang](docs/decomp-dev.md)

Codex-Decompilierung pausiert; Übergabe an Paperclip auf `hermes-srv`. [Übergabe und nächste Schritte](docs/PAPERCLIP-HANDOFF.md). Nach jedem Fortschritt committen und auf `origin/main` pushen. Für sämtliche Freelancer-Arbeit gilt die [Quotengrenze](docs/PAPERCLIP-QUOTA.md): nur bei nachweislich mehr als 30 % verbleibendem Codex-Wochenlimit, sonst stoppen.
