# kit CHANGELOG — every entry names the retrofit action it implies

> Semver in `kit/VERSION`. A repo records the version it was scaffolded or
> last retrofit at in `project.manifest.json` → `kit_version`. `/retrofit`
> reads that field and applies every entry BELOW it, in order, as a migration
> — never a re-scaffold. A repo with no `kit_version` is `pre-2.0.0`, not
> "current": absence of a declaration is never read as up-to-date (that
> silence is exactly how the wrapper registry hid five repos).
>
> Entry format: version · date · what changed · **retrofit action** (what
> `/retrofit` does to a repo below this version) · verify gate if any.

## 2.0.0 — 2026-08-17 — baseline

The state of the kit at the moment it gained a version. Everything a
kit-v2 core install carries as of this date:

- Layered CLAUDE.md, ROADMAP.md (phase-gated; Prior-Art bookends per
  Decision 30), DECISIONS.md (append-only), `project.manifest.json`
  (survey answers + composite territory registry; NO status prose per
  Decision 28), INDEX.md + LIBRARY.md (`library-entry.3`), `traces/`,
  `./verify` (`fast|full|report`) carrying the `leak_gate`
  (POSIX + Windows identity paths, `.leakcheck-allow`), CI mirroring the
  Stop hook (`kit/templates/ci.github.yml`, Decision 31 economics),
  `.gitattributes` LF (Decision 34), `contract_gate` for composites
  (Decision 43), `status_validate` fixtures (Decision 45).
- **Retrofit action:** a repo with no `kit_version` gets the K0 survey (which
  of the above are present), then `kit_version: "2.0.0"` written into its
  manifest ONLY when all baseline items are present. Partial installs record
  `kit_version: "pre-2.0.0"` plus the gap list in ROADMAP as explicit debt.
- **Verify gate:** none new — the baseline is what `./verify fast` already
  checks where the repo has one.

## 2.0.1 — 2026-08-17 — /retrofit is a CHANGELOG-driven migration (K1)

- `kit/currency.py` — deterministic: reads a repo's declared `kit_version`,
  diffs against this file, emits the ordered delta with a presence check per
  requirement. `REQUIREMENTS` in that file is the GATE for each version;
  the prose here is the explanation. A test pins that every version here has
  a row there.
- `/retrofit` opens by running it and works the delta; closes by running it
  again and requiring `nothing to do`. Idempotence is checked, not hoped.
- A repo may declare current while missing items (autonomous did, for one
  hour, on the day it declared): reported as drift, louder than behind.
- **Retrofit action:** none for the repo — this entry changes the TOOL, not
  what a repo must contain. Repos at 2.0.0 are unaffected and stay 2.0.0;
  the version bump is a patch so `currency.py` does not report 46 repos
  behind by an entry that asks nothing of them.
- **Verify gate:** autonomous's own `./verify fast` runs the currency tests
  and its own currency check.

## 2.1.0 — 2026-08-17 — mailbox scope rule in every charter (K1 follow-on)

- Every repo's `CLAUDE.md` states, in its own words, **which mailbox is its
  own and that other repos' exchanges are not its business** — the three
  questions in INTEGRATIONS §3 "Scope" (who owes me / did anyone answer me /
  should I act on X↔Y).
- **Retrofit action:** append a `## Mailbox` section to `CLAUDE.md` naming
  (a) `integrations/` in THIS repo as the only place briefs to us land,
  (b) that responses to OUR briefs live in the PROVIDER's tree and must be
  pulled and read, (c) that exchanges between other repos may be READ freely
  but never ACTED on or raised to the human as ours — if one concerns us, we
  file a brief. (Corrected 2026-08-18 per hypersaw-001/002: an earlier draft
  said "ignored", which over-reached into informational quarantine; a repo that
  retrofit before the correction should re-read this clause.)
  Marker-delimited, append-only; if a `## Mailbox` section already exists,
  leave it alone and report the difference.
- **Verify gate:** none — this is a charter statement, and gating prose on
  grep would reward the words over the understanding. The behavioural gate is
  the scoped session brief, which only ever shows a repo its own obligations.
