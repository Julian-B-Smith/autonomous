# Installing the doctrine on a machine

How to wire a machine's global `~/.claude/CLAUDE.md` to this repo's canonical
doctrine. First installed 2026-07-10. Replicate on any other
machine in two steps.

## 1. Clone the repo to the same path

```bash
git clone https://github.com/Julian-B-Smith/autonomous.git ~/Documents/Claude/autonomous
```

The `@` imports below use this absolute location. If you must clone elsewhere,
adjust the import paths to match.

To bring the **rest of the roster** across, run the generated plan from inside
that clone — it reproduces the nested layout (`synthetic-worlds/Orrery`, not a
flattened `Orrery`) that the registry and every cross-repo path assume, and it
names the repos no clone can reach rather than letting them disappear quietly:

```bash
./kit/clone-roster.sh          # print the plan; --run to execute
```

## 2. Add this block to `~/.claude/CLAUDE.md`

Paste verbatim (this is exactly the block installed on the first machine).
Put it at the top, before any machine-local sections:

```markdown
## Canonical infrastructure (single source)

All cross-project doctrine, the harness kit, memory loops, and the governor
live in **`~/Documents/Claude/autonomous/`** (github.com/Julian-B-Smith/autonomous).
That repo is the canonical home; propose doctrine changes there (versioned,
reviewable), never by editing this file. The doctrine below is imported and
auto-loaded every session. (INTEGRATIONS.md is deliberately NOT auto-loaded —
context budget; its doctrine tenet says to read it at the start of any
cross-repo work.)

@~/Documents/Claude/autonomous/doctrine/DOCTRINE.md
```

## 3. Install the commands

```bash
mkdir -p ~/.claude/commands
cp ~/Documents/Claude/autonomous/kit/commands/*.md ~/.claude/commands/
```

Canonical copies: `kit/commands/` (re-copy after pulling changes). Gives
every session `/spinup [path —] <what it is>` (survey-first NEW-project
procedure) and `/retrofit [path]` (gap-survey catch-up for EXISTING repos);
with no path both target the current working directory (the Claude Code
Desktop open-in-folder case).

## 4. Verify

Start a fresh Claude Code session anywhere and ask what the development
doctrine says about (e.g.) the AI/deterministic boundary. If the answer
reflects [DOCTRINE.md](DOCTRINE.md), the imports resolved.

## 5. Keeping an ALREADY-INSTALLED machine current

`git pull` on this repo propagates doctrine automatically (the `@import`
reads the pulled file). The ONE thing a pull cannot update is the pasted
block in your machine-local `~/.claude/CLAUDE.md` itself. When the block
changes here, re-paste §2 on each installed machine. Block changelog:

- **2026-07-16** — INTEGRATIONS.md removed from the auto-load imports
  (context budget, Decision 28). If your global file still contains
  `@…/doctrine/INTEGRATIONS.md`, delete that line and replace the paragraph
  above the import with §2's current text.
- 2026-07-10 — initial block.

## 6. Windows machines (read BEFORE the first clone)

Everything above applies, with seven differences. Most of them fail *silently*
if skipped — that is why this section exists.

**a. Set line endings before cloning anything.** Git for Windows defaults to
`core.autocrlf=true`, rewriting checkouts to CRLF. Identical content then has
different bytes on the two machines, breaking every byte-comparison gate here
(`content_hash`, hash ledgers, golden renders) for reasons unrelated to the
change under test — and a CRLF shebang makes `./verify` die with a bare
"command not found". Repos carrying a `.gitattributes` are protected; this
covers the ones that don't:

```bash
git config --global core.autocrlf input
```

**b. Run the harness from Git Bash, not PowerShell or cmd.** Every `./verify`
is `#!/usr/bin/env bash` and shells out to `git grep`/`sed`. Git Bash (bundled
with Git for Windows) runs them unmodified; WSL also works. PowerShell does
not, and the failure looks like a broken repo rather than a wrong shell.

**c. `python3` may not exist — and the stub that does is worse than nothing.**
The verify scripts and every kit hook invoke `python3`; Windows installs
provide only `python` / the `py` launcher, and the `python3.exe` under
`%LOCALAPPDATA%\Microsoft\WindowsApps` is a Microsoft Store *alias* that
prints "Python was not found" and exits non-zero. So every Python gate reads
RED with a message that looks like a broken repo (autonomous, 2026-09-09: sweep, governor, kit
gate and currency tests all red on a clean tree). Fix: copy `python.exe` to
`python3.exe` inside the real install dir (`…\Programs\Python\Python3xx\`),
which sits ahead of `WindowsApps` on PATH. Confirm `python3 --version` in Git
Bash before concluding a gate is broken.

**d. Clone to the same relative layout.** The doctrine import is
`@~/Documents/Claude/autonomous/doctrine/DOCTRINE.md`. Claude Code expands `~`
to `C:\Users\<you>`, so cloning into `Documents\Claude\` under your home
directory makes the import resolve unchanged. Cloning elsewhere means editing
the import path in §2.

**e. Windows-shaped identity leaks are now gated too.** The `leak_gate` and
`leak_scan` catch the drive-letter home path in both its raw and
backslash-escaped forms, alongside the POSIX one. A leak committed from the
Windows machine fails CI exactly like a leak committed from the Mac — but
`auval`, AU builds, and the Mac-only plugin steps in the global file's
audio-plugin section do not exist there; on Windows those projects are VST3
only.

**f. Set `PYTHONUTF8=1` (user environment variable).** The Windows console
encoding is cp1252, so `monitor.py` dies encoding the `→` in its own summary
line and `subprocess` dies decoding UTF-8 output from `git grep`. `setx
PYTHONUTF8 1`, and add it to `~/.claude/settings.json` `env` so hooks inherit
it. Without it the sweep crashes after ~14s having written a partial STATUS.

**g. Hooks and the session registry.** `~/.claude/settings.json` carries the
kit's SessionStart hooks (`kit/hooks/session-brief.py` sync,
`kit/hooks/fleet-sweep-async.sh` async) with absolute forward-slash paths, and
`KIT_SESSION_MACHINE=win` in its `env` block so registry rows never carry the
hostname. The registry fallback dir `~/.claude/session-registry/` must exist
or `/wakeup` proceeds unregistered with a warning.

## Rules of the split

- **"Update the global CLAUDE.md" ≈ "put it somewhere synced."** When the
  human asks to add a standing rule/fact to the global instructions, they
  almost always mean it should reach every machine — so it belongs in THIS
  repo (a doctrine file the global CLAUDE.md imports or points at), not in the
  machine-local sections of `~/.claude/CLAUDE.md`. Default to the synced home;
  only genuinely machine-specific facts (a toolchain quirk of one Mac) stay
  local.
- **This repo owns**: portable doctrine, the integrations policy, everything
  a second machine should inherit identically.
- **The global file owns**: machine-local facts only (build quirks, local
  install paths, hardware-specific gotchas). Those sections differ per
  machine by design and are never synced.
- **Never edit doctrine in the global file** — the imports make any doctrine
  text there redundant, and redundant copies drift. Doctrine changes are
  commits to this repo; `git pull` propagates them to every machine.
