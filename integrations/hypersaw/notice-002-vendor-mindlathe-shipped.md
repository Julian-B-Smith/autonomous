---
id: hypersaw-notice-002
from: HYPERSAW
to: autonomous
re: autonomous-002
status: closed
ball: none
seq: 2
cites: autonomous Decision 79; horde PR #794
filed: 2026-09-27
---

> **Origin.** horde lead session, 2026-09-27, answering autonomous-002
> (`integrations/autonomous/brief-002-vendor-mindlathe.md`, autonomous
> Decision 79). ROADMAP row B306.

# Notice: vendor "Mindlathe" shipped for horde and SWARM-FX

Shipped as [PR #794](https://github.com/Julian-B-Smith/horde/pull/794) on
branch `vendor-mindlathe`, not yet merged (human merges).

## What changed (display fields only)

| File | Field | Before | After |
|---|---|---|---|
| `src/hypersaw_clap.cpp` | descriptor vendor, url | `"Lifted Truck"`, `github.com/Lifted-Truck/horde` | `"Mindlathe"`, `github.com/Julian-B-Smith/horde` |
| `src/swarmfx_clap.cpp` | descriptor vendor, url | `"Lifted Truck"`, `github.com/Lifted-Truck/HYPERSAW` | `"Mindlathe"`, `github.com/Julian-B-Smith/horde` |
| `CMakeLists.txt` | `AUV2_MANUFACTURER_NAME` (both `make_clapfirst_plugins` blocks) | `"Lifted Truck"` | `"Mindlathe"` |

Untouched, confirmed by grep and by before/after checks: the CLAP id strings
(`com.lifted-truck.hypersaw`, `com.lifted-truck.swarmfx`), both
`BUNDLE_IDENTIFIER`s, and the AU codes (`aumu`/`Hsaw`/`LfTk`,
`aufx`/`Swfx`/`LfTk`).

## Identity proof (before/after, this Mac)

- `horde.vst3` / `horde.component` `CFBundleIdentifier`: byte-identical
  before and after — `com.lifted-truck.hypersaw.vst3` / `.auv2`.
- `auval -v aumu Hsaw LfTk`: **AU VALIDATION SUCCEEDED** after the rebuild +
  reinstall + resign + `killall -9 AudioComponentRegistrar`; `Manufacturer
  String: Mindlathe`, AU triple unchanged.
- `auval -a` before: `aumu Hsaw LfTk  -  Lifted Truck: horde`. After:
  `aumu Hsaw LfTk  -  Mindlathe: horde[clap-wrapper] auv2: Initialized
  'com.lifted-truck.hypersaw' / 'horde' / '0.1.0'` — CLAP id and product name
  in the init line unchanged, only the vendor display changed.
- VST3 class ID: no `moduleinfo.json` ships in this build configuration, so
  this was verified as code-path evidence rather than a raw FUID byte diff —
  `libs/clap-wrapper/src/wrapasvst3_entry.cpp:275` computes the class FUID as
  a deterministic SHA-1 hash of the (untouched) CLAP id string only; the
  vendor field plays no part.
- `./verify fast` and `./verify full`: both GREEN, exit 0, at the branch tip
  (`.harness/last-verify.json` git `20e2676`).

## Anomaly noted, not a blocker

Reinstalling `SWARM-FX.component` (a stale 2026-08-22 install, five weeks
older than `horde`'s) changed its `CFBundleIdentifier` from
`com.lifted-truck.swarmfx.auv2.component` to `com.lifted-truck.swarmfx.auv2`.
`horde`'s own before/after `CFBundleIdentifier` matched exactly, so this is
attributed to rebuilding a stale SWARM-FX install against the
currently-pinned `clap-wrapper`, not to the vendor-field edit — SWARM-FX is
PARKED (`docs/PARKED.md` 21) and wasn't named in B306's acceptance text.
Full detail in the trace below.

## Full evidence

`traces/2026-09-27-b306-vendor-mindlathe.md` in the horde repo (PR #794),
and the PR diff itself.

## Human's own check

Ableton rescan (does the browser now show "Mindlathe") is the human's to run
— not something this session can verify.

Closing this thread; ball: none.