- **Why:** on 2026-08-17 agents in several unrelated projects each warned the
  human about one brief in autonomous's mailbox. Tooling caused it; the rule
  was never written down either way.

## 2.2.0 — 2026-08-18 — the leak gate must FIRE, not merely exist (spectral-morph-001)

- `currency.py` now asserts gate BEHAVIOUR: it plants a POSIX identity path
  and a Windows identity path in a scratch file inside the repo, runs the
  repo's own `./verify fast`, and requires the gate to name the file. The
  plant is created and removed inside one call. Previously it checked that
  `verify` CONTAINED the string `leak_gate` — a presence check on the gate's
  name, and the one place the kit violated its own "assert the effective state"
  rule. `harness/verify` — the template every new project is born from —
  shipped a POSIX-only pattern for a month and read as compliant.
- **Retrofit action:** if either plant fails to fire, replace the repo's
  `leak_gate` pattern with `autonomous/verify`'s (both identity forms, both
  placeholder exclusions). Three detectors, one policy: `verify`,
  `harness/verify`, `governor/leak_scan.py` carry the same regex.
- **Verify gate:** the two `gate-fires:` checks. A repo already declaring
  2.0.0/2.1.0 on a POSIX-only gate now reads BEHIND — correct, and this entry is
  what makes that a migration rather than a silent tightening.

<!-- Next entries append BELOW, newest last, so the migration order reads
     top-to-bottom. K2 (intake/), K3 (session-boundary artifacts) will land
     here as 2.1.0 / 2.2.0 when they ship. -->

## 2.2.1 — 2026-08-18 — retrofit closes by asking to be verified (tool-only)

- `/retrofit` Step 6: on close, the repo files
  `autonomous/integrations/<repo>/retrofit-<version>.md` (uncommitted, mailbox
  exception) carrying its own final `currency.py` output, and pings a live
  autonomous session via `SendMessage` if `ListAgents` shows one. The notice
  is not a claim of completion — it is a request that autonomous re-read the
  tree NOW instead of at the next sweep (closes the delivery gap of Decision
  53 from the other side).
- `governor/retrofit_verify.py` — the receiving half. Re-runs `currency.py`
  on the sender, compares to the claim, and stamps the notice `verified` /
  `disputed` (with the exact difference) / `unresolvable`. Frontmatter is the
  resident's (Decision 56); the filer's body is appended to, never edited.
  Runs from the session brief and by hand.
- **Retrofit action:** none — tool-only. A repo at 2.2.0 is CURRENT.
- **Verify gate:** `governor/test_retrofit_verify.py`.

## 2.2.2 — 2026-08-18 — the gate-fires probe restores `.harness/` (tool-only)

- `currency.py`: `_gate_report`/`_gate_fires` snapshot `.harness/last-verify.json`
  and `.harness/dirty` before running the target's `./verify fast` and restore
  them byte-for-byte after (including "absent"). Found by juce-rag on the
  first live Step 6 verification: a correctly firing gate exits 1, the
  target's `record()` wrote that, and its Stop hook blocked on a red that was
  the probe passing (LIBRARY L0006).
- **Retrofit action:** none — tool-only. A repo at 2.2.0 is CURRENT.
- **Verify gate:** `kit/test_currency.py::TestProbeLeavesHarnessAlone`.

## 2.2.3 — 2026-08-18 — currency renders `~/`; Step 6 notices land in a PUBLIC repo (tool-only)

- `currency.py`'s human-facing render tildeizes the repo path (`_tilde`). The
  JSON keeps the absolute path — machine-consumed, never committed. Step 6
  tells every repo to paste that render into a notice filed in autonomous,
  which is PUBLIC, so an absolute home path is a leak the gate correctly
  rejects. FOUNDATIONS' first notice tripped it within the hour.
- `/retrofit` Step 6 now says so explicitly, and says the ping may need the
  ` [ref]` from `ListAgents` when the bare name does not resolve (juce-rag).
- **Retrofit action:** none — tool-only. A repo at 2.2.0 is CURRENT.
- **Verify gate:** the existing `leak_gate` (it caught this unaided).

