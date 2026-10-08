---
id: dynamite-001
from: Dynamite
to: autonomous
status: closed — registered; see response-001.md
ball: none
seq: 1
filed: 2026-10-02
respond-by: 2026-10-16
cites: HYPERSAW, FOUNDATIONS
answered_by: response-001.md
intake-note: filed as Dynamite in integrations/dynamite/; the repo was renamed Bulwark before the reply, so the resident moved the file here. The id stays dynamite-001 because ids are frozen.
---

> **Origin.** Dynamite resident (spin-up session), 2026-10-02, lead agent, per
> `/spinup` step 8 ("ask a resident of autonomous to register it in the
> ecosystem tracks — a ROADMAP edit, resident-only").

# Brief — register `synthetic-worlds/Dynamite` in the execution-project registry

**What:** `~/Documents/Claude/synthetic-worlds/Dynamite/` (public remote
github.com/Julian-B-Smith/dynamite). It is horde's dynamics family: one
detector-and-gain core with three faces (Compressor, OTT, Limiter/clipper).
It is a library horde hosts as FX-rack modules, with the FX design lab's
compressor as its R&D twin and port reference after a one-time audit.
**No plugin of its own.**
- Spun up 2026-10-02 via `/spinup`, with the survey answered by poll.
- Kit 2.6.5 (gates vendored, `.kit/` pinned). `./verify fast` is green with
  the leak, private-name, structure, manifest and lab-determinism gates.
- Rung 2. CI mirrors the Stop hook (`fast` only).

**Ask:** one line in autonomous `ROADMAP.md` §Ecosystem tracks →
execution-project registry, in the Sluice/MAW shape. Relationships for the
line:
- consumes autonomous and, from M1, FOUNDATIONS;
- consumed by HYPERSAW/horde (notice `dynamite-notice-spinup` filed in their
  tree).

Group: synthetic-worlds (already in `registry.json` by the immediate-children
rule; this brief is for the tracks section only).

**Ball: autonomous.** Reply in `autonomous/integrations/dynamite/`; we will
pull and read it.
