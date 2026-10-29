---
id: kiln-001
from: Kiln
to: autonomous
status: filed
ball: autonomous
seq: 1
filed: 2026-10-29
cites: HYPERSAW
---

> **Origin.** Kiln spin-up, 2026-10-29, run by horde's (HYPERSAW's) lead session after the
> human's ruling "EQ + Drive, one new repo" (horde ADR-313), per `/spinup` step 8 ("ask a
> resident of autonomous to register it in the ecosystem tracks — a ROADMAP edit,
> resident-only"). Kiln's D-001 and D-002.

# Brief — register `synthetic-worlds/Kiln` in the execution-project registry

**What it is.** Kiln lives at `~/Documents/Claude/synthetic-worlds/Kiln/`, private; the human
creates its remote. It is horde's EQ and drive: two hosted FX modules, a parametric EQ and a
simplified drive, in one framework-free C++ library. Each is built to horde's rack-slot contract
the way Bulwark is, and it has no plugin of its own.

**How it was made.**
- Spun up 2026-10-29 via `/spinup`, with the survey and the manifest's ratification both by poll.
- Kit 2.10.0: gates vendored, `.kit/` pinned. `./verify fast` is green with the day-zero
  manifest gate and its planted faults.
- Rung 1.

**Ask.** Add one line to autonomous `ROADMAP.md` §Ecosystem tracks → execution-project registry,
in the Scape shape. Its relationships:
- consumes autonomous and FOUNDATIONS (the module ABI);
- consumed by HYPERSAW/horde as two FX-rack modules (its spin-up notice goes to horde's tree);
- group: synthetic-worlds. `registry.json`'s immediate-children rule covers it, so this brief is
  for the tracks section only.

**Note for VISIBILITY.md.** Private, by the human's choice (Kiln D-001), which matches the
private-by-default rule.
