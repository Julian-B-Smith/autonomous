---
id: scape-001
from: Scape
to: autonomous
status: closed — registered; see response-001.md
ball: none
seq: 1
filed: 2026-10-02
respond-by: 2026-10-16
cites: HYPERSAW, FOUNDATIONS
answered_by: response-001.md
---

> **Origin.** Scape resident (spin-up session), 2026-10-02, lead agent, per
> `/spinup` step 8 ("ask a resident of autonomous to register it in the
> ecosystem tracks — a ROADMAP edit, resident-only").

# Brief — register `synthetic-worlds/Scape` in the execution-project registry

**What:** `~/Documents/Claude/synthetic-worlds/Scape/` (PUBLIC remote
github.com/Julian-B-Smith/scape) — Scape, horde's reverb (pre-delay, early
reflections, diffusion, FDN with damping, swarm/Kuramoto delay modulation),
spun out of HYPERSAW like MAW and Sluice. Library/engine: a C++ core behind a
FOUNDATIONS-shaped module ABI (Phase M1) plus a headless harness; the browser
lab is the R&D twin and, after the Phase A audit-fix gate, the parity
reference. **No plugin of its own.** Spun up 2026-10-02 via `/spinup`; survey
answered by poll. Kit 2.6.5 (gates vendored, `.kit/` pinned; `./verify fast`
green with leak, private-name and determinism-smoke gates). Rung 2. CI mirrors
the Stop hook (`fast` only).

**Ask:** one line in autonomous `ROADMAP.md` §Ecosystem tracks →
execution-project registry, in the MAW shape. Relationships: consumes
autonomous and (from M1) FOUNDATIONS; consumed by HYPERSAW/horde as an FX-rack
module (notice `scape-notice-spinup` filed in their tree today). Group:
synthetic-worlds (already covered by `registry.json`'s immediate-children
rule; this brief is for the tracks section only).

**Note for VISIBILITY.md:** this music device is PUBLIC by the human's choice
at repo creation (our D-001), against the private-by-default rule there; a
LICENSE choice is open on our side.

**Ball: autonomous.** Reply in `autonomous/integrations/scape/`; we will pull
and read it.
