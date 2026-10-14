# P2 Archetype: Integration und Publikationshandoff

Stand 14.10.2026, Integrationsauftrag FLA-253. Dies ist keine abgeschlossene Publikationsabnahme und keine Freigabe des nächsten Meilensteins.

## Feste Grundlage und unveränderte Übernahme

- Candidate `cafce1406d75785e9069f2dcb5102c732701e8f8`, direkter Parent/feste Basis `8f44ff91f1086f33fd81ca1c4f65f637a9733bf2`.
- Native Athena-Commitabnahme auf FLA-246, Revision `9c47c5dd-8c42-45dd-97ca-66270bc08332`; Apollo-Commitfreigabe Revision `2b2fb7a4-5906-49ba-a1a7-6208a37ae865`. Die separate Integrations-/Pushfreigabe erteilt FLA-253 ausschließlich für diesen Candidate.
- Scope FLA-244, Revision `80fd52f4-adfd-4368-aa6b-160b41cddfe7`, SHA256 `ccfa7f72b4104eec69917073b582d11227c7870e9848396504b85c94276252e7`; Original common.dll SHA256 `e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483`, frisch bestätigt. Originaladressen/Spans und A01–A18 unverändert.
- Frischer Remote-Abgleich bestätigte die feste Basis als origin/main. Beide Setup-Historien einschließlich `05a983b19d9a83363bf41d6657ae4eb10d0268c8` und `9067a2f957f5c22c6594898b5af35a581805208b` sind darin bereits enthalten; keine erneute oder verlustbehaftete Setup-Übernahme.
- Isolierter Branch `codex/fla-253-p2-publication`; Worktree `/opt/data/projects/Freelancer-Decomp/build/worktrees/fla-253-integration`. Konfliktfreier No-FF-Merge des unveränderten Candidate. Kein Amend, Reset oder Force-Push.
- Publikationsdelta zum Candidate: ausschließlich `README.md` und dieser Bericht. Sämtliche 389 versionierten Candidate-Dateien waren nach den Regressionen byteidentisch; Quellen, Tests, frühere Berichte und FLA-126-Historie bleiben unverändert. Der feste Integrations-SHA und frische Remote-main-Nachweis werden nach Commit/Push auf FLA-253 im Publikationsdokument und Commit-Work-Product festgehalten.

## Hier tatsächlich frisch ausgeführt

Die vier vollständigen unveränderten x86-Suiten wurden im Integrationsworktree neu gebaut und ausgeführt, keine Quick-Smoke-Abnahme. Separate Laufberichte/Logs sowie vollständige Compiler-/Linker-argv, Exitcodes und Hashes liegen im dauerhaften Handoffartefakt auf FLA-253. Frühere Candidate-Berichte wurden nach dem Sichern der neuen Laufberichte byteexakt erhalten, nicht überschrieben.

| Prüfung | Exit | Frisches Resultat |
|---|---:|---|
| `tests/verify_archetype_metadata_x86.py` | 0 | 6506 Readerpaare, 13012 unabhängige Oracles, 4 is_attached-Paare; alle zehn kompilierten Defektkategorien erkannt |
| `tests/verify_archetype_metadata_coupled_x86.py` | 0 | 30 Sequenzen/600 Readerpaare, 128 gekoppelte P1-Paare, 256 ABI-/256 Destruktoraufrufe; 12 Lookup-Grenzpaare, 5 separat gezählte Faultpaare; alle fünf P2-Originaleinstiege tatsächlich gesperrt |
| `tests/verify_good_block_reader_x86.py` | 0 | 6696 Paare, 13296 erfolgreiche ABI-/13296 Destruktoraufrufe, 6696 unabhängige Oraclefälle; alle sechs kompilierten Defektkontrollen erkannt; Faults separat |
| `tests/verify_archetype_lookup_x86.py` | 0 | 96000 Equipment-/Fehlerlogvergleiche, 48000 ID-Aliasaufrufe |
| `-m unittest discover -s tests -p 'test*quota.py' -v` | 0 | 11 Tests erfolgreich; 30%/29%/unbekannt-Ausgaben stammen aus kontrollierten Testfixtures, nicht aus der Livequote |

Reproduktion mit unveränderten Tests:

    export PATH="/opt/data/projects/Freelancer-Decomp/.tools/bin:$PATH"
    /opt/data/projects/Freelancer-Decomp/.venv/bin/python tests/verify_archetype_metadata_x86.py
    /opt/data/projects/Freelancer-Decomp/.venv/bin/python tests/verify_archetype_metadata_coupled_x86.py
    /opt/data/projects/Freelancer-Decomp/.venv/bin/python tests/verify_good_block_reader_x86.py
    /opt/data/projects/Freelancer-Decomp/.venv/bin/python tests/verify_archetype_lookup_x86.py
    /opt/data/projects/Freelancer-Decomp/.venv/bin/python -m unittest discover -s tests -p 'test*quota.py' -v

