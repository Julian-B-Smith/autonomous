# Trace — the second machine comes up, and the governor learns it had a home

**Arc:** 2026-09-09 · 1 PR (#10, merged) · Decision 71 · LIBRARY L0018
**Closed by:** `/breakdown`, abbreviated — the human answered the survey in
prose before leaving for a week.

## What changed, in one line

The governor and kit stopped depending on the machine that wrote them.

## The through-line

Every kit tool was written on the Mac and had never run anywhere else. On the
Windows machine the same tree, at the same commit, read differently in five
places — and four of the five failed *silently*, which is the shape this repo
exists to catch:

1. `python3` resolved to the Microsoft Store stub → every Python gate red with
   a message that looked like a broken repo, not a missing interpreter.
2. cp1252 console → `monitor.py` crashed on the `→` in its own summary line,
   after writing a partial STATUS.
3. `leak_scan`'s username pattern was a bare substring; the Windows username
   is inside "transport" and "support" → **20 HIGH** across 54 repos, every
   one false, one of them here. The vendored `leak_gate` (path shapes only)
   stayed green — two detectors, two policies, found the way the gotcha list
   predicts.
4. `ball_scan` emitted `os.path.relpath` verbatim → backslash file keys, two
   tests red on a clean tree.
5. Every gate-fires probe ran `["./verify","fast"]` as a direct subprocess.
   Windows cannot exec a bash script; the OSError was caught as "gate did not
   fire" — a dead *process*, one level above L0002's dead *pattern*.

Fixes: `username_pattern()` anchored in POSIX ERE + `test_leak_scan.py`
(planted known-bad, near-miss, ERE-safety); `ball_scan._rel()`;
`currency.verify_cmd()` at six sites; one stated platform skip;
INSTALL-GLOBAL §6 c/f/g. Sweep after: **2 HIGH**, both in other repos'
territory (life-os-app, life-os-data), reported and not touched.

## Machine setup that lives outside the repo (Osiris)

`python3.exe` copy in the 3.12 install dir · `PYTHONUTF8=1` (user env +
settings `env`) · `core.autocrlf input` · global CLAUDE.md block + machine-
local section · `~/.claude/commands/` · SessionStart hooks (brief sync, sweep
async) · `KIT_SESSION_MACHINE=win` · `~/.claude/session-registry/` (empty,
per-machine). Not installed: `jq`, so the PR-status hook is off here.

## What is deliberately NOT done

- No kit version bump (Decision 68, weekly batch).
- No board publish — no `*_URL` files on this machine.
- The README's "46 repos" figure was not re-verified this close; the registry
  resolves 54 paths, and the 46 is the kit-scaffolded subset from 08-31.
