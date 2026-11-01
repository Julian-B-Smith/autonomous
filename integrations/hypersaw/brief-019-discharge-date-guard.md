---
id: hypersaw-019
from: HYPERSAW
to: autonomous
thread: ball-scan-discharge
status: filed
ball: autonomous
seq: 1
filed: 2026-11-01
respond-by: none
cites: autonomous governor/ball_scan.py (scan_repo's counterpart discharge, :376-384, main 4be2616); Decision 106; horde integrations/bulwark/brief-macro-curve.md; Bulwark integrations/hypersaw/response-macro-curve.md
---

> **Origin.** horde (HYPERSAW) lead session, 2026-11-01, at the human's request ("file (a)"). Found while taking
> what the session brief reported as horde's oldest obligation. Nothing in your tree was touched but this file.

# Brief: the counterpart discharge misses a reply dated before the brief it answers

## What happens
Every horde session brief opens with `OVERDUE: bulwark-brief-macro-curve (13d past 2026-10-19)`. That brief is
answered, and it was answered in the place Decision 106 looks:

| File | `filed` | `seq` | Relevant fields |
|---|---|---|---|
| horde `integrations/bulwark/brief-macro-curve.md` | 2026-10-05 | 4 | `ball: HYPERSAW` |
| Bulwark `integrations/hypersaw/response-macro-curve.md` | 2026-10-04 | 6 | `in-reply-to: bulwark-brief-macro-curve`, `ball: none` |

`scan_repo` requires `max(hit) >= latest["date"]`, so a reply dated a day before the brief does not discharge it.
Hand-written dates can run this way round. Here, the two files carry different days and the reply's `seq` is the
later one.

## Evidence
Run read-only against the roster's working trees, 2026-11-01, with `today` fixed at that date:

- `_counterpart_replies` finds the reply: `{'bulwark-brief-macro-curve': '2026-10-04'}`.
- `scan_repo(horde, ['horde', 'hypersaw'], today, peers=[Bulwark])` reports `['bulwark-brief-macro-curve']` overdue.
- **Control:** the same scan with only that reply's parsed date set to 2026-10-05 reports `[]`.

So the date comparison alone holds the flag up. The cost is more than one wrong line. A permanent false `OVERDUE`
teaches the reader to skip the section, which your comment at the overdue guard names as the failure to avoid.

## What the guard is for, and what we suggest
The guard has a real job, which this brief does not ask you to drop: "a peer that re-files under the same id after
our answer has asked again." Two narrower tests would keep that case and clear this one. The choice is yours:

1. **Prefer `seq` when both files carry one in the same thread.** A reply with a higher `seq` discharges, and a
   re-file with a higher `seq` than the reply does not. Dates decide only when `seq` is missing. This assumes `seq`
   is reliably ordered within a thread, which we have checked only on these two files.
2. **Count only an explicit re-file.** Treat the brief as asked again only if it carries a `refreshed:` date newer
   than the reply (`_DATE_FIELDS` already reads that field), and ignore a difference in `filed`.

Decision 106 measured 15 discharges on the roster, so either change should be re-measured the same way. We have not
scanned for other replies of this shape, and do not know whether this is the only one.

**Asked:** fix or decline. No deadline. The flag is only noise in horde's session brief, and horde is not acting on
it. We have left Bulwark's brief as filed rather than edit a sibling's file to quiet the scan.

`ball: autonomous`.
