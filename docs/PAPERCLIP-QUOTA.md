# Freelancer weekly quota policy

User requirement: run decompilation only while MORE THAN 30% of the Codex weekly allowance remains. 30% exactly is blocked. Compare remaining = 100 minus used, not used itself.

The Paperclip Hermes command is `/opt/data/paperclip-guards/freelancer_quota.py`. Source is tools/paperclip/freelancer_quota.py. It recognizes Freelancer chat assignments by the project path or exact routine title in the query; other Hermes tasks pass through to the original command. It queries the existing `hermes usage --provider openai-codex --json` under Paperclip's HERMES_HOME=/opt/data. No secrets are printed or copied.

Before launching a Freelancer model, require a numeric valid Weekly window with remaining >30. Unknown data, timeout, provider mismatch or invalid numbers block the launch. Active protected jobs recheck every 60 seconds; at <=30 or unknown, SIGINT requests shutdown, followed by TERM/KILL if needed. Files stay on disk. Already-running process 377831 received a temporary user service watcher, with process identity checks against PID reuse. That watcher expires when the process ends. New jobs use the command wrapper automatically.

The routine remains enabled every 15 minutes, so later ticks retry without consuming a model call when quota is insufficient. Work can resume when the weekly limit resets or remaining exceeds 30. No reset credits are redeemed and no paid credits are purchased. Usage polling and network latency mean an in-flight request may finish before the next check; this is a sampled stop threshold, not a reservation of exactly 30% capacity.

Tests cover strict threshold, missing/invalid data, worst weekly window, unrelated-task isolation, blocked startup without launching a model, and active-run stopping. Current Hermes account observation on 2026-10-13: 10% used / 90% remaining.

Die Firmenausfuehrung ist inzwischen auch fuer Apollo und NASA-Conan geschuetzt. Details in PAPERCLIP-COMPANY.md. Gateway-Relay-Service: tools/paperclip/systemd/freelancer-quota-gateway.service.
