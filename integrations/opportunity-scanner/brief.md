---
id: opportunity-scanner-001
from: opportunity-scanner
to: autonomous
status: closed
ball: none
seq: 1
filed: 2026-09-17
respond-by: 2026-10-01
cites: none
answered_by: response-001.md
closed: 2026-09-17
---

<!-- provenance: authored by the opportunity-scanner /spinup session,
     2026-09-17, per ONBOARDING Part 2 step 8 (ask a resident of autonomous
     to register a new execution project). Motivating decision:
     opportunity-scanner D-0006. -->

# Brief: register opportunity-scanner in the execution-project registry

## Need

`~/Documents/Claude/opportunity-scanner/` was spun up 2026-09-17 via `/spinup`
on kit 2.6.0 (survey → `project.manifest.json` → harness → vendored gates →
`./verify fast` green → initial commit). ONBOARDING Part 2 step 8 says a new
ecosystem participant asks a resident of autonomous to register it in the
ROADMAP's **Execution-project registry** — that list is a resident-only
ROADMAP edit, so this brief is the request.

The mechanical roster (`registry.json`, rule `~/Documents/Claude` →
immediate-children) already includes the directory, so `kit_sync --all` and
currency sweeps see it today; nothing there needs changing.

## Proposed registry line

- **opportunity-scanner** (`~/Documents/Claude/opportunity-scanner/`, private)
  — marketplace-surface scanner: a Markdown+YAML registry/signals/trials
  corpus as the durable product, with disposable Python adapters, a niche
  scanner, and emergence/exit watchers over it. Spun up 2026-09-17 via
  /spinup; manifest provisional pending ratification; rung 1 (single thread —
  sequential, human-gated build order; rung 2 is a recorded Phase-2 decision
  if hollowness assessment fans out). CI mirrors the Stop hook (`verify fast`
  on ubuntu; `full` = adapter health, network, human-run). Consumes autonomous
  only; no consumers. Not upstream of anything — a registry line, not a track.

## Contract tests offered

None — no interface crosses the boundary. The repo's own `./verify fast`
(kit_integrity, leak_gate, plant_not_tracked, corpus validation, validator
goldens) is the only oracle involved and `kit/currency.py` reads it directly.

## Migration impact

None for any repo.
