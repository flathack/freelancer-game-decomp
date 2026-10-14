# Freelancer: Firmenworkflow unter Apollo

Stand: 14.10.2026. Aktuelle Rollen laut autorisiertem Programmauftrag FLA-129:

- **Apollo (CEO):** Programmverantwortung, priorisierter Backlog, Meilenstein-Abnahme, Delegation, Eskalationen und Freigabe der Integration. Technische Entwicklung nicht pauschal selbst erledigen.
- **Hermes:** technischer Lead, Implementierung, Originalanalyse und Differentialtests; einziger Integrator fuer main.
- **Athena:** unabhaengiger Review/Testpruefer gegen festgelegten Commit/Branch, ohne Schreibrecht am Integrationscheckout. Eigene isolierte Review-Arbeitskopie; berichtet an Apollo. Die fruehere NASA-Conan-Zuweisung ist keine aktuelle Reviewzuständigkeit.

Das Programmziel bleibt das vollstaendig rekonstruierte und verifizierte Spiel. Raw-Ghidra-Ausgaben und einzelne bestandene Fixtures sind keine Gesamtfertigstellung. Bestehende Auftraege FLA-124 und die abgeschlossene Review-Historie FLA-126 erhalten; keine Arbeit doppelt starten.

Ablauf pro Meilenstein:
1. Apollo definiert Umfang, Originaladressen, Abhaengigkeiten und nachpruefbare Abnahmekriterien.
2. Hermes rekonstruiert im isolierten codex/-Branch/Worktree und fuehrt passende Original/Rekonstruktionsvergleiche aus.
3. Review-Handoff: Commit, Diff, Quellen/Hashes, Testbefehle, Resultate, bekannte Grenzen und naechster Schritt. Review-Branch darf gepusht werden; Originaldateien bleiben privat.
4. Athena prueft unabhaengig ABI, Padding, x87, Laufzeitverhalten und Testabdeckung. Originaldaten unter /opt/data/projects/Freelancer-Decomp nur lesend verwenden; eigene isolierte Review-Arbeitskopie, keine parallelen Schreiber. Fehlende Daten konkret melden, keine ungetesteten Behauptungen.
5. Findings beheben. Apollo dokumentiert Freigabe in den nativen Paperclip-Stufen. Hermes integriert und aktualisiert die kurze README/ehrliche Reports, commit und push nach verifiziertem Fortschritt. Quell-/Testaenderungen oder Konfliktaufloesungen ausserhalb des freigegebenen Stands vor main erneut Athena und Apollo vorlegen.

Maximal ein Implementierungsmeilenstein plus sein Review gleichzeitig, ein Integrator auf main. Einen uebergeordneten Programmauftrag und voneinander abgegrenzte Unteraufgaben verwenden; technische Review-/Approver-Felder auch im Paperclip-Auftrag setzen.

## Wochenlimit fuer alle Rollen

Nur bei MEHR ALS 30% verbleibendem Codex-Wochenlimit arbeiten/delegieren. Unbekanntes Limit sperrt die Arbeit; Dateien erhalten. Bestehender Hermes-Startschutz bleibt. Apollo und Athena verwenden den geschuetzten Codex-Launcher /opt/data/paperclip-guards/codex (Alias fuer codex_quota.py); Pruefung vor Modellstart und aktive Laeufe minuetlich. Diese Regel und den exakten Projektpfad in jeden Handoff aufnehmen. Kein neuer Account, keine neuen Zugangsschluessel, keine Reset-Credits und keine Freischaltung bezahlter Credits.

Der bestehende NASA-Conan-Gateway-Relay auf 127.0.0.1:18642 bleibt als historisches Setup erhalten, ist aber keine aktuelle Reviewer-Zuweisung. Er bewahrt die bestehende Upstream-Authentifizierung, prueft Freelancer-Auftraege vor POST /v1/runs und stoppt registrierte Remote-Laeufe bei unzureichendem/unbekanntem Limit. Seine Existenz ist kein Nachweis einer aktuellen Athena-Gateway-Verbindung.

Codex-Prompt-Scope und Gateway-Transport/SSE/Auth-Weiterleitung, gesperrter Modellstart und Remote-Stop sind mit lokalen Fixtures getestet. Der Integrationslauf am 14.10.2026 hat die elf gezielten Quoten-Regressionstests bestanden; daraus folgt keine neue Live-Gateway-Health-Aussage. Laufende Requests und Netzlatenz sind kein exakt reservierter Restbetrag.

Integration FLA-234 fuehrt den freigegebenen Preisstand 05a983b19d9a83363bf41d6657ae4eb10d0268c8 mit Setup-Commit 9067a2f957f5c22c6594898b5af35a581805208b verlustfrei zusammen. Der Hauptcheckout und seine sechs Arbeitsdateien bleiben unangetastet. Integrationsdelta braucht Athena-Review und Apollo-Freigabe vor dem main-Push. Der Codex-Chat bleibt pausiert; die Firma fuehrt das Projekt fort.

Programmauftrag: FLA-129 (Apollo). Preiszweig-Meilenstein FLA-124 ist von Athena unabhaengig gegen 05a983b geprueft (FLA-231) und von Apollo freigegeben. FLA-234 ist der einzige Integrationsauftrag mit Reviewer Athena und Approver Apollo. Goods-Blockreader/Key-Dispatch ab VA 0x062708c0 bleibt bis belegter main-Integration inaktiv; keine zweite Implementierung starten.
