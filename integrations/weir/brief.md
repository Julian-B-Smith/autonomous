---
id: weir-001
from: Weir
to: autonomous
status: filed
ball: autonomous
seq: 1
filed: 2026-10-28
cites: HYPERSAW
---

> **Origin.** Weir spin-up, 2026-10-28, run by horde's (HYPERSAW's) lead session at
> the human's request ("We should probably start building them out in C++ directly in
> a parallel repo"), per `/spinup` step 8 ("ask a resident of autonomous to register it
> in the ecosystem tracks — a ROADMAP edit, resident-only"). Weir's D-001, D-002.

# Brief — register `synthetic-worlds/Weir` in the execution-project registry

**What:** `~/Documents/Claude/synthetic-worlds/Weir/` (PRIVATE remote
github.com/Julian-B-Smith/weir, created 2026-10-28). Weir is horde's filter library: a framework-free C++ library of filter DSP,
every type behind one interface, run as a per-voice stereo instance. It starts from
horde's filter lab (B566) and its C++ transcription, but the C++ leads: the lab is a
starting point, not a parity target. No plugin of its own. Spun up 2026-10-28 via
`/spinup`; survey answered by poll, manifest ratified by poll. Kit 2.10.0 (gates
vendored, `.kit/` pinned; `./verify fast` green with the day-zero manifest gate and
its planted faults). Rung 1.

**Ask:** one line in autonomous `ROADMAP.md` §Ecosystem tracks → execution-project
registry, in the Scape shape. Relationships: consumes autonomous; consumed by
HYPERSAW/horde (the engine's per-voice filter slot and the FX filter module; notice
`weir-notice-spinup` filed in horde's tree today). Group: synthetic-worlds (covered by
`registry.json`'s immediate-children rule; this brief is for the tracks section only).

**Note for VISIBILITY.md:** private by the human's choice (Weir D-001), which matches
the private-by-default rule there; its name may appear in horde's tracked files.
