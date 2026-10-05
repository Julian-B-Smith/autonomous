# Repo Hygiene: Leak Prevention for Agentic Coding Sessions

The canonical security-sweep spec. Deterministic scans, gates, and habits that
keep personal identity, paths, and secrets out of committed history. Slots into
the doctrine: AI proposes, deterministic gates decide; `./verify` is the oracle;
gates never weakened.

**What already implements this spec** (so this doc is the *why*, the code is the
*what*):
- **`./verify` `leak_gate`** (kit-core, every repo) — the Layer-0 CI-blocking
  identity gate. Pure `git grep` (POSIX, zero deps → present on every runner →
  cannot silently skip). Doctrine: "Never commit machine identity."
- **`governor/leak_scan.py`** — fleet privacy scan (identity + cross-repo
  private-name exposure). Kept byte-for-policy consistent with `leak_gate`.
- **`governor/monitor.py`** — rolls leak_scan + gate/CI/staleness into fleet
  STATUS. Caught a real regression (Tonality) in un-gated repos.
- **`.leakcheck-allow`** — per-repo allowlist for files that legitimately
  contain the patterns (security docs — this file is on it).
- **`governor/HISTORY-REMEDIATION.md`** — the leaked-history purge runbook.

---

## 1. Leak surface (what actually gets through)

Roughly in order of frequency:

1. **Absolute paths with usernames** — `/Users/<name>/...`, `/home/<name>/...`,
   `C:\Users\...`. Arrive via error messages, stack traces, and tool output
   copied into READMEs, `DECISIONS.md`, and `traces/`. Trace files are a prime
   vector: append-only records of sessions that saw full paths constantly.
2. **Binary files the text scanners can't see.** `git grep -I` (what `leak_gate`
   and `leak_scan` use) SKIPS binary files — so a path or username baked into a
   binary passes every text gate silently. Confirmed vectors: **`.pyc`**
   (CPython embeds the absolute source path in the bytecode header — a tracked
   `.pyc` leaked `/Users/<name>/...` into public history here, uncaught),
   **`.ipynb`** execution outputs (absolute paths, hostnames, sometimes data),
   **image EXIF / PDF author** fields (often the OS username). Defense is
   **prevention, not detection**: gitignore generated binaries; strip notebooks;
   check media metadata. A text scanner will never catch these.
3. **Secrets** — API keys, tokens, `.env`, private keys. Different failure
   mode: a leaked secret must be **rotated**, not just scrubbed.
4. **Git identity** — `git config user.email` stamps every commit.
   Use the GitHub noreply address globally:
   `git config --global user.email "<ID>+<username>@users.noreply.github.com"`
5. **Editor/tool droppings** — `.vscode/`, local `.claude/` state, `.DS_Store`,
   debug logs, coredumps, sourcemaps.

---

## 2. Deterministic scans

### 2a. Identity (the shipped gate — always available, fail-closed by nature)

The canonical check is `leak_gate` in every repo's `./verify`: `git grep` for
`/(Users|home)/[^/]+/`, the dash-encoded `-(Users|home)-<name>-` form Claude Code uses for session folders (kit 2.7.0), and the live `$USER`, honoring `.leakcheck-allow` and
filtering prose placeholders (`/Users/<user>/`, `$`, `%`, `@`, `{`). Pure git —
no tool to be missing, so it can never silently skip. Runs locally (Stop hook)
AND in CI. Fleet-wide: `governor/leak_scan.py` (+ cross-repo private-name check
with `--visibility`).

### 2b. Secrets (enhanced tier — real tools, FAIL CLOSED if absent)

Secrets need entropy + pattern tools grep can't replace:

```bash
gitleaks detect --source . -v              # scans full history by default
trufflehog git file://. --only-verified    # verifies keys are actually live
```

**Fail closed.** If a secrets scan is part of a gate, a MISSING scanner must
FAIL the gate, never skip — a gate that passes because it couldn't look is
indistinguishable from a clean pass, and that false confidence is worse than no
gate (this exact "silently matches nothing" trap has bitten this repo twice).
So: install the tool in CI, or make its absence a hard error. Do NOT
`command -v gitleaks || echo skipping`.

