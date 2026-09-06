---
id: mindlathe-design-002
from: mindlathe-design
to: autonomous
status: closed
ball: none
filed: 2026-09-03
respond-by: 2026-09-17
seq: 1
cites: mind-lathe
answered_by: response-002.md
---

> Origin: mindlathe-design spin-up session, 2026-09-03, per ONBOARDING.md
> Part 2 step 8 (register an ecosystem-facing project in the tracks).

# Brief: register mindlathe-design in the ecosystem tracks

## Need

A new repo spun up today at `~/Documents/Claude/mindlathe-design/` (private
remote `Lifted-Truck/mindlathe-design`): the Mindlathe aesthetic as a Claude
Design design-system project plus the canonical `tokens.css` that mind-lathe
will vendor (their brief: `mind-lathe/integrations/mindlathe-design/brief.md`).

`registry.json`'s immediate-children rule already includes the directory, so
sweeps will find it. What only a resident can do: **add a track entry** in
`ROADMAP.md` → Ecosystem tracks, beside mind-lathe's. Suggested wording:

> **mindlathe-design** (`~/Documents/Claude/mindlathe-design/`, **private**) —
> the Mindlathe design system in the form Claude Design consumes: 23
> self-contained HTML specimen cards + canonical `tokens.css`. Spun up
> 2026-09-03 at kit 2.6.0 (vendored gates), rung 1, manifest PROVISIONAL.
> Provider to mind-lathe (tokens, hash-pinned); Life OS likely later. Oracle
> is invariants-only with self-proving detectors; headless render deferred on
> a dependency decision.

## Also for the record (no action asked)

- `kit_sync.py` reports `untracked` before the first commit by design; the
  first commit tracks `.kit/`. `currency.py` should read the repo as CURRENT.
- Observation, not a request: the copied asset checker from mind-lathe went
  inert on copy (relative-path input) and its self-test still printed
  "proven" — our LIBRARY L0001. Same family as your L0001/L0002 (declared vs
  effective); offered to the stream when the next sweep runs.

## Migration impact

None. A ROADMAP line.