## 2.3.0 — 2026-08-18 — the leak gate hides OTHER sessions' probe plants

Found by mind-lathe, hours after 2.2.2 fixed the record clobber — a second,
independent race the record fix does not touch. `currency.py` proves a gate
FIRES by planting identity paths in `.kit-currency-plant-*` INSIDE the target
working tree. Any concurrent `./verify fast` on that tree reads the other
run's plant and goes red on a file that no longer exists by the time anyone
looks — and a retrofit ends by forcing a verify, which is exactly when the
probe runs. mind-lathe's Stop hook reported two hits on
`.kit-currency-plant-37128.md`, then a clean tree.

- `leak_gate` (in `verify`, `harness/verify`, and any repo's copy) excludes
  `.kit-currency-plant-*` unless `KIT_LEAK_PLANT` names that exact file —
  so the plant is invisible to every run except the probe that owns it. Not
  a weakening: the excluded name is a fixed dot-prefixed pattern no project
  file uses, and the owning run still sees it.
- `currency.py` sets `KIT_LEAK_PLANT` on its own probe run, then runs the
  target's verify a SECOND time without it and requires the plant to be
  unnamed — the behavioural check for this entry.
- **Retrofit action:** add the `KIT_LEAK_PLANT` branch to the repo's
  `leak_gate` (copy the block from `harness/verify`; the three detectors stay
  byte-identical). A repo without it still reds a concurrent session while
  being probed — that is what BEHIND means here.
- **DO NOT gitignore `.kit-currency-plant-*`.** It is the obvious way to
  close the hole this exclusion opens — an orphaned plant is untracked AND
  unignored, so a careless `git add -A` could commit identity paths the gate
  now ignores by design. It does not work: `git grep --untracked` skips
  IGNORED files, so the ignore line blinds the probe that OWNS the run too,
  turning the whole gate-fires check into a silent no-op. Proven both
  directions by mind-lathe, whose human had already approved the ignore line
  before their control caught it. What they did instead, and what to copy: a
  `plant_not_tracked` check OUTSIDE `leak_gate` that fails if any
  `.kit-currency-plant-*` is TRACKED — untracked plants stay visible to their
  owning probe, and a committed one can never hide. Kept outside the kit-core
  function so `leak_gate` stays byte-identical across the three detectors.
- **Adopt the block VERBATIM, comment included.** A repo that merges only the
  code keeps its older comment and has to re-reconcile at every future entry;
  byte-identical means an empty diff against canonical (mind-lathe).
- **Verify gate:** `plant-invisible` in `currency.py`'s REQUIREMENTS; the
  fleet checklist will show every repo lacking it.

## 2.4.0 — 2026-08-18 — kit mechanism is VENDORED and checksummed, not copied

The distribution model changes; the doctrine does not. Copying kit code into
every repo produced TEN distinct `leak_gate` implementations across the fleet,
NINE of them missing the Windows identity pattern, while every one of those
repos declared a `kit_version` that promised it. The same day, a batch that
applied a byte-identical diff to 13 repos still left 10 variants standing,
because an identical patch on divergent bases gives divergent results. The
version was a claim about a copy, and a copy can lie.

Split: kit **mechanism** (gate code) is machine-owned and versioned;
kit **substance** (charter, ROADMAP, DECISIONS, LIBRARY) stays a
judgment-bearing retrofit. Only mechanism goes through the new path.

- `.kit/kit-gates.sh` — vendored, byte-identical everywhere, carrying
  `record`, `leak_gate`, `kit_integrity`. Vendored rather than sourced from
  one shared copy because CI has no checkout of the standards repo, and a
  gate that cannot run in CI is not a gate.
- `.kit/MANIFEST` — `kit_version` plus a sha256 per vendored file.
  `kit_integrity` (in `fast`) recomputes and reds on any local edit. Honest
  limit: it lives inside a file it checks, so it detects drift, not tampering
  — the authoritative comparison is external (`kit_sync.py --check`).
- `./verify` becomes PROJECT-owned: it sources `.kit/kit-gates.sh` and holds
  only project gates and test commands. A missing `.kit/` is a hard exit, not
  a degraded run — a silently skipped privacy gate is the exact bug the gate
  exists to prevent.
- `kit/kit_sync.py` — install/check, per repo or `--all`. Never commits.
- `kit/migrate_to_vendored.py` — one-time per repo. Refuses rather than
  guesses: a hand-written `verify` is reported for a human.
- `currency.py` — vendored repos answer the gate questions by CHECKSUM. No
  probe, no plant written into a foreign tree, so the entire defect family
  from 2.2.2/2.3.0 (record clobber, plant collision, ignore-blinding) cannot
  occur for them.
- **Retrofit action:** `python3 <kit>/kit_sync.py <repo>` then
  `python3 <kit>/migrate_to_vendored.py <repo> --apply`. Both deterministic
  and idempotent; neither commits. After this, kit mechanism updates need no
  agent session at all — `kit_sync.py --all` is the whole update.
- `harness/verify` is now THIN — it ships no gate code at all. Until this,
  the doctrine had moved to vendoring while the template every repo is born
  from still carried an inline `leak_gate`, so every fresh `/retrofit` and
  `/spinup` would have manufactured the exact drift 2.4.0 exists to end. Same
  shape as hypersaw-002: a rule corrected where it is READ and left standing
  where it is INHERITED. `ONBOARDING.md` Part 2, `/retrofit` (new Step 4b) and
  `/spinup` now instruct `kit_sync.py` and forbid pasting gate code.
- **Verify gate:** `vendored` in REQUIREMENTS; `kit/test_kit_sync.py`; and a
  COPYABLE GATE check in autonomous's `verify` — no file under `harness/` or
  `kit/templates/` may define `leak_gate`/`record`, so this cannot recur.

## 2.4.1 — 2026-08-18 — a check-in names the directory it actually wrote (tool-only)

Residuum filed a receipt reading `current` while the named repo had no `.kit/`
at all, and nothing in the receipt could show why — `.` resolves against the
caller's working directory, so a run launched from elsewhere syncs a different
repo and still reports success. The receipt now records the absolute path the
run resolved to (tilde-form: it lands in a PUBLIC repo), and `retrofit_verify`
disputes it when that path is not where the registry has that repo. A silent
wrong-target becomes a detectable one.

- `kit_sync.py --note TEXT` — the filer's own words in the receipt. Without it
  the check-in is a fixed template with nowhere to answer a question, which is
  how a direct question to Residuum went unanswered in the very channel it was
  asked in.
- `verify` now RUNS `kit/test_kit_sync.py`. The 2.4.0 entry named it as that
  entry's gate and no oracle invoked it, so thinning `harness/verify` broke
  three of its cases while everything stayed green for three commits. Its
  migration fixture no longer copies `harness/verify` either — a fixture must
  not depend on the artifact under reform.
- **Retrofit action:** none — tool-only. A repo at 2.4.0 is CURRENT.
- **Verify gate:** `kit/test_kit_sync.py`, now actually wired.

## 2.5.0 — 2026-08-18 — `.gitattributes` must be TRACKED, not merely present

Found by Tonality in their own repo, mid-retrofit: `currency.py` reported
`[x] .gitattributes (LF)` for a file that was never `git add`ed. An untracked
`.gitattributes` reaches no clone and no CI, so the repo could declare 2.4.1
with the Windows-CRLF hazard the policy exists to close fully live. The check
read the working tree; the policy only exists in the index.

Third instance of one family in two days — `contains:leak_gate` (2.2.0),
files-installed-but-not-sourced (2.4.0), and now present-but-untracked. The
question a check asks must be the question that matters, and "is this file on
disk" is almost never it.

- `currency.py` gains a `tracked` check kind (`git ls-files --error-unmatch`).
- **Retrofit action:** `git add .gitattributes` and commit. Two repos fleet-wide
  were in this state when it shipped (one of them dormant).
- **Verify gate:** the `tracked` row in REQUIREMENTS; the fleet checklist shows
  every repo lacking it.

## 2.5.1 — 2026-08-18 — `kit_sync` stops calling an untracked `.kit/` current (tool-only)

terrane found the intersection of the whole family: `.kit/` vendored,
checksum-current, UNTRACKED and unsourced, with no `./verify` at all — and
`kit_sync --check` reported `current`. A clone or CI run had zero gates while
the repo read healthy. Every individual check passed.

- New status `untracked`: canonical bytes that are not in the index. Not
  fixable by syncing (the bytes are already right), so the CLI says
  `git add .kit` instead of pretending a write helps.
- `--check` still answers ONLY about the vendored files, by ruling: whether
  `./verify` sources them is the oracle's question, answered by `currency.py`
  and `kit_audit`'s `wired` column. A verdict that means three things means
  none of them. It simply must not call a one-machine state `current`.
- Known false positive recorded in `kit-gates.sh` itself (substack2pdf): the
  leak pattern is a PATH shape, so a URL path reading `/home/<segment>/`
  trips it. Reword the prose rather than allowlist the file — an allowlist
  blinds the gate to that file forever; a reword costs a sentence.
- **Retrofit action:** none — tool-only. But if `kit_sync` now reports
  `untracked`, run `git add .kit && git commit`: your repo is ungated in
  every clone until you do.
- **Verify gate:** `kit/test_kit_sync.py`, whose fixtures had to become real
  git repos — they had been testing the one machine they ran on.

## 2.6.3 — 2026-09-19 — the dirty hook ignores writes outside the repo; /wakeup runs a stale routine audit

Both from HYPERSAW's harness-kit thread (notice `dirty-hook-path-filter`,
brief `hypersaw-003`), adopted as filed.

