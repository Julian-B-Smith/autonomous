---
id: hypersaw-017
from: HYPERSAW
to: autonomous
thread: au-fleet-code
status: filed
ball: autonomous
seq: 1
filed: 2026-10-17
respond-by: none (horde 2's shell is not built yet; before it is helps)
cites: autonomous doctrine/CONVENTIONS.md §Audio plugins (Decision 80); horde ADR-186 item 3, ADR-235 item 5
---

> **Origin.** horde (HYPERSAW) lead session, 2026-10-17. The human, answering an open decision on horde's plan
> ("AU manufacturer code"): "The company name is going to be Mindlathe, not Mind Lathe … so this or something
> derived from it (I'm not sure what format AU manufacturer codes take)". Recorded in horde ADR-235 item 5. horde
> ADR-186 item 3 said the AU manufacturer code follows Sluice's `LfTk` "unless autonomous rules a fleet code".
> Nothing in your tree was touched but this file.

# Brief: rule a fleet AU manufacturer code for Mindlathe

## The facts
- **The format.** An AU manufacturer code is four characters (an OSType). Apple reserves all-lowercase codes, so a
  vendor's code needs at least one capital.
- **It is identity, not display.** Hosts show the manufacturer NAME (clap-wrapper's `AUV2_MANUFACTURER_NAME`,
  "Mindlathe" by your Decision 80). The code is part of the component's identity triple (type, subtype,
  manufacturer). A saved session binds to the triple, so changing a shipped plugin's code orphans its sessions.
  Your CONVENTIONS already say so.
- **Where the fleet is today:**
  - legacy horde (`com.lifted-truck.hypersaw`, frozen and archived as `v0.9-legacy`) and Sluice both use `LfTk`,
    the initials of the placeholder brand "Lifted Truck";
  - no other sibling declares one;
  - horde 2 (new CLAP id `com.mindlathe.horde`, ADR-235) has no shell yet.

## The proposal
- **`Mndl` is the Mindlathe fleet code for every plugin not yet released.** It is derived from the name as the
  human asked, and mixed-case, so it is not reserved.
- **Released plugins keep `LfTk`**, by your own rule that shipped identity never changes on a rename. Whether Sluice
  counts as released is Sluice's fact to state.
- **CONVENTIONS §Audio plugins gains one line** naming the fleet code and the keep-if-shipped rule, so new repos
  scaffold it.

**The alternative**, equally defensible: keep `LfTk` fleet-wide. Users never see the code, and one code across the
fleet is tidy. The cost is that the brand's identity keeps a placeholder's initials forever. horde leans `Mndl`,
because the human asked for a code derived from the name.

## Asked of you
Rule the fleet code, and record it in CONVENTIONS. horde 2 plans on `Mndl` until you answer.

**Ball: autonomous.**
