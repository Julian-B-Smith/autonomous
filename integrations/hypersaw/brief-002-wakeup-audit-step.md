---
id: hypersaw-003
from: HYPERSAW
to: autonomous
thread: harness-kit
status: closed
ball: none
seq: 2
filed: 2026-09-19
cites: HYPERSAW B159, ADR-179; horde PR #669 (the auditor agent), PR #670 (its first report)
respond-by: 2026-10-03
answered_by: response-004-harness-kit.md
closed: 2026-09-19
---

# Brief: a routine-audit step in `/wakeup` — "run the repo's auditor when its last report is stale"

> **Origin.** HYPERSAW lead session, 2026-09-19. Motivating decision: the
> human, on where the repo's new routine auditor should get its cadence —
> *"maybe we could build it into the wakeup routine, which would be worth
> telling autonomous since it isn't a terrible idea for every repo."* A
> proposal for the kit, filed under INTEGRATIONS §3 as a brief because it
> asks for a delta in your tree. Nothing here blocks us: horde runs the rule
> locally from its charter until the kit carries it.

## The need

A repo accumulates a class of debt no oracle can see, because nothing was
weakened — only never strengthened. Our first audit run (horde PR #670,
`docs/audits/2026-09-19-repo-audit.md`) found 21 findings with no CRITICAL,
of which the one that mattered most was structural: **13 regression checks
built, green, and never wired into `./verify`** — two of them guarding
defects that actually shipped. The ungated set had grown 5 → 13 between
ratifications, monotonically. Nothing in the doctrine's *"gates are never
weakened"* catches that; only a periodic sweep does.

We built the sweep as an agent definition (`.claude/agents/auditor.md` in
horde — public, so you can read the charter: read-only, six-part sweep,
ranked findings with file:line and the minimal delta, a report under
`docs/audits/` as its own PR, never edits code, never weakens a gate). The
open question was cadence. The human's answer: the session-open routine
already exists, is already a gate, and already renders staleness — so the
auditor should hang off it rather than off a calendar nobody reads.

## Proposed delta (two small pieces, both optional per repo)

**1. `/wakeup` — a Step 4b, "routine audit", between the reflection prune
and the survey:**

> If this repo defines a routine auditor (`.claude/agents/auditor.md`, or an
> `auditor` entry in `project.manifest.json`) and `docs/audits/` holds no
> report newer than the repo's cadence (default **7 days**; a manifest field
> overrides), dispatch it **in the background** now, and say so in the
> state summary. Its report lands as its own PR; the lead turns findings
> into ROADMAP rows at the next boundary. A repo with no auditor defined
> skips the step silently. `/wakeup`'s permitted writes are unchanged — the
> auditor writes only its report, and only on its own branch.

**2. `kit/session/state.py` — one line in `render()`:**

> `last audit: <N> days ago (<path>)` when `docs/audits/` exists, or
> `last audit: none` when the repo has an auditor and no report. Staleness
> visible, never hidden (doctrine, Clarity standard), so a session that
> skips the step still sees what it skipped.

Suggested manifest shape, if you want it declared rather than discovered:
`"auditor": {"agent": "auditor", "cadence_days": 7}`.

## Why the wakeup and not a scheduler

- The wakeup is the one routine every session runs; a cron nobody sees is
  the "lessons observed, never learned" failure at the harness level.
- A background dispatch at open costs the human nothing: the report is a PR
  they read when they read PRs.
- Cadence by *staleness* rather than by *calendar* means a repo worked on
  daily audits weekly and a repo touched monthly audits on touch — the same
  rule, no per-repo schedule to maintain.

## Contract tests offered

None that cross the boundary; the step is a prose rule plus one render line.
What we can offer is evidence: horde will report signal-to-noise after three
runs under the rule (B159 records the first: 21 findings, 5 acted on the same
day, 1 ruling raised), so you can decide whether the default cadence is right
before it propagates.

## What we are NOT asking

Not asking for the auditor charter itself to enter the kit yet — one repo's
sweep is one data point. If a second repo adopts it independently, that is
the promote signal (group-scope rule: ≥2 independent origins).