- `harness/.claude/hooks/posttool-dirty.sh` — marks `.harness/dirty` only
  when the written path is inside `$CLAUDE_PROJECT_DIR` (relative paths
  assumed inside; unreadable path marks dirty). A PR body or scratch script
  written after the final verify no longer trips the stop gate — six
  HYPERSAW implementer streams paid that round trip in three days (B158).
  HYPERSAW's fix, verbatim; both branches re-tested here by feeding the
  hook JSON on stdin.
- `/wakeup` Step 4b — if the repo declares an auditor
  (`.claude/agents/auditor.md` or manifest `auditor.{agent,cadence_days}`)
  and `docs/audits/` holds no report newer than the cadence (default 7
  days), dispatch it in the background at session open. Cadence by
  staleness, not calendar. The auditor charter itself is NOT in the kit:
  one repo's sweep is one data point (Decision 73's independence rule).
- `kit/session/state.py` — `last audit: N days ago (path)` / `last audit:
  none` when an auditor is declared; omitted when none is (absence of an
  auditor is not staleness). Three tests.
- **Retrofit action:** none required — TOOL-ONLY. The hook is copied at
  spin-up, not vendored: an existing repo copies the new file when it wants
  the fix (`cp autonomous/harness/.claude/hooks/posttool-dirty.sh .claude/hooks/`),
  one line in its DECISIONS. The wakeup step is inert until a repo declares
  an auditor.
