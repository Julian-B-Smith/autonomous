---
description: Bring an EXISTING repo to the current kit version — a CHANGELOG-driven migration (currency check → gap plan → pause → append-only apply → declare), idempotent by construction
---

Retrofit this existing project: $ARGUMENTS

(Arguments — both optional: a target directory and a one-line description.
**If no directory is given, the target is the current working directory.**
Sanity-check the opposite of /spinup: the target SHOULD be an existing
project with real content; if it looks empty/greenfield, suggest /spinup
instead and stop.)

## Step 0 — currency, deterministically, before you read anything else

Run the kit's currency checker FIRST and paste its output into your first
message. It is the only source of truth for *what this retrofit is for*:

    python3 ~/Documents/Claude/autonomous/kit/currency.py <target>

It prints the kit version, the repo's DECLARED `kit_version` (absence reads
as `pre-2.0.0` — never as current), and the ordered list of CHANGELOG entries
the repo is behind, each with a presence check per requirement. Three
outcomes, and they decide the whole session:

- **CURRENT, nothing to do** → say so and STOP. Re-running the retrofit on a
  current repo is a no-op by construction. Do not "improve" anything.
- **CURRENT but `declares X but is missing: …`** → the declaration is false.
  That is drift, and it is louder than being behind: restore the missing
  items (append-only, per step 4) or, if they were removed deliberately,
  lower the declaration and record why in DECISIONS. Never leave a false
  declaration standing.
- **BEHIND by N entries** → the entries, in order, ARE the plan. Every
  `[ ]` is a gap to close; every `[x]` is done and MUST NOT be touched.
  Read `~/Documents/Claude/autonomous/kit/CHANGELOG.md` for each entry's
  **retrofit action** — that text is what you apply.

Then follow the canonical procedure at
`~/Documents/Claude/autonomous/ONBOARDING.md` → Part 2 → "Retrofitting an
EXISTING project" — all five steps, exactly, with the currency delta as the
gap table. Five behaviors are non-negotiable and unchanged:

1. **Infer before asking.** Gap-survey the repo read-only first; propose
   survey answers derived from the code and ask only what code cannot show
   (the architecture rung is still asked, never defaulted). What you do ask,
   you ask as a poll — inferred answer as the recommended option, evidence
   in its description (`kit/prompts/_human-gates.md`).
2. **Plan, then pause for approval before writing anything.** An existing
   repo is working state; list every create-vs-modify up front, keyed to
   the CHANGELOG entry that requires it. The pause is a poll (Proceed /
   Proceed except… / Stop), not a paragraph ending in a question mark.
3. **Append, never rewrite.** Marker-delimited insertions only; existing
   content wins conflicts pending a human ruling; re-running must be a
   no-op — and now that is CHECKED, not hoped: run `currency.py` again at
   the end and it must print `nothing to do`.
4. **Never break what works — or hide what doesn't.** `./verify` wraps the
   existing test/lint commands; currently-red tests are quarantined and
   recorded in ROADMAP as explicit debt, never deleted, never silently
   gated on, never "fixed" by weakening.
5. **Foreign/exported scaffolds: standard mechanisms, project substance**
   (the override clause — full text in ONBOARDING). Where a chat-exported kit
   overlaps the ecosystem kit, the kit's MECHANISMS replace the exported ones
   (verify, charter layout, ROADMAP/DECISIONS, loop, hooks, CI); the exported
   kit's project-specific SUBSTANCE is migrated into standard slots (§Domain,
   ROADMAP, DECISIONS, LIBRARY seeds, bespoke checks → verify targets) BEFORE
   anything is deleted. Unmappable content is surfaced to the human, never
   silently discarded. Map first, replace second, delete only what's mapped.

## Step 4b — vendor the kit-owned gates (kit >= 2.4.0)

Gate code is NEVER copied into a repo. Run:

    python3 ~/Documents/Claude/autonomous/kit/kit_sync.py <target>
    python3 ~/Documents/Claude/autonomous/kit/migrate_to_vendored.py <target> --apply

The first writes `.kit/kit-gates.sh` + `.kit/MANIFEST` (sha256-pinned); the
second thins `./verify` to source them. If the migrator REFUSES, wire
`. .kit/kit-gates.sh` by hand per `kit/templates/verify.project` and keep every
project gate — refusal means it will not guess at your oracle, which is right.

Then prove all three, because they come apart: `./verify fast` is green, the
verify actually SOURCES `.kit/kit-gates.sh` (a checksum-perfect copy nothing
sources leaves the repo ungated — three repos read `current` while completely
unprotected), and the gate FIRES on a planted identity path.

## Step 4b′ — permissions: does `.claude/settings.json` still deny your own push?

Repos scaffolded before kit 2.6.1 (2026-09-17) carry `"Bash(git push*)"` in
`permissions.deny`, which contradicts Decision 66 and makes Step 6's PR
impossible without a human relay. Check now, before you need it:

    grep -n '"Bash(git push\*)"' .claude/settings.json

A hit is the old template. Poll the human (`_human-gates.md` §2): adopt the
2.6.1 `permissions` block from `autonomous/harness/.claude/settings.json`
(merge, keeping any project-specific entries), relay-once, or leave it. Do
not discover this at the push and stall the close.

## Step 4c — TIDY THE TREE YOU FOUND. Do not report it; resolve it.

A retrofit inherits whatever state the repo is in, and the human should not be
the one reconciling it. Before declaring, deal with everything loose:

- **Uncommitted work that belongs to the kit** — a `.kit/` synced by the
  standards repo, a `verify` patched by a batch, a `.gitattributes` written
  and never staged: `git add` it and carry it in this PR. It is the same
  change you are making.
- **Uncommitted work that is the PROJECT'S** — someone's half-finished
  feature: leave it alone, do not stage it, and name it in your report so the
  human knows it is there. Yours to notice, not to absorb.
- **Untracked `.kit/`** — `git add .kit`. An untracked vendored gate reaches
  no clone and no CI, so the repo is ungated everywhere but this disk
  (kit 2.5.1).
- **Commits sitting on `main` unpushed** — move them onto your branch so they
  ride this PR rather than waiting for someone to find them.
- **Stray probe plants** (`.kit-currency-plant-*`) — delete them. They are
  another session's litter, untracked and unignored, and one `git add -A`
  from committing identity paths the gate ignores by design.

Report what you tidied in the PR body. The rule: after your PR, `git status`
in that repo should be clean except for work that is genuinely someone else's
in progress.

## Step 5 — declare, then prove the declaration

**There is no longer a "declare it and you're done" case.** Since kit 2.6.0
currency is COMPUTED from the tree: a version is behind only when one of its
requirements is actually unmet, so if `currency.py` says BEHIND there is real
work, and when the work is done the repo reads CURRENT with nothing to write.
(Before 2.6.0 a repo could be BEHIND purely because a string in its manifest
was stale — that cost 24 repos a needless second retrofit in one day.)

Close every `[ ]` in the delta, then run `currency.py` once more: it must say
CURRENT. If it does not, the retrofit is not done, whatever the diff looks
like — the checker reads the tree, not your summary of it.

Write `"kit_version": "<kit version>"` into `project.manifest.json` as you
close. Since 2.6.0 that field is **provenance, not a gate** — "last
deliberately retrofitted at X", the one fact the tree cannot tell you. Being
current no longer depends on it, and a stale one costs nothing, so never
spend a session on it alone.

## Gotchas (each cost a real run)

- The Write tool does NOT set the exec bit: `chmod +x verify
  .claude/hooks/*.sh` or the oracle fails `permission denied` and — worse —
  `currency.py` correctly reports `./verify` as missing (it checks
  executability, not existence).
- `git grep -E` is POSIX ERE — no `\s`, `\d`, `\b` in any gate you write.
  Plant a known-bad line and watch the gate fire before you trust it
  (autonomous LIBRARY L0002).
- Every gate asserts the EFFECTIVE state, never the declared one (kit
  README, gate rule). The retrofit's own closing check is an instance:
  `currency.py` reads the tree, not your summary of it.

## Step 6 — notify autonomous, so it verifies NOW rather than next sweep

The standards repo verifies a retrofit by RE-READING the repo (`currency.py`),
never by trusting a report. So this notice is not a claim of completion — it
is a request that the effective-state check run now. Two channels, both:

1. **File it** (works whether or not an autonomous session is live — the
   protocol's own channel). Write, under the mailbox exception, to
   `~/Documents/Claude/autonomous/integrations/<this-repo>/retrofit-<kit-version>.md`:

   ```
   ---
   id: <this-repo>-retrofit-<kit-version>
   from: <this-repo>
   to: autonomous
   status: filed
   ball: provider
   filed: <YYYY-MM-DD>
   re: retrofit to kit <kit-version> — please verify against the tree
   ---
   Retrofit to <kit-version> complete. currency.py output at close:

   <paste the final currency output — must read CURRENT / nothing to do.
   autonomous is PUBLIC: the path must read `~/…`, never an absolute home
   path. kit >=2.2.3 renders it that way; if yours prints an absolute path,
   tildeize it by hand — the leak_gate will reject the notice otherwise.>

   PR: <url>  (or: no remote; commit <sha> is local-only)
   ```
   Leave it uncommitted; committing into autonomous is its resident's act.
   The subject line MUST be the currency output, because that is what
   autonomous compares against its own re-read — a notice without it is a
   claim, and claims are exactly what this step exists to replace.

2. **Ping it** (only if a session is live). Run `ListAgents`; if a session
   whose name contains `autonomous` is listed, `SendMessage` it one line
   (if the bare name does not resolve, append the ` [ref]` that `ListAgents`
   printed for that row — juce-rag hit this on the first live run):
   `<this-repo> retrofit to <kit-version> filed at integrations/<this-repo>/retrofit-<kit-version>.md — please verify.`
   If no such session is listed, skip this — the file already carries it.

Close on a BRANCH with a PR, never a commit left on `main`:

    git switch -c chore/kit-retrofit-<version>
    git push -u origin HEAD && gh pr create --fill

Evidence goes in the PR body — that is where the human reviews. **Do not
merge**; merges are theirs. No remote? Commit on `main` and say so plainly.
`gh` missing? Push the branch and report the compare URL. Canonical wording
for any session's close: `kit/prompts/_closing.md`.

Autonomous will re-run `currency.py` on your repo, compare, and either close
the notice (`status: verified`) or file back what differs. **Do not wait on
that** — you are done when your own close check reads `nothing to do`.

Finish by reporting: the currency output before and after (this is the
visual for the review beat — the `[ ]`→`[x]` delta), the manifest
ratification POLL and its result (never "for ratification" in prose —
`_human-gates.md` §1), green `./verify fast` output, and any briefs filed. Reference
for the target end-state: `~/Documents/Claude/autonomous/` itself (declares
the current kit version and passes its own checker),
`~/Documents/Claude/distillery/`.