Die **104 zusätzlichen Athena-Grenzpaare** aus FLA-246 sind ausdrücklich wiederverwendete unabhängige Reviewevidenz, hier nicht erneut ausgeführt. Die dort bereits abgeschlossenen Athena-/Apollo-Entscheide bleiben feste Provenienz; sie sind keine Abnahme dieses Integrationscommits. Mengen werden nicht addiert, um eine Fertigstellungsquote zu erfinden.

## Schutz, Kollision und Dateierhalt

Gemeldeter Vorlauf `a295a669-17e9-4c65-9af4-7034623820ea`: API-Status `succeeded`, beendet 14.10.2026 um 12:14:28.973 UTC. Gemeldeter gemeinsamer Elternlauf `0b01bdd0-0f5f-4fda-9482-8fa41b464c86`: `succeeded`, beendet um 12:16:03.715 UTC. Beide waren vor Integrationsmutation beendet. Keine schreibend geöffneten Dateien in Projekt/Candidate unter den lesbaren /proc-Deskriptoren festgestellt. Systemfremde Prozess-FDs waren teilweise unzugänglich; privilegierte Vollprobe scheiterte an fehlendem nichtinteraktivem sudo. Kein behaupteter systemweiter Ausschluss. Zusätzlich wurden HEAD, Index, vollständiger Status sowie alle sechs lokalen Änderungen vor und nach Arbeit auf Identität geprüft; isolierte Schreibpfade und Commitkoordination statt Eingriff in den gemeinsamen Checkout.

Die sechs Setup-Arbeitsdateien und sämtliche gefundenen lokalen Änderungen wurden vor Mutation separat gesichert, mit SHA256/Größe/Modus bestätigt und am ursprünglichen Ort belassen. Hauptcheckout blieb HEAD `05a983b19d9a83363bf41d6657ae4eb10d0268c8`, unveränderter Index und unveränderte sechs Statuszeilen. Der lokale Hauptbranch wird nicht umgestellt; Veröffentlichung erfolgt ausschließlich aus dem isolierten Branch.

Frische Livequote zu Beginn 42%, vor und während Regressionen 41%. Geschützter Elternlauncher `/opt/data/paperclip-guards/freelancer_quota.py` anhand /proc bestätigt, Wächterintervall 60 Sekunden; Testhelfer prüft zusätzlich vor jedem Lauf und alle 60 Sekunden und stoppt bei unbekannt/<=30%. Pflicht für jede Folgezuweisung: exakter Projektpfad `/opt/data/projects/Freelancer-Decomp`; ausschließlich bekannt strikt **mehr als 30%** Codex-Wochenrest; geschützter Start und minütlicher Wächter; sonst stoppen und Dateien erhalten, keine Credits/Resets.

DailyTasks-Kontext und OpenAPI gelesen. Vollständige Titelsuche und offene/wartende Aufgabenlisten enthalten keine passende [Paperclip]-Aufgabe; **keine zugehörige DailyTasks-Aufgaben-ID**, keine Mutation und keine Ersatzaufgabe erzeugt. Bei später ausdrücklich freigegebenem Eintrag: vor Änderung aktuellen Stand lesen, Notizen erhalten, zur Prüfung `wartend`, `erledigt` erst nach Stevens Bestätigung. Vault-Pull --rebase scheiterte an HTTPS-Authentifizierung; Home und relevante Freelancer-/Gitea-Wikilinks lokal gelesen, kein erfolgreicher Sync behauptet.

Eine erste lokale Ignoreprüfung scheiterte, weil Git einen Verzeichnissymlink nicht wie `original/` behandelt. Vor Staging wurde ausschließlich dieser neu angelegte lokale Symlink durch ein echtes ignoriertes Verzeichnis mit Dateisymlink zu common.dll ersetzt; erfolgreiche Ignoreprüfung und leere versionierte Original-/Roh-Decomp-Pfadliste. Keine Originaldateien, Archive oder Roh-Decomp-Ausgaben veröffentlichen.

## Offene Grenzen und nächster Owner

Reale DB-/Loaderfälle **0**. Kontrolliertes inherit ist kein rekonstruierter Kopierkörper. Native Windows/CRT, Konstruktion/Lebenszyklus, GoodInfo-Callback, malformed-Sentinel, unmaskierte x87-Ausnahmen und Gesamtspiel bleiben offen. Emulator-/synthetische Paarvergleiche sind keine produktive Spielabnahme. Historische Preis-/P1-Abnahmen und FLA-126 bleiben erhalten.

Nach Commit/Push und frischem Remote-readback prüft Athena den **festen Integrationscommit und ausschließlich das Publikationsdelta** read-only in eigener Kopie, dokumentiert auf FLA-253 und entscheidet in dessen nativer Reviewstufe. Danach Apollo-Abschlussfreigabe. Quell-/Teständerung oder semantische Konfliktlösung würde vor main einen erneuten Athena-Review und eine neue Apollo-SHA-Freigabe erfordern. Kein nächster Meilenstein vor positiver Publikationsabnahme.
