# Freelancer: Firmenworkflow unter Apollo

- **Apollo (CEO):** Programmverantwortung, priorisierter Backlog, Meilenstein-Abnahme, Delegation, Eskalationen und Freigabe der Integration. Technische Entwicklung nicht pauschal selbst erledigen.
- **Hermes:** technischer Lead, Implementierung, Originalanalyse und Differentialtests; einziger Integrator fuer main.
- **NASA-Conan:** unabhaengiger Review/Testpruefer. Read-only Review gegen festgelegten Commit/Branch, kein paralleles Schreiben ins Integrationsverzeichnis. Berichtet an Apollo.

Das Programmziel bleibt das vollstaendig rekonstruierte und verifizierte Spiel. Raw-Ghidra-Ausgaben und einzelne bestandene Fixtures sind keine Gesamtfertigstellung. Bestehende Auftraege FLA-124 und FLA-126 erhalten; keine Arbeit doppelt starten.

Ablauf pro Meilenstein:
1. Apollo definiert Umfang, Originaladressen, Abhaengigkeiten und nachpruefbare Abnahmekriterien.
2. Hermes rekonstruiert im isolierten codex/-Branch/Worktree und fuehrt passende Original/Rekonstruktionsvergleiche aus.
3. Review-Handoff: Commit, Diff, Quellen/Hashes, Testbefehle, Resultate, bekannte Grenzen und naechster Schritt. Review-Branch darf gepusht werden; Originaldateien bleiben privat.
4. NASA-Conan prueft unabhaengig ABI, Padding, x87, Laufzeitverhalten und Testabdeckung. Originaldaten liegen auch auf nasa-cachy im urspruenglichen /mnt/ai-models/PROJECTS/TASKS/Freelancer-Decomp; dort eine eigene Review-Arbeitskopie verwenden. Fehlende Daten konkret melden, keine ungetesteten Behauptungen.
5. Findings beheben. Apollo dokumentiert Freigabe. Hermes integriert und aktualisiert die kurze README/ehrliche Reports, commit und push nach verifiziertem Fortschritt.

Maximal ein Implementierungsmeilenstein plus sein Review gleichzeitig, ein Integrator auf main. CEO-Routine alle 15 Minuten, coalesce if active. Einen uebergeordneten Programmauftrag und voneinander abgegrenzte Unteraufgaben verwenden; technische Review-/Approver-/Monitor-Felder auch im Paperclip-Auftrag setzen.

## Wochenlimit fuer alle drei Rollen

Nur bei MEHR ALS 30% verbleibendem Codex-Wochenlimit arbeiten/delegieren. Unbekanntes Limit sperrt die Arbeit. Bestehender Hermes-Startschutz bleibt. Apollo verwendet Codex CLI ueber /opt/data/paperclip-guards/codex (Alias fuer codex_quota.py); Prompt wird vor Modellstart geprueft, aktive Laeufe minuetlich. NASA-Conans bestehender Gateway wird durch einen nur auf 127.0.0.1:18642 gebundenen Relay gefuehrt. Er bewahrt die bestehende Upstream-Authentifizierung, prueft Freelancer-Auftraege vor POST /v1/runs und stoppt registrierte Remote-Laeufe bei unzureichendem/unbekanntem Limit. Kein neuer Account, keine neuen Zugangsschluessel und keine Freischaltung bezahlter Credits.

Codex-Prompt-Scope und Gateway-Transport/SSE/Auth-Weiterleitung, gesperrter Modellstart und Remote-Stop sind mit lokalen Fixtures getestet. Server-Gateway-Health und Paperclip-Verbindungstests bestehen. Die Grenze wird minuetlich abgefragt; laufende Requests und Netzlatenz sind kein exakt reservierter Restbetrag.

Vor dem naechsten Integrations-Push Setup-Commits von origin/main ohne Verlust laufender Arbeitsdateien integrieren. Der Codex-Chat bleibt pausiert; die Firma fuehrt das Projekt fort.

Programmauftrag: FLA-129 (Apollo), mit NASA-Conan als Reviewer. Laufender Implementierungsauftrag FLA-124 ist Unterauftrag davon, mit Reviewer NASA-Conan und Approver Apollo. Routine `34df3d50-f7c7-4964-9aba-7fcded82076b` heisst jetzt Freelancer: CEO-Steuerung und Meilensteine und ist Apollo zugeordnet.