- **Verify gate:** none.

## 2.6.2 — 2026-09-17 — human gates are polls; a denied push is named, not relayed

Two things the human kept having to say by hand (Decision 74). First, gates
arrived as paragraphs ending in a question mark — survey questions,
"manifest for ratification", plan pauses — easy to miss, no fixed answers,
no record of what was offered. Second, repos born under the pre-2.6.1
template hit the `git push*` deny at close and every one of them quietly
asked the human to run two commands instead of naming the defect.

- `kit/prompts/_human-gates.md` — new shared wording: every human gate is an
  AskUserQuestion poll with a recommended option (the survey is nine polls;
  ratification is one: Ratify / Ratify with changes / Not yet; the retrofit
  plan pause is one); a denied own-branch push is named as the pre-2.6.1
  template and the fix is polled, never routed around, never silently
  relayed.
- `spinup.md`, `retrofit.md` (new Step 4b′: check `.claude/settings.json`
  for the old deny BEFORE the close), `_closing.md`, ONBOARDING (human
  §ratifier, residency rule 6, spin-up step 1), `kit/README.md` (survey
  delivery) — all point at it.
- **Retrofit action:** none required — TOOL-ONLY. Step 4b′ OFFERS the 2.6.1
  permissions block by poll; adoption is the resident's, recorded in that
  repo's DECISIONS. Commands are re-installed to `~/.claude/commands/` as
  usual (the session hook flags a stale copy).
