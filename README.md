# Freelancer (2003) – Decompilierung

Stand: **14.10.2026**. Ziel ist rekonstruierter, überprüfter Quellcode des vollständigen Spiels.

| Fortschritt | Stand |
|---|---|
| Roh-Decompilierung | **34/34 Code-Module**, 54.832 erkannte Funktionen ausgegeben |
| Kompilierbarer, verhaltensgeprüfter Code | Teilbereiche: INI-Reader (39 Exporte), FileMap, IDs, String-Cache, EquipDesc, Teile von Loadout und P2 Archetype-Metadatenreader |
| Byteidentische Treffer im Dashboard | **21 von 8.021.343 Code-Bytes ≈ 0,00026 %** |
| Vollständig rekonstruiertes, spielbares Spiel | **Noch nicht erreicht** |

Die Roh-Ausgaben sind kein fertiger Quellcode. Für die gesamte verhaltensgeprüfte Rekonstruktion gibt es noch keinen belastbaren Prozentwert. Zusätzlich ist der 3-Byte-No-op `INI_Reader::log_link` separat byteidentisch bestätigt.

Zuletzt: Die **P2 Archetype-Metadatenreader** (Root/Equipment/AttachedEquipment und is_attached-Bindung) sind aus dem von Athena geprüften und von Apollo freigegebenen Candidate `cafce1406d75785e9069f2dcb5102c732701e8f8` ohne Quell-/Teständerung integriert. Frische Integrationsregression: **6.506 Readerpaare / 13.012 unabhängige Oracles**, zehn erkannte kompilierte Defektkategorien, gekoppelte Suite sowie vollständige unveränderte P1-/Lookup-Suiten. Athenas zusätzliche 104 Grenzpaare sind wiederverwendete Reviewevidenz, keine neuen Integrationstests. Reale DB-/Loaderfälle: **0**. inherit-Kopierkörper, native Windows/CRT, GoodInfo-Callback, malformed-Sentinel und Gesamtspiel bleiben offen. [Integrationsbericht und Grenzen](analysis/archetype-metadata-integration.md). Die separate Publikationsprüfung durch Athena und Apollo steht noch aus; kein nächster Meilenstein vor deren Abschluss. P1-, Preis-, Index- und Loadout-Nachweise sowie die bisherige Historie bleiben erhalten.

- [Detaillierter Fortschritt](analysis/progress.md)
- [Rekonstruktionsnotizen](docs/reconstruction-notes.md)
- [decomp.dev-Anbindung und Messumfang](docs/decomp-dev.md)

Codex-Decompilierung pausiert; Übergabe an Paperclip auf `hermes-srv`. [Übergabe und nächste Schritte](docs/PAPERCLIP-HANDOFF.md). Nach jedem Fortschritt committen und auf `origin/main` pushen. Für sämtliche Freelancer-Arbeit gilt die [Quotengrenze](docs/PAPERCLIP-QUOTA.md): nur bei nachweislich mehr als 30 % verbleibendem Codex-Wochenlimit, sonst stoppen.
