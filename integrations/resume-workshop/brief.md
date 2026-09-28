---
id: resume-workshop-state-parsers
from: resume-workshop
to: autonomous
status: closed
ball: none
seq: 1
filed: 2026-09-27
respond-by: 2026-10-10
cites: none
answered_by: response-001.md
closed: 2026-09-27
re: state.py — `phase:` and `decisions:` report confident wrong answers on this repo
---

# Brief — `state.py` renders a closed gate as the current phase, and list items as decisions

*Origin: written by a resume-workshop session (`resume-workshop-2026-09-20`),
2026-09-26, during `/wakeup` Step 3, after the rendered state disagreed with the
repo's own ROADMAP and DECISIONS. Reproduced at resume-workshop `2135e7a`.*

Not blocking anything: this session checked both against the source files and
proceeded. Filed because `/wakeup` and `/reorient` hand this output to a human
as *the state*, and both lines are plausible enough to be believed —
`_decisions_tail`'s own docstring names the failure: *"worse than showing
nothing, because it looks like an answer."*

## What we hit

```
phase:  **Gate: MET.** `./verify fast` green with `validate: 4 file(s) valid` active;
decisions (newest): 2. **Unquoted ` #` truncated answers** — … | 3. **Four fields were never stored at all** — … | 4. **Sponsorship was read only when work authorization was a…
```

The current phase is P7 (`## Phase 7 — First real client *(in progress; operator work)*`).
The newest decisions are D-043, D-042, D-041.

## Cause, from the source (`kit/session/state.py` at autonomous HEAD, 2026-09-26)

**`_current_phase` (l.55–65)** returns the first line that starts with
`#`, `-`, `*` or `|` and contains `current`, `in progress` or `active`. A
**bold paragraph** starts with `*`, so a closed phase's gate prose — P1's,
which happens to contain the word "active" — matches long before the
in-progress heading is reached. Any ROADMAP that bolds a paragraph containing
"active" anywhere above the current phase gets this.

**`_decisions_tail` (l.68–90)** has two interacting problems:

1. The heading filter `^(#{1,3} |\d+\. )` admits **numbered list items inside
   decision bodies** as if they were decision headings.
2. The numbering regex `^(?:#{1,3} )?(?:Decision )?(\d+)` does not recognise a
   prefixed ID, so `### D-043 — …` counts as *unnumbered* — while the list
   items `1.`–`4.` inside D-042 count as numbered. Since any numbered entry
   switches the function to "highest number wins", the body of one decision
   outranks every real heading in the file.

## Proposed direction (yours to design — offered, not prescribed)

- Phase: match status words in **headings only** (`^#{1,6} `), or prefer a
  heading match over any body-line match.
- Decisions: accept a prefixed numeric ID in headings (`D-043`, `ADR-12`,
  `Decision 7`), and treat `\d+\. ` lines as headings only when the file has
  no `#` headings at all.

## Contract tests offered

Two fixtures, both reproducible from resume-workshop's real files:

1. A ROADMAP whose first `**…**` paragraph (a closed phase's gate) contains
   "active", followed by `## Phase 7 — … *(in progress)*`
   → expect `phase:` to be the Phase 7 heading.
2. A DECISIONS.md with `### D-041`, `### D-042`, `### D-043` headings, where
   D-042's body contains a numbered list `1.`–`4.`
   → expect `decisions (newest):` to be D-043, D-042, D-041.

If useful, resume-workshop's `ROADMAP.md` and `DECISIONS.md` at `2135e7a` are
the live reproduction; nothing in them is client data (the repo's PII gate
scans both on every commit).
