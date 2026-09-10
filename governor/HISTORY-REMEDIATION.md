# History remediation runbook — purging leaked strings from git history

> Prepared 2026-07-13 after `leak_scan` found machine-absolute paths in five
> repos. HEAD is now clean everywhere (0 HIGH); this runbook is about the
> **history behind HEAD**, which still contains the old blobs.
>
> **Read the decision section first. The honest answer for most of these repos
> is "don't."** Rewriting history is never truly non-destructive; the goal is
> to make it *safe and reversible*, and to only pay that cost where it buys
> something real.

## 1. Decide per repo — is it worth it?

What is actually exposed in history: a **macOS username** and a **directory
layout** (`/Users/<user>/Documents/…`). What is NOT exposed: no credentials,
no tokens, no keys, no source that wasn't already public. Severity: **low
information-disclosure, not a security vulnerability.**

Rewrite only if ALL of these hold:
- the repo is **public** (private history is seen by no one but you), AND
- the leak is **genuinely sensitive** (a real secret, a client name, a private
  project's existence) — not just a username, AND
- you accept the cost below.

| repo | history state | verdict |
|---|---|---|
| **dispatch** | bad blobs exist but are **UNPUSHED** (`origin/main` is behind them) | **Rewrite — free.** No force-push, no coordination, nothing public. Just fix local history before the next push. Do this one. |
| **Tonality** | public; venv paths in history for months | Judgment call. Username only → low value, real cost. Default: **skip**. |
| tonality-Live, automata, terrane, wont | same class, lower profile | **Skip.** |

**The asymmetry that should decide it:** a rewrite does NOT un-expose anything
already public — clones, forks, GitHub's cached views, and any archiver keep
the old objects. You are reducing *future* discoverability of a username, not
recovering secrecy. That is worth very little; the cost is real.

## 2. The cost (say it out loud before starting)

- **Every commit SHA after the first rewritten commit changes.** Permanently.
- **Force-push required** for anything already pushed.
- **Every other clone must re-clone or hard-reset** — including your second
  machine. A stale clone that then pushes will *reintroduce the old history*.
- Links to specific commits (in DECISIONS, traces, issues) go dead.
- GitHub may retain unreferenced objects and cached views; forks keep theirs.

## 3. The safe procedure (if you decide yes)

Uses `git-filter-repo` (the maintained successor to `filter-branch`;
`brew install git-filter-repo`). `--replace-text` is the surgical option: it
rewrites the *string* inside blobs and leaves structure/messages intact.

```bash
# 0. BACK UP FIRST — a full mirror you can restore from. Non-negotiable.
git clone --mirror https://github.com/Julian-B-Smith/<repo> ~/backups/<repo>-$(date +%F).git

# 1. Fresh clone to operate on (filter-repo refuses a dirty/linked tree)
git clone https://github.com/Julian-B-Smith/<repo> /tmp/<repo>-rw && cd /tmp/<repo>-rw

# 2. Define the replacements (literal string -> replacement).
#    Build it from $(whoami) so this runbook never itself contains the
#    username — the leak_gate would (correctly) reject it if it did.
#    That is not a cute detail: the first draft of this file DID hardcode it
#    and CI caught it. See §6.
printf '/Users/%s/Documents==>~/Documents\n' "$(whoami)" > /tmp/replacements.txt

# 3. Rewrite (rewrites ALL commits touching those blobs)
git filter-repo --replace-text /tmp/replacements.txt

# 4. VERIFY before pushing — the string must be gone from all history
git log --all -p | grep -c "$(whoami)" || echo "clean"
git log --oneline | head            # sanity: history structure intact

# 5. Re-add the remote (filter-repo strips it deliberately) and force-push
git remote add origin https://github.com/Julian-B-Smith/<repo>
git push --force --all && git push --force --tags

# 6. On EVERY other machine: re-clone (do NOT merge a stale clone)
#    rm -rf <old> && git clone <url>
```

**Rollback:** restore from the step-0 mirror (`git push --mirror` from the
backup). This is why step 0 is non-negotiable.

## 4. The nondestructive alternatives (prefer these)

- **Do nothing.** HEAD is clean; the gate prevents recurrence. For a username,
  this is the proportionate response.
- **Rename the leak, not the history.** If the concern is the *username*
  specifically, a macOS account rename is orthogonal and doesn't touch git.
- **Fresh-start a repo** (new repo, squashed initial commit, archive the old
  private) — appropriate only if history has no value.
- **For unpushed history (dispatch): rewrite freely.** No force-push, no
  coordination, no public exposure. This is the one genuinely free case.

## 5. Prevention is already in place (that's the real fix)

- `leak_gate` in every project's `./verify` — blocks the Stop hook AND CI, so
  a new leak can't be committed.
- `governor/leak_scan.py` — fleet backstop for un-gated repos + cross-repo
  private-name exposure.
- Doctrine: "Never commit machine identity."

A leak that never lands needs no history surgery. The gate is worth more than
any rewrite.
