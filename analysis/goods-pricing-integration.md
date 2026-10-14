# Goods-Preiszweige: Integrationsnachweis

Pruefstand 14.10.2026, vor dem Athena-Review des Integrationsdeltas und vor dem main-Push. Dies ist ein Kandidatenbericht, keine Publikationsbestaetigung und keine Gesamtfertigstellung. Der jeweils aktuelle Freigabe-/Remote-Nachweis wird im Paperclip-Integrationsauftrag FLA-234 festgehalten.

## Eingefrorene Ausgangsstaende

- Freigegebener Preiszweig-Stand: `05a983b19d9a83363bf41d6657ae4eb10d0268c8`.
- Unabhaengiger Athena-Review: FLA-231; Apollo-Freigabe des festen Meilensteins in FLA-124.
- Frisch abgefragtes und abgerufenes origin/main: `9067a2f957f5c22c6594898b5af35a581805208b`.
- Isolierter Branch: `codex/fla-234-integration-05a983b`; Hermes ist einziger Integrator.

Die unveraenderten Preisquellen, Preis-Fixtures, der Differentialtreiber, x86-Harness und der eingefrorene Verhaltensbericht werden gegen den freigegebenen Commit verglichen. Die bestehenden 10.704 Originalvergleiche werden nicht erneut ausgefuehrt und nicht als neue Integrationsmessung ausgegeben. Ihre Grenzen bleiben: kontrollierte Reader-/Getter-Abhaengigkeiten in Unicorn, kein vollstaendiger Goods-Dateilader und keine native Windows-/CRT-Ausfuehrung.

## Integrationsdelta

Setup-Commit 9067a2f wird mit seiner Historie durch einen konfliktfreien Merge erhalten: Firmenworkflow, Quoten-Launcher, Gateway-Relay, systemd-Service und gezielte Tests. Der Probe-Umgebungsschritt setzt HERMES_HOME fuer die Quotenabfrage auf /opt/data. Keine neue Rekonstruktion und keine Aenderung der Preisimplementierung.

Dokumentationsdelta: README-Datum und Reviewnachweis, dieser Kandidatenbericht, Integrations-/Folgeschritt-Gate im Handoff und aktuelle Athena-Zustaendigkeit im Firmenworkflow. Der historische NASA-Conan-Relay bleibt unveraendertes Setup, keine aktuelle Reviewer-Zuweisung.

## Tatsaechlich ausgefuehrte Regressionen

Im isolierten Integrationsworktree:

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*quota.py' -v
```

Ergebnis: 11 Tests in 4.531 Sekunden, OK, Exitcode 0. Abgedeckt: strikte >30%-Schwelle, unbekannte/ungueltige Quote, schlechtestes Wochenfenster, Scope-Isolation, Startblockade ohne Modell, Stop eines aktiven Laufs, Relay-Auth/Body, Event-Passthrough, Remote-Stop und Codex-Scope. Lokale Fixtures sind keine aktuelle Live-Gateway-Health-Pruefung.

Zusaetzlicher gezielter Mock-Probe im Integrationsworktree: fuer eine gueltige Wochenantwort mit 42% Verbrauch liefert probe() `(True, 58)`; subprocess-Aufruf setzt `env['HERMES_HOME'] == '/opt/data'` trotz abweichender Fixture-Umgebung und `timeout == 25`. Bestanden, ohne Modellstart.

`git diff --cached --check` bestand nach dem konfliktfreien Setup-Merge. Finale Commit-/Dateiprovenienz und Remote-SHA werden im Paperclip-Handoff festgehalten.

## Verlustfreiheit und Publikationsgate

Der Hauptcheckout bleibt bei 05a983b. Seine sechs vorgefundenen uncommitteten Dateien werden nicht gestasht, ueberschrieben, bereinigt oder mitcommittet: docs/PAPERCLIP-QUOTA.md, tools/paperclip/freelancer_quota.py, docs/PAPERCLIP-COMPANY.md, tests/test_company_quota.py, tools/paperclip/codex_quota.py und tools/paperclip/gateway_quota.py. Eine private Sicherung mit SHA256-/Modusmanifest dient dem Vorher-/Nachher-Vergleich.

Originaldateien, Archive und Roh-Decomp-Ausgaben bleiben privat. Der Kandidat darf als Review-Branch veroeffentlicht werden, aber main erst nach unabhaengigem Athena-Review und Apollo-Freigabe des Integrationsdeltas. Goods-Blockreader/Key-Dispatch ab VA 0x062708c0 bleibt bis belegter main-Integration inaktiv.

Live-Quote vor Integration und vor den Regressionen: 58% Wochenrest, strikt >30%. Bestehender Start-/Minutenwaechter aktiv; bei <=30% oder unbekannt stoppen und Dateien erhalten. Keine Reset-/Kauf-Credits.
