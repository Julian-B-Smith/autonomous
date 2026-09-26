# Boards routine — republish the Session Board and Threads Board on a cadence

> Canonical prompt for the `fleet-boards` scheduled task in the Claude desktop
> app on the primary machine (K5, Decision 76). The task's own stored prompt is
> one line pointing here, so this file is the single definition — the
> landscape audit's two-copies problem is not repeated. Local, not cloud: the
> boards show this machine's session registry and sibling repos' working
> trees, which neither a cloud routine nor a GitHub runner can see.

---

You are running the boards routine for the `autonomous` standards repo. It
needs no judgment: a script decides what changed; you publish what it names.
Do exactly the following and nothing else.

1. Run, from `~/Documents/Claude/autonomous`:

       python3 kit/session/boards.py --out "$TMPDIR/fleet-boards" --why routine

   It prints one line per board: name, verdict, page path, artifact URL.

2. For each line whose verdict is `CHANGED` and whose URL is not `-`:
   - Read the live artifact first (Artifact tool, `action: "read"`, that URL);
     a publish to an artifact this run has not read is refused.
   - Publish the page path with the Artifact tool, passing that URL as `url`.
     Omit `favicon` (the artifact keeps its own). Never pass `force`.
   - If the publish is refused because the page moved underneath you, read it
     again and publish once more. If it is refused a second time, stop and
     report it; do not retry further.
   - **Only after a publish succeeded**, confirm it:

         python3 kit/session/boards.py --out "$TMPDIR/fleet-boards" --confirm <board-name>

     Never confirm a board you did not publish. An unconfirmed board is simply
     offered again next run; a false confirm hides a stale page.

3. `UNCHANGED`, `NOT-PUBLISHER`, a URL of `-`, or an `ERROR:` verdict: publish
   nothing for that board.

4. Do not commit, pull, push, edit any file, open a PR, or touch any other
   repo. The script logs every run and every confirm to the session
   registry's `boards.log`; that log is the routine's whole footprint.

5. Finish with one line per board: its name, the verdict, and "published" or
   "not published" with the reason.
