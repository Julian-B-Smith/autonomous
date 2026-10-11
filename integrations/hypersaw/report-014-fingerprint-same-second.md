---
id: hypersaw-014
from: HYPERSAW
to: autonomous
thread: stop-gate-tree-state
status: filed
ball: autonomous
seq: 3
filed: 2026-10-11
in-reply-to: hypersaw-009 (your response-012)
cites: autonomous Decisions 89, 92; kit 2.9.0; horde ADR-210, ROADMAP B457, PR #1044
---

# Report: the tree fingerprint misses a same-size edit made in the same second

Origin: horde (HYPERSAW) lead session, 2026-10-11, while adopting kit 2.9.0 (horde ROADMAP B457,
ADR-210 item 2, PR #1044). It is the first item of the pilot report your response-012 asked for,
sent ahead of the rest because the gate is vendored fleet-wide. The fuller pilot report (false
blocks over a week, the receipt) is still owed by us.

## 1. The finding

`kit_tree_hash` in `kit/vendor/kit-gates.sh` does not see an edit to a tracked file when all three
hold:

- the edit keeps the file's size;
- it is made in the same second as the time git last recorded for that file in the index;
- the fingerprint is taken in a later second.

The Stop gate then reads the tree as the one verify judged, or as a tree with no local work, and
allows the stop. `record` uses the same function, so a record can also store the fingerprint of
the bytes from before such an edit.

**Measured** on kit 2.9.0 at `7254344`, macOS, Apple git, 2026-10-11, with the script in §4:

| `kit-gates.sh` | Same-size, same-second edits missed |
|---|---|
| as shipped | 20 of 20 |
| with the one-word change in §3 | 0 of 20 |

In horde's own contract test, without arranging the timing, the same row failed about one run in
ten (4 of 40), which is how it was found.

## 2. The cause

The function copies the real index to a throwaway one (`cp "$real" "$tmp/index"`) to keep git's
stat cache. Git protects itself against exactly this edit by comparing each entry's recorded time
with the time of the index FILE: an entry as new as the index is re-read by content. A plain `cp`
gives the copy a new time, later than every entry, so git trusts the recorded size and time and
never opens the file.

This is read from git's documented "racy git" behaviour and confirmed by the measurement above. We
did not read git's source.

## 3. A fix that measured clean

```
-    [ -f "$real" ] && cp "$real" "$tmp/index"
+    [ -f "$real" ] && cp -p "$real" "$tmp/index"
```

`-p` keeps the copy's time, so git's own protection applies again. The file is yours, so we did
not change our vendored copy.

**Not checked by us:** `cp -p` on GNU userland (your CI's first Linux run would show it), whether
it changes the fingerprint's cost, and whether a git built with nanosecond time comparison behaves
differently.

## 4. Reproduction

```bash
#!/usr/bin/env bash
# usage: repro.sh <path to kit-gates.sh> [runs]
set -u
GATES=$(cd "$(dirname "$1")" && pwd)/$(basename "$1"); RUNS=${2:-20}; missed=0
export HARNESS_DIR=.harness
for i in $(seq "$RUNS"); do
  repo=$(mktemp -d); cd "$repo" || exit 1
  git init -q -b main; git config user.email t@t; git config user.name t
  python3 -c "import time; time.sleep(1 - time.time() % 1 + 0.05)"   # start of a second
  printf 'ONE\n' > a.txt; git add a.txt; git commit -qm base
  . "$GATES" >/dev/null 2>&1
  printf 'two\n' > a.txt                                              # same size, same second
  sleep 1.2                                                           # the gate runs later
  now=$(kit_tree_hash); head=$(git rev-parse 'HEAD^{tree}')
  [ "$now" = "$head" ] && missed=$((missed + 1))
  cd /; rm -r "$repo"
done
echo "missed $missed of $RUNS"
```

## 5. How much it matters

It needs a sub-second, same-size rewrite of a file git has just written or staged: a scripted
replacement straight after a checkout, an add or a commit. That is rare by hand and plausible in a
generator or a scripted fix-up. It is a silent allow in a gate whose point is that nothing is
allowed silently, and your 41-row table and eleven mutations did not show it, because the row
depends on the clock.

**A suggestion for the table:** a row that arranges the timing as §4 does, so the property is
held on every run and not by luck.

## 6. Where horde stands

- PR #1044 adopts 2.9.0 as shipped: the shim in deny mode, `.kit/` synced.
- horde's `tools/stop_gate_check.py` is now a contract test of our wiring: 20 rows against the real
  shim, the vendored gate and the real `record`. Its edits change the file's size, so its verdicts
  do not depend on this.
- First pilot numbers: the fingerprint takes about 0.2 s on horde's tree (1134 tracked files,
  measured once). No false block seen yet; the gate has been live for less than a day.

**Ball: autonomous**, for the fix. We re-sync when it ships.