### 2c. Binary metadata (what the text scanners miss — §1.2)

```bash
exiftool <file>              # Author/Creator/GPS — strip with: exiftool -all= <file>
nbstripout --install         # per repo: strip .ipynb outputs at commit time
```
And **gitignore generated binaries** (`__pycache__/`, `*.pyc`, build dirs) — the
only reliable defense, since `git grep -I` can't read them.

### 2d. History, not just HEAD

A file scrubbed from HEAD is still in every clone. See
`governor/HISTORY-REMEDIATION.md` for the purge runbook — and its verdict:
usually DON'T (a rewrite can't un-expose what's already public), except unpushed
history. For **secrets**, rotate the credential unconditionally — the rewrite is
cosmetic.

---

## 3. The gates (three tiers, none sufficient alone)

### 3a. `./verify` leak_gate — Layer-0, CI-blocking (SHIPPED)

The identity gate is already `leak_gate` in the kit `./verify` (§2a). It is the
enforcement floor: deps-free so it runs unmodified on any runner, and blocks
both the Stop hook and CI. This is the one that must never be weakened or skip.

### 3b. Pre-commit hook — inner gate, staged content, local (opt-in enhancement)

Save as `.githooks/pre-commit`, then `git config core.hooksPath .githooks`. It
scans STAGED content (catches leaks before they enter history) and can run the
richer local tools (gitleaks on staged diff, `$USER`/hostname patterns rg can't
express in POSIX ERE). Hooks are advisory (skippable with `--no-verify`) — which
is exactly why the CI-blocking `leak_gate` (3a) is the real backstop, and any
secrets scan the hook runs still fails-closed on a missing tool (§2b).

### 3c. Pre-publication audit — phase gate, full history (private → public)

Before any repo goes public: fresh clone to a temp dir (audit what the world
would actually get), full-history identity scan, `gitleaks detect`, and a manual
eyeball of README / `DECISIONS.md` / `traces/` / CI configs / notebooks / media.
Record the audit in `DECISIONS.md` as the gate artifact. (This is also survey
Q + the pre-ship Prior-Art/IP re-scan's sibling — a deliberate disclosure gate.)

---

## 4. Habits (keep the input rate low)

1. **Never `git add -A` after an agentic session.** Highest-leverage habit.
   `git status`, then `git diff --staged`, then stage deliberately
   (`git add -p` when in doubt). Agents create scratch files, logs, and test
   output you didn't ask for — and a tracked `.pyc` (the binary leak in §1.2)
   is exactly what a blanket `add` ships. Doctrine "Self-documenting code" and
   this pair: stage what you understand.
2. **Global gitignore** (`~/.config/git/ignore`): `.env`, `.env.*`, `.DS_Store`,
   `*.pem`, `id_rsa*`, `id_ed25519*`, `*.key`, `.vscode/`, `__pycache__/`,
   `*.pyc`. Per-project: sanitize `traces/` at write time (keeps them
   committable) rather than letting session paths in.
3. **Commit identity:** noreply email globally; audit with
   `git log --format='%an %ae' | sort -u` per repo occasionally.
4. **Media check** before committing images/PDFs (§2c).

---

## 5. Mental model

| Layer | Knows | Catches | Fails how |
|---|---|---|---|
| `leak_gate` (git grep) | your `$USER` + abs-path shape | text identity leaks | can't (deps-free); blind to binaries |
| Secrets scanner | entropy + key patterns | keys, tokens | **must fail-closed if absent** |
| Binary/media check | file metadata | .pyc/EXIF/notebook leaks | needs prevention (gitignore), not scan |
| Human staged-diff review | context + intent | the categorically weird | skippable — hence the CI gate |

The gates are the oracle; the habits keep the input low; the pre-publication
audit is the disclosure gate. Passing ≠ done — done is green **plus** the
pre-publication checklist for anything going public.
