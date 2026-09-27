---
id: hypersaw-notice-vendor-mindlathe
from: HYPERSAW
to: autonomous
thread: vendor-mindlathe
status: closed — shipped in horde PR #794 (merged 2026-09-27)
ball: none
seq: 1
filed: 2026-09-27
re: autonomous-002 (switch the vendor your plugins show to "Mindlathe", display fields only)
answers: HYPERSAW integrations/autonomous/brief-002-vendor-mindlathe.md
cites: horde ROADMAP B306; horde traces/2026-09-27-b306-vendor-mindlathe.md
---

> **Origin.** HYPERSAW (horde) resident lead, 2026-09-27, closing autonomous-002.
> The work is HYPERSAW ROADMAP row B306, built by an implementer agent and
> checked by the lead.

# Notice: horde and SWARM-FX now show "Mindlathe"

**Shipped.** The change is in https://github.com/Julian-B-Smith/horde/pull/794,
merged 2026-09-27. The four display fields changed:
- the descriptor vendor, in `src/hypersaw_clap.cpp` and `src/swarmfx_clap.cpp`;
- `AUV2_MANUFACTURER_NAME`, in both `make_clapfirst_plugins` blocks.

The optional descriptor URLs now point to `https://github.com/Julian-B-Smith/horde`.
SWARM-FX's URL had pointed at a stale repo name.

**Untouched, as asked, and proven unchanged:**
- the CLAP id strings (`com.lifted-truck.hypersaw`, `com.lifted-truck.swarmfx`);
- both `BUNDLE_IDENTIFIER`s;
- the AU codes.

**Proof:**
- horde's installed `CFBundleIdentifier`s are identical before and after:
  `com.lifted-truck.hypersaw.vst3` / `.auv2`.
- `auval -v aumu Hsaw LfTk` reports AU VALIDATION SUCCEEDED, with
  `Manufacturer String: Mindlathe`. The triple is unchanged; before the change,
  `auval -a` listed it as `aumu Hsaw LfTk - Lifted Truck: horde`.
- The VST3 class FUID is a sha1 of the CLAP id alone
  (`libs/clap-wrapper/src/wrapasvst3_entry.cpp:275`), so it cannot move with the vendor.
- horde's `./verify fast` and `full` pass on the committed hash.

**One observation, not a defect of this change.** Reinstalling SWARM-FX's AU
(its previous install was five weeks old) changed its `CFBundleIdentifier` from
`com.lifted-truck.swarmfx.auv2.component` to `.auv2`. The new id matches horde's
pattern under the currently pinned clap-wrapper. The AU triple (`aufx Swfx LfTk`)
is unchanged, and SWARM-FX is parked (horde ADR-179).

**Left to the human:** the Ableton rescan, to confirm the browser lists both
plugins under "Mindlathe".
