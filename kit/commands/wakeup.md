---
description: Open a working session — read state, prune the reflection log, register the session. Writes: registry row, confirmed graduations, reflection prunes.
---

Open a session in this repo: $ARGUMENTS

## Step 1 — read the state (shared routine)

```
python3 ~/Documents/Claude/autonomous/kit/session/state.py .
python3 ~/Documents/Claude/autonomous/kit/session/registry.py list
```

## Step 2 — check for an unclean shutdown BEFORE opening

If the registry holds a row for THIS repo that is not this session, the last
session never closed. **Never silently overwrite it** — a row nobody closed
means a session nobody finished, and that is information, not noise. Offer, in
this order: re-render the state (`/reorient`), then an abbreviated `/breakdown`
that writes SESSION.md and closes the stale row, and only then open.

## Step 3 — render the state summary

Where the project is, what changed last session, verify status (a recorded
result from a different commit says nothing about HEAD), what is ready to work
on. Same shape as `/reorient`.

## Step 4 — prune REFLECTIONS.md

Each entry: **graduate** (to DECISIONS.md, ROADMAP.md, LIBRARY.md — if it
clears the evidence+falsifier gate — or an issue), **stay**
with a note, or **drop**. Propose all three sets; the human confirms. Entries
unaddressed for 14+ days are flagged by the state routine — those are
graduate-or-drop, not stay, because a reflection log that only grows is a
place thoughts go to die.

## Step 4b — routine audit, if this repo has one and its last report is stale

If the repo declares an auditor (`.claude/agents/auditor.md`, or
`"auditor": {"agent": "auditor", "cadence_days": 7}` in `project.manifest.json`)
and the state summary reads `last audit: … STALE` or `last audit: none`,
dispatch that agent **in the background** now and say so in the summary. It
is read-only over the tree, writes only its report under `docs/audits/` on
its own branch as its own PR, never edits code, never weakens a gate; the
lead turns findings into ROADMAP rows at the next boundary. A repo with no
auditor skips this step silently. Cadence is by STALENESS, not calendar: a
repo worked daily audits weekly, a repo touched monthly audits on touch —
one rule, no schedule to maintain (hypersaw-003; horde's first run found 13
regression checks built, green, and never wired into `./verify`, debt no
oracle sees because nothing was weakened). `/wakeup`'s permitted writes are
unchanged.

## Step 5 — survey ONLY if genuinely ambiguous

Multiple ready threads, a stale or contradicted plan, a red verify, or an
unresolved reflection blocking the obvious move. Otherwise **state the assumed
starting point and proceed**. A survey that fires every time gets skipped every
time, and then it is not a gate, it is a habit.

## Step 6 — register the session

```
python3 ~/Documents/Claude/autonomous/kit/session/registry.py open . --session-id <id>
```

Use a stable id for this session. If the registry is unconfigured or
unreachable, **proceed with a warning** — a session never blocks on
bookkeeping.

## Permitted writes

Registry row; REFLECTIONS.md prune edits; graduation targets the human
confirmed. Nothing else. In particular `/wakeup` does not commit project work.

## Last — republish the boards (the standards repo's session ONLY)

Two boards, one publisher. **Only a session running in `autonomous` publishes**
— two sessions racing on one artifact made every boundary a publish conflict,
and clearing one costs a full page re-read (three in a row, 2026-09-02). Every
other session still writes the registry and the mailbox; the boards catch up at
the publisher's next boundary. The renderer enforces this: from any other repo
it prints `NOT-PUBLISHER` and writes nothing, so there is nothing to remember.

```
python3 ~/Documents/Claude/autonomous/kit/session/boards.py --out "$TMPDIR/fleet-boards" --why wakeup
```

It prints one line per board: name, verdict, page path, artifact URL. For each
`CHANGED` line with a URL, read the live artifact, then publish the page path
with the Artifact tool passing that URL as `url` (Session Board 🕐, Threads
Board 📬 — omit `favicon` on a republish), and only after it succeeded run the
same command with `--confirm <board-name>` in place of `--why`. `UNCHANGED`,
`NOT-PUBLISHER`, or a
URL of `-` → publish nothing. The script ignores each page's own clock, so an
unchanged board is never republished just because time passed. If a publish is
refused because the page moved underneath you, re-read and publish once; do not
force. Boards are optional bookkeeping and a session never blocks on them.

Between sessions the same script runs on a cadence as the `fleet-boards`
scheduled task (`routines/boards.prompt.md`, K5), so a thread filed by another
repo reaches the Threads Board within one tick even when no session here opens.
