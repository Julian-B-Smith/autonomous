# REFLECTIONS

Open questions, half-thoughts, and things to hold between sessions. Distinct
from DECISIONS.md (settled calls) and LIBRARY.md (verified lessons). Pruned
every `/wakeup`: each entry graduates, stays with a note, or is dropped.
Entries unaddressed for 14+ days are flagged graduate-or-drop — a reflection
log that only grows is where thoughts go to die.

Format: `- [YYYY-MM-DD] text`

- [2026-09-09] The two machines share NOTHING gitignored yet: this box has a
  fresh, empty `~/.claude/session-registry/` (so the Mac's open rows —
  mind-lathe since 08-28 — are invisible here), no `BOARD_URL`/`THREADS_URL`,
  no `audit-loop.config`. ROADMAP K3 still waits on the human naming
  `KIT_SESSION_REGISTRY`. Until then every "still open" report is per-machine
  and the boards publish from one machine only. Forget-risk of the week.
- [2026-09-09] The rename happens while nobody is watching. GitHub redirects
  old-owner URLs, so pulls keep working — but `algedonic.py`'s default org,
  plainsynth's cross-repo CI, and this repo's 14 live references (README §7,
  ROADMAP registry lines, INSTALL-GLOBAL §1) are LIVE references, not records,
  and read wrong the moment the rename lands. `kit/rename_owner.py --check`
  is the first command on return; `--apply --new-owner Julian-B-Smith`
  rewrites remotes on each machine separately.
- [2026-09-09] `jq` is absent here, so `kit/hooks/pr-status.sh` was not wired;
  the PR-state observer is Mac-only until it is installed. Also: the
  `CITES MISSING` report is 79 lines on every verify run — correct, but it
  buries the one line that matters; T4 is the fix, not a filter.