- **Verify gate:** none.

## 2.6.1 — 2026-09-17 — the harness template stops denying what the close contract requires

Found by Sluice (notice `sluice-notice-push-deny`, their D-014), three PRs
into its life: `harness/.claude/settings.json` denied `Bash(git push*)` while
ONBOARDING rule 6 and Decision 66 make pushing the agent's OWN branch and
`gh pr create` the agent's acts. Deny beats allow in Claude Code, so every
kit-scaffolded repo was born needing the human to relay two commands per PR
— a delayed review surface, which is the opposite of what the close contract
exists to give. The template contradicted a ratified decision for 25 days.

- `harness/.claude/settings.json` — allow `git commit *`, `git switch *`,
  `git push -u origin *`, `gh pr create *`; deny `--force`, `-f`,
  `--delete`, `* :*` (remote-ref deletion), and any push to `main` in its
  three spellings. Sluice's narrowing, adopted verbatim. The pre-tool hook's
  blocklist is untouched as the second line of defence; merging stays the
  human's (no `gh pr merge` in the allow list).
- **Retrofit action:** none required — TOOL-ONLY. `.claude/settings.json` is
  copied at spin-up (ONBOARDING step 2), never vendored or checked, so an
  existing repo keeps its own until its resident chooses to adopt the
  narrowing; the human can also just approve pushes as they come. New repos
  are born consistent with rule 6.
- **Verify gate:** none.

## 2.6.0 — 2026-08-18 — currency is COMPUTED from the tree, not declared

The last of the day's presence-vs-effective family, and the one that caused
the most human work. `kit_version` in `project.manifest.json` was the gate:
`currency.py` read the claim and diffed the CHANGELOG above it. A claim goes
stale on its own, so shipping a version made every repo BEHIND whether or not
anything about it had changed. Measured the day it was fixed: **24 repos had
retrofitted THAT DAY and read BEHIND again, and all 24 satisfied every
requirement of every version they were behind.** Zero needed work. The ledger
was asking for 24 sessions to edit 24 strings.

A version is now behind only when one of ITS requirements is actually unmet.

- `currency.py` computes `current` and `behind` from the checks. `declared`
  is still reported — as PROVENANCE, "last deliberately retrofitted at X",
  the one thing the tree cannot tell you. Nothing gates on it.
- `declared_but_missing` is gone as a concept: with no claim, there is
  nothing to contradict. A missing requirement is just an unmet requirement.
- `retrofit_verify` judges a notice by whether the tree meets every
  requirement at or below the claimed version. Three bugs died with the
  declaration: disputes for a stale string, for a release that POSTDATED the
  notice, and for having advanced PAST it.
- `kit/advance.py` deleted the day it was written. It existed to fix stale
  strings; there are none.
- **Retrofit action:** NONE, for any repo, ever, for this entry. No repo's
  code read the field (checked across the fleet: 46 apparent hits were
  `.kit/kit-gates.sh` skipping the unrelated `kit_version:` line in
  `.kit/MANIFEST`, and two `verify` hits were comments). Manifests keep the
  field; it simply stops being asked to tell the truth.
- The same principle applied one layer down: `.kit/MANIFEST`'s `kit_version`
  line is provenance too, so `version-stale` is gone as a status. It made
  every repo stale on every bump for byte-perfect trees, and left the trap
  where a read-only `--notify` reported a state it could not fix (vertex).
  Refreshed for free on any sync; never a reason to act.
- **Verify gate:** `kit/test_currency.py`, where the test asserting the old
  rule is INVERTED and says so — an undeclared but complete repo is now
  CURRENT.

