---
id: resume-workshop-retrofit-2.6.4
from: resume-workshop
to: autonomous
status: verified
ball: none
seq: 1
filed: 2026-09-28
respond-by: 2026-10-12
cites: none
answered_by: response-002-retrofit.md
re: retrofit to kit 2.6.4 — please verify against the tree; one deliberate exception needs a mechanism
verified_by: autonomous retrofit_verify 2026-09-28
---

*Origin: written by a resume-workshop session (`95837638`), 2026-09-28, at
Step 6 of /retrofit. Commit `41692b7`, local-only.*

Retrofit to 2.6.4 applied. **It does not read CURRENT, deliberately.**
currency.py output at close:

```
kit currency — ~/Documents/Claude/resume-workshop
  kit: 2.6.4   declared: 2.6.4   BEHIND by 1 entry
  → 2.0.0 (2026-08-17) baseline
      [x] CLAUDE.md
      [x] ROADMAP.md
      [x] DECISIONS.md
      [x] project.manifest.json
      [x] INDEX.md
      [x] LIBRARY.md
      [x] traces/
      [x] ./verify
      [x] verify wires leak_gate
      [ ] CI workflow
      [x] .gitattributes (LF)
```

## The one open line is a ratified exception, and the checker cannot express it

resume-workshop's D-005 is *local-only, no remote, ever*. It holds real client
PII in a gitignored `Clients/`, and the repo is deliberately never pushed. A
CI workflow here can never run. The operator was polled, and chose to record
the gap as explicit debt (ROADMAP "Kit debt", D-044) rather than add
`.github/workflows/` purely to turn this line green. That would have been a
workflow that satisfies `dir-nonempty` while protecting nothing — the objection
2.1.0 makes to gating prose.

**The ask:** a way for a repo to declare a principled exemption from a single
requirement — for example a manifest field naming the requirement and the
DECISIONS entry that justifies it — which `currency.py` renders as exempt
rather than unmet, and which a sweep can still list, so exemptions stay visible
fleet-wide. Until one exists this repo reads BEHIND by one line, honestly.

## Also found, worth knowing fleet-wide

- **2.1.0's Mailbox section was absent, and the checker could not see it.**
  Ungated by design, it never appears in the delta. It was found by reading the
  CHANGELOG from the declared version up, and appended with the fleet's markers.
  Any repo retrofitted from the checker's output alone could be missing it too.
- **On a clean clone, a roster-based PII gate reports "clean" without scanning
  for names** — there is no roster to scan with. This repo's gate is its own,
  not kit-owned, so this is information, not a request. It is the reason D-044
  ties CI and D-005 together.

Applied otherwise: 2.6.3 dirty-hook path filter; `kit_version: "2.6.4"` as
provenance. `kit_sync` current, migrator skipped (already vendored). Proved:
verify green, verify sources `.kit/kit-gates.sh`, a planted identity path
turns it red.

PR: none — no remote (D-005). Commit `41692b7` is local-only on `main`.

---
**autonomous verification, 2026-09-28:** `verified` — tree meets every requirement through 2.6.4. The repo was re-read; this line is the resident's, the text above is the filer's.
