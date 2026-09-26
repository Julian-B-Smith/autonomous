---
description: Ecosystem-level /breakdown — triage every repo, close the ones that can be closed honestly, and hand back the ones that need a human. For when per-repo close is untenable.
---

Close out the fleet: $ARGUMENTS

**Use this when per-repo `/breakdown` is untenable** — 39 repos is not an
evening. It is NOT a replacement for `/breakdown`; it is the subset of it that
can be done without a human in the room, plus an honest list of what cannot.

## Step 1 — triage, read-only

```
python3 ~/Documents/Claude/autonomous/kit/session/batch_close.py
```

Three buckets, and the split is the whole design:

- **mechanical** — nothing outstanding that only that repo's session could
  explain: kit-owned edits (`.kit/`, `project.manifest.json`), and/or a branch
  whose work is already committed. Closeable from here.
- **needs-session** — its OWN uncommitted source, or a red oracle at HEAD.
  Only its session knows what that work is, and a red verify is a finding to
  surface, not something to sweep past.
- **clean** — nothing to close.

Show the human all three counts and every `needs-session` row WITH its reason.
The refused list is the more useful half of the output.

## Step 2 — what a mechanical close actually does

For each mechanical repo: writes `SESSION.md`, stages only its own artifacts,
commits, pushes a branch, opens a PR. **Never merges.**

The `SESSION.md` it writes is stamped `closed: mechanical` and states in its
own text that no survey was taken and that it is a state snapshot, not a
handoff. **This is the constraint the whole command is built around.**
`SESSION.md` is "the only prior-session context the next session trusts"
(brief §2), and three of `/breakdown`'s six steps need a human — what today
decided, the thread you would forget, the first move next session. A batch
cannot answer those, so it must not produce a file that looks like it did.
A poisoned handoff is worse than an open session.

## Step 3 — apply, with approval

```
python3 ~/Documents/Claude/autonomous/kit/session/batch_close.py --apply
```

This writes into repos this session does not reside in, so it is a sanctioned
batch like `kit_sync --all`: dry by default, `--apply` required, and the human
approves the triage first. Report every PR opened and every repo refused.

## Step 4 — hand back what you could not close

List the `needs-session` repos and say, per repo, what is in flight. Those get
a real `/breakdown` in their own session — that is where the three questions
get answered and a genuine `SESSION.md` gets written.

## Notes

- A repo whose stranded commits sit on `main` gets a branch at HEAD, so the PR
  proposes them. **Local `main` still points at those commits** — after the PR
  merges, that repo may want `git switch main && git reset --hard origin/main`.
  That reset is destructive and is the human's, never this command's.
- A red oracle is never hidden and never closed past.
- Deregistering: if the session registry holds rows for closed repos, remove
  them with `registry.py close --session-id <id>` and report what remains open.

## Last — republish the boards (the standards repo's session ONLY)

Two boards, one publisher. **Only a session running in `autonomous` publishes**
— two sessions racing on one artifact made every boundary a publish conflict,
and clearing one costs a full page re-read (three in a row, 2026-09-02). Every
other session still writes the registry and the mailbox; the boards catch up at
the publisher's next boundary. The renderer enforces this: from any other repo
it prints `NOT-PUBLISHER` and writes nothing, so there is nothing to remember.

```
python3 ~/Documents/Claude/autonomous/kit/session/boards.py --out "$TMPDIR/fleet-boards" --why closeout
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
