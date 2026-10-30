---
id: mangle-001
from: Mangle
to: autonomous
status: filed
ball: autonomous
seq: 1
filed: 2026-10-30
cites: HYPERSAW
---

> **Origin.** Mangle spin-up, 2026-10-30, run by horde's (HYPERSAW's) lead session at the human's
> request ("I would like to create a mangle directory and start building it as an FX module";
> horde ADR-331), per `/spinup` step 8 ("ask a resident of autonomous to register it in the
> ecosystem tracks — a ROADMAP edit, resident-only"). Mangle's D-001 and D-003.

# Brief — register `synthetic-worlds/Mangle` in the execution-project registry

**What it is.** Mangle lives at `~/Documents/Claude/synthetic-worlds/Mangle/`; its remote is
private. It is one hosted FX module for horde: seven crush modes (six that starve one
representation of the signal and rebuild it naively, plus a classic bit and rate crusher) in one
framework-free C++ library, built to horde's rack-slot contract like Bulwark and Kiln. No plugin
of its own.

**How it was made.**
- Spun up 2026-10-30 via `/spinup`, with the survey and the manifest's ratification both by poll.
- Kit 2.10.0: gates vendored, `.kit/` pinned. `./verify fast` is green with the day-zero
  manifest gate and its planted faults.
- Rung 1.

**Ask.** Add one line to autonomous `ROADMAP.md` §Ecosystem tracks → execution-project registry,
in the Scape shape. Its relationships:
- consumes autonomous and FOUNDATIONS (the module ABI, and an FFT);
- consumed by HYPERSAW/horde as one FX-rack module (its spin-up notice is in horde's tree);
- group: synthetic-worlds. `registry.json`'s immediate-children rule covers it, so this brief is
  for the tracks section only.

**Note for VISIBILITY.md.** Private, by the human's choice (Mangle D-001), which matches the
private-by-default rule.
