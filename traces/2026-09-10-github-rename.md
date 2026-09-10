# 2026-09-10 — the GitHub account rename, end to end

**Decisions:** 70 (name), 72 (org spelling), 69 (plugins rename first).
**Runbook:** the Rename Runbook artifact (Phases 0–3). **Tool:** `kit/rename_owner.py`.

## Sequence

| when | act | evidence |
|---|---|---|
| 09-07 | 34 repos had no description; 30 set from READMEs, 3 shells archived (`grust`, `the-governor`, `mind.lathe`) | `gh repo list` reads none empty |
| 09-07 | Decision 70: user → `Julian-B-Smith`; brand gets an org | PR #9 |
| 09-08 | Gist audit: a 2017 secret gist held four Twitter OAuth credentials; human deleted it | 3 gists remain, none with keys |
| 09-09 | Snapshot `rename_owner.py --check`: 45 remotes / 76 live / 49 record / 43 brand | `~/rename-before.txt` (re-run 09-10, identical) |
| 09-09 | Windows machine's first sweep merged (PRs #10, #11); one docstring held a literal 0x08 where `\b` was meant | PR #12 |
| 09-10 | Human renamed the account, registered the empty parking account, created org `mindlathe` | API: user `Julian-B-Smith` (created 2017 = same account); `Lifted-Truck` type User, 0 repos, created 09-10; `mindlathe` type Organization, 0 repos; old URL → 301 |
| 09-10 | `--apply --new-owner Julian-B-Smith`: 45 remotes rewritten; check reads 0 | `~/rename-after.txt` |
| 09-10 | Live refs in this repo + `algedonic.py` default org | PR #13, CI green under the new owner |
| 09-10 | Machine-local: `~/.claude/CLAUDE.md` pointer and its stale brand line | not tracked, by design |

## What was left alone, and why

Record files (DECISIONS, traces, research, integrations, LIBRARY, briefs, archive)
still read `Lifted-Truck`: true when written. `rename_owner.py --old-owner`
defaults to the old name because that mapping is the tool's job. 76 live
references across ~20 other repos are each resident's, at their next close, via
the runbook's relay line.

## Still open

- Windows machine: the same `--apply` when its agent wakes (SESSION.md handoff).
- plainsynth CI checks out `FOUNDATIONS` by the old owner (relay).
- Packages under the old name: unchecked (token scope); human's Settings → Packages.
- `gh auth status` labels the keyring login by the old name; cosmetic.
- A quiet week, then: parking account still empty, redirect still 301, check reads zero live.

## Lesson candidates

- A user and an organization cannot share a GitHub name: the account-vs-brand
  split has to be decided before the rename, not after (Decision 70's reason).
- "Secret" gists are unlisted, not private; a nine-year-old one carried live-shaped keys.
