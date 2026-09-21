# autonomous

**A working system for building software with AI coding agents — and keeping
it correct without a human reading every line.**

This repository is the standards body, toolkit, and control room for a fleet
of about fifty software projects developed almost entirely by Claude Code
agents, from audio plugins in C++ to research tooling in Python, under one
person's direction. It holds the doctrine every agent session loads, the
harness kit that scaffolds and audits each repository, the memory loops that
turn incidents into durable lessons, and the deterministic sweeps that tell
the human what needs attention. Everything here has been run in anger; the
decision log records what broke and what was changed because of it.

*Last verified current: 2026-09-20.*

---

## In one screen

**The problem.** A single developer directing agents can produce more code in
a week than they can read in a month. Reviewing every diff does not scale;
trusting the agent's own report of what it did is not review. Something has
to sit between the agent and `main` that is neither the model's judgment nor
the human's eyes.

**The answer, in five moves.**

1. **The harness outranks the model.** Deterministic hooks, a per-repo
   `./verify` oracle that blocks the session from ending on red, a layered
   `CLAUDE.md`, an append-only decision log, and a phase-gated roadmap. Model
   quality is a multiplier on this; it is not a substitute for it.
2. **AI proposes; deterministic code decides.** No model call sits in the
   path of scheduling, validation, or measurement. Gates are never weakened
   to pass. A reviewer is independent only if it is not the author's own
   lineage.
3. **Assert the effective state, never the declared one.** Every recurring
   defect in this repo's history had the same shape: a check asked whether a
   thing was *named*, *present*, or *claimed* rather than whether it *worked*.
   So the kit's currency checker reads the tree, gate code is vendored and
   checksummed rather than copied, and probes plant a known-bad and watch the
   gate fire before trusting it.
4. **Memory with a write gate.** Each project keeps a small library of
   hard-won lessons, every one with evidence and a falsifier. Lessons are
   promoted only when a second occurrence is shown to be independent; the
   loop feeds its own output back as input, so one wrong lesson is
   reinforced forever.
5. **The human holds the gates, not the keyboard.** Read through Stafford
   Beer's Viable System Model: agents are the operations, deterministic
   sweeps are the audit that bypasses self-report, a monthly landscape audit
   watches the outside world, and the human is the policy layer at named
   ratification gates. Every question for the human arrives as a poll with a
   recommendation, never a paragraph ending in a question mark.

**What it has produced.**

| | |
|---|---|
| Repositories under the doctrine | ~50, across C++/JUCE, Python, TypeScript, and research |
| Decisions on record | 75, append-only, each with rationale and rejected alternatives |
| Kit releases | 16 versions since 2026-08-17; fleet-wide changes ship weekly, tool-only fixes freely |
| Cross-repo exchanges | 45 mailbox threads under one file-based protocol, every state with exactly one accountable side |
| Deterministic test suites in this repo | 91 tests across currency, vendoring, sessions, batch close, sweeps |
| Second machine | a Windows box runs the same sweeps against the same commit, as the falsifier for "clean here means clean" |

**What it is not.** Not a framework you install. Not a multi-agent platform:
the organ fleet is one architecture rung of three, deliberately never the
default, and the parts that govern a running fleet are designed, not built.
Not finished: the roadmap and the reality-check notes below say what is
live and what is still a drawing.

---

## Who this is for, and how to read it

- **Engineering leaders and clients** evaluating whether agentic development
  can be made accountable: read this screen, then §1a (why the layers are
  those layers) and §6 (what "governance" concretely means here). The
  decision log is the evidence base; the roadmap is the honesty check.
- **Practitioners** who want the mechanisms: §2a (how the kit reaches a repo
  and why it is vendored, not copied), §3 (the testing cycle), §5 (the
  cross-repo protocol), and `kit/` itself.
- **A new agent session** arriving here: `ONBOARDING.md`, then `CLAUDE.md`.

The **Navigator's Handbook** under [handbook/](handbook/) is the
human-operator's manual for this way of working: the fourteen principles, the
three nested loops, and the procedures for starting a task, watching a run,
and deciding at a gate. Its companion, the **Gap Integration Schematic**, maps
each principle to what this repo has built and what it still lacks. Both are
living documents and both are audited against the repo, not the other way
round.

---

## 1. The layers, bottom to top

```
┌─────────────────────────────────────────────────────────────────┐
│ 5 · GOVERNOR        watchdog (deterministic halts) · curator    │
│                     (memory) · coherence critic (fresh eyes)    │
├─────────────────────────────────────────────────────────────────┤
│ 4 · MEMORY LOOPS    per-project knowledge loop → promote-up     │
│                     audit loop → curator down-propagation       │
├─────────────────────────────────────────────────────────────────┤
│ 3 · COORDINATION    territories · contracts · task ledger ·     │
│     (fleet only)    merge queue · integrations policy           │
├─────────────────────────────────────────────────────────────────┤
│ 2 · OPERATING LOOP  implementer / verifier / critic ·           │
│                     ./verify oracle · traces · shift rhythm     │
├─────────────────────────────────────────────────────────────────┤
│ 1 · MECHANICAL      layered CLAUDE.md · hooks · CODEMAP ·       │
│     HARNESS         ROADMAP+DECISIONS · .claudeignore           │
├─────────────────────────────────────────────────────────────────┤
│ 0 · DOCTRINE        the standing rules every layer answers to   │
└─────────────────────────────────────────────────────────────────┘
```

Every project gets layers 0–2. Layer 3 exists only on the fleet rung.
Layers 4–5 are installed when a project's lifespan and autonomy earn them.

**Layer 0 — Doctrine** ([doctrine/DOCTRINE.md](doctrine/DOCTRINE.md)).
The standing rules: AI/deterministic boundary (AI proposes and judges, never
schedules/validates/measures), oracle discipline (gates never weaken to
pass), visual-first review, right-sized architecture, the living-README
clarity standard, reduce-never-invent. Machines' global `~/.claude/CLAUDE.md`
files import these — install per [doctrine/INSTALL-GLOBAL.md](doctrine/INSTALL-GLOBAL.md).
The file has a hard size budget enforced by `./verify`, because it loads into
every session on every machine.

**Layer 1 — Mechanical harness** ([kit/](kit/); v1 archived at
[archive/kit-v1/](archive/kit-v1/)).
Deterministic enforcement of the boring stuff: a dirty-marker on every edit
inside the repo, a Stop hook that refuses to end a session on a red oracle,
lean layered CLAUDE.md, append-only DECISIONS.md, phase-gated ROADMAP.md that
outranks all other docs, and permissions that let an agent push its own
branch and open a PR but never merge.

**Layer 2 — Operating loop** ([harness/](harness/)).
The Generic Agent Harness: an **implementer** writes code inside a scoped
brief; a **verifier** runs the oracle and reports verbatim (never fixes); a
**critic** reviews adversarially in a fresh context (never edits). The
independence is the point — agents demonstrably overrate their own work.
Sessions run as **shifts**: fresh context, one task, verify, commit, journal
(traces/), handoff artifact, end. Structured handoffs beat long-running
compaction. Session boundaries are commands: `/wakeup` opens, `/breakdown`
closes, `/reorient` re-primes a lost context, `/closeout` closes a whole
fleet at once when per-repo is untenable.

**Layer 3 — Coordination** (fleet rung only; [DESIGN.md](DESIGN.md) §2–3).
Work partitions into **organs**: bounded modules with hook-enforced write
territories, a versioned `contract/` dir as the only seam, and their own
resident layer-2 loop. Coordination is stigmergic — task ledger, contract
commits, serialized merge queue; **no live agent-to-agent messaging**. The
excluded thing, precisely, is unattended cross-session messaging; the
exclusion rests on small scale and human oversight, not on file-based
coordination being inherently safer (Decision 73).

**Layer 4 — Memory** ([loops/](loops/); standards in §4 below).

**Layer 5 — Governor** ([governor/](governor/); spec DESIGN §4).
Three separable functions on the AI/deterministic split: a **watchdog**
(deterministic, no model calls), a **curator** (model judgment behind
quarantined writes), and a **coherence critic** (fresh-context review,
because "green is not coherent"). **What is real today** is the
watchdog-as-monitor: fleet-health sweeps that read the tree and the remote,
never a self-report — `monitor.py`, `leak_scan.py`, `ball_scan.py`,
`s4_scan.py`, `kit/currency.py` — plus the weekly algedonic channel that
turns remote-visible pain (a red default branch, a leak in a public tree)
into a notification. The HALT sentinel, the watchdog loop, and the conductor
are designed and deferred until a running organ fleet exists to govern.

---

## 1a. The cybernetic frame (why the layers are those layers)

The layers above are not an arbitrary stack. Since Decision 47 this system is
read through **Stafford Beer's Viable System Model**, adopted for a blunt
reason: it lets a fresh-context agent inherit fifty years of diagnosed failure
modes in a sentence, instead of rediscovering each one through its own
incident.

| VSM | Here | Built? |
|---|---|---|
| **S1** — the operations that do the work | each repo in the fleet | live |
| **S2** — anti-oscillation, shared standards | `doctrine/INTEGRATIONS.md`, contracts, the kit | live |
| **S3** — resource bargain, direction | the human at ratification gates; `ROADMAP.md` | live |
| **S3\*** — audit that BYPASSES self-report | `governor/monitor.py`, `leak_scan.py`, `ball_scan.py`, `kit/currency.py` | live |
| **S4** — outside-and-then | the monthly landscape audit, `governor/s4_scan.py` | live |
| **S5** — identity, policy | `doctrine/DOCTRINE.md` + the human | live |
| **algedonic** — pain that leaps the hierarchy | `governor/algedonic.py`, weekly | live |

Three consequences worth stating, because they explain choices that otherwise
look like overcaution:

**S3\* is the load-bearing one.** An audit that reads a system's *self-report*
is not an audit. Every recurring defect in this repo's log has the same shape:
a check asked a question adjacent to the one that mattered — did the gate's
*name* appear, was the file *present*, did the manifest *say* it was current —
and passed while the thing itself was broken (LIBRARY L0014). So the standing
rule is **assert the effective state, never the declared state**, and it is why
the kit's currency checker reads the tree rather than a version string.

**Ashby's law sets the human's channel as the constraint.** Every mechanism
here is an attenuator or an amplifier for one human's attention, and *a channel
nobody reads has no requisite variety*. That is the actual reason a report that
cries wolf is treated as a defect and fixed, not tolerated: a sweep that
flagged 20 repos for a username that was a substring of "transport" trained its
reader to ignore it, and was fixed the day it was found.

**Recursion is the direction, not the current state.** The same protocol should
run at the project level and at the ecosystem level over projects — that is why
`/breakdown` (one repo) and `/closeout` (the fleet) are the same shape at two
scales. Full mapping, pathology checklist and amendment queue:
[research/2026-08-14-viable-system-model-mapping.md](research/2026-08-14-viable-system-model-mapping.md).

---

## 1b. Track record: what broke, and what changed

The decision log is the evidence. A sample, each one a real incident that
became a mechanism:

- **A machine-identity path leaked into a public repo's history** and sat
  there for 19 days while every local sweep pointed one directory too high.
  Result: the leak gate runs on tracked *and* untracked files, a fleet-wide
  scanner backs it, and the weekly algedonic channel checks what a stranger
  can see. (Decisions 47, 64)
- **Ten different copies of the same gate** existed across the fleet, nine
  missing a pattern that every one of them *declared* it had. Result: gate
  code is vendored byte-identical and sha256-pinned; a repo's own `./verify`
  sources it and fails if it is edited. (Decision 65)
- **Twenty-four repos read "behind" on the day they had been updated**, all
  satisfying every requirement, held back by a version string. Result:
  currency is computed from the tree; the declared version survives only as
  provenance. (kit 2.6.0)
- **Every kit-scaffolded repo was born unable to open its own pull request**,
  because a template denied what the close contract required. Found by the
  third repo to be born under it. Result: a narrowed permission set and a
  retrofit step that checks for the old one before the close. (kit 2.6.1–2.6.2)
- **A second machine's first sweep produced 20 false alarms** from a
  username that was a substring of ordinary words. Result: an anchored
  pattern, and the standing rule that a clean sweep on one machine is
  evidence about that machine only. (Decision 71)

Each entry in [DECISIONS.md](DECISIONS.md) records the alternatives rejected
and why; each lesson in [LIBRARY.md](LIBRARY.md) carries its evidence and the
observation that would falsify it.

---

## 2. How a project comes to life (the spin-up protocol)

1. **Survey.** A standard, repeatable question list about scope — what it is,
   the architecture rung, the domain core, oracle shape, consumers, lifespan/
   autonomy tier (full list: [kit/README.md](kit/README.md)). Each question is
   a poll to the human; answers are committed as `project.manifest.json`, and
   ratification of the manifest is one more poll.
2. **Deterministic scaffold.** Code — not model judgment — applies templates
   from the manifest: hooks, CLAUDE.md skeletons, verify stubs, only the
   modules the answers earned. Re-runnable: change an answer, re-run, diff.
3. **Architecture menu** (survey question 2, never defaulted):
   - **Rung 1 — single-threaded agent.** The default for most projects.
   - **Rung 2 — thread + read-only subagents / fresh-context verifier.**
     Earned by: read-heavy exploration, or correctness stakes that warrant an
     independent checker.
   - **Rung 3 — organ fleet.** Earned by: genuinely parallelizable *and
     verifiable* work, real seam count, value justifying ~15× token cost.
4. **Knowledge loop** seeded with the survey's tag vocabulary (§4a).
5. First ROADMAP phase and its gate are written before any code.

Escalate rungs only when the current rung is the demonstrated bottleneck.

---

## 2a. How the kit reaches a repo (vendored, not copied)

Until kit 2.4.0 the kit's gate code was **copied** into each repo at scaffold
time. The result, measured on 2026-08-18: **ten distinct `leak_gate`
implementations across the fleet, nine of them missing the Windows identity
pattern — while every one of those repos declared a `kit_version` that promised
it.** A version was a claim about a copy, and a copy can lie.

The split that fixed it:

- **Kit MECHANISM is vendored and checksummed.** `.kit/kit-gates.sh` is
  byte-identical everywhere, pinned by sha256 in `.kit/MANIFEST`, and
  `kit_integrity` reds the build if anything edits it. `./verify` is
  project-owned and *sources* it. Vendored rather than sourced from one shared
  copy because CI has no checkout of this repo, and **a gate that cannot run in
  CI is not a gate**. Update with `kit/kit_sync.py`; no agent session required.
- **Kit SUBSTANCE stays a judgement-bearing retrofit** — charter, ROADMAP,
  DECISIONS, LIBRARY are per-repo and are what `/retrofit` is actually for.

**Currency is computed, not declared** (2.6.0). A repo is behind only when one
of a version's requirements is genuinely unmet. `kit_version` in the manifest
survives as *provenance* — "last deliberately retrofitted at X", the one fact a
tree cannot state — and nothing gates on it.

**Releases are batched.** Fleet-affecting kit changes accumulate and ship at
most weekly, announced; tool-only fixes flow freely because they cost repos
nothing (Decision 68). A repo that has never been retrofitted is a standing
queue item, worked when that repo is next opened, never nagged.

---

## 3. The testing cycle (oracle discipline)

Every project exposes one interface: **`./verify <target>`** (contract:
[harness/README.md](harness/README.md)).

- **`fast`** — seconds: lint, typecheck, unit tests, cheap invariants.
  **Layer-0: deterministic, no model calls, blocks everything** — the Stop
  hook refuses to end a session on red; CI mirrors it.
- **`full`** — the whole gate: fast + integration + golden datasets +
  behavioral evals. **Layer-E items are measured, never blocking** — and
  never conflated with Layer-0 (guaranteed vs measured is stated, always).
- **`report`** — prints the last verify result without re-running.

Rules that never bend: gates are never weakened to pass (a wrong gate is
fixed deliberately, with a DECISIONS entry); gate definitions live outside
the implementing agent's write territory; **passing ≠ done** — done is oracle
green *and* acceptance criteria satisfied *and* a trace written, checked
separately. An automated reviewer counts as independent only if separately
sourced from the author. On the fleet rung, add: merge queue with required
checks, flaky quarantine from day one, and consumer-contract tests (§5) in
the provider's CI.

---

## 4. Memory: the standards

### 4a. Spinning up a knowledge loop (per-project)

**When: every project, at scaffold time — default-on** (Decision 11). The
loop costs three files and a write-gated session discipline; a quiet project
pays ~nothing, and early setup-era lessons are unrecoverable if never
captured. What scales with project scope is the heavier machinery (audit
threads, fleets, governor), never the loop itself.
**How:** run [loops/knowledge-loop/integrate-knowledge-loop.prompt.md](loops/knowledge-loop/integrate-knowledge-loop.prompt.md)
verbatim. It installs three files — CLAUDE.md protocol block, INDEX.md
(compact retrieval map, read in full), LIBRARY.md (durable lessons) — and
seeds exactly one real lesson. The per-session cycle is ORIENT (read INDEX,
pull only matching LIBRARY entries) → ACT → REFLECT ("what could a future
session not cheaply re-derive?") → WRITE (atomic LIBRARY+INDEX append).
Every lesson carries **evidence and a falsifier**; new lessons enter as
`candidate` and earn `canonical` on a second occurrence the promoter has
shown to be independent — a different root cause, not the same shared kit
file, prompt, or tool seen twice. Recurrence alone never promotes
(Decision 73).
**The write gate:** prefer not writing over writing unverified — the loop
feeds its own output back as input, so one wrong lesson is reinforced
forever. In autonomous operation, REFLECT is hook-enforced, never voluntary.

### 4b. Spinning up an audit loop (cross-project harvest)

**When:** a parent directory has ≥2 children running knowledge loops.
**How:** (canonical: [loops/audit-loop/](loops/audit-loop/))
1. Run `integrate-audit-loop.prompt.md` at the parent scope — installs the
   AUDIT-LOOP protocol block, INDEX/LIBRARY, and `AUDIT-STATE.json` (the
   hash ledger that makes passes incremental and idempotent).
2. Schedule `audit-loop.sh` (weekly cron, **propose-only mode**): it hashes
   each child's LIBRARY, skips unchanged children, and writes proposed
   promotions to `audit-runs/<date>.proposal.md` — never directly to the
   shared store. This is the staging-buffer defense from the memory-poisoning
   literature.
3. A human (later: the curator) reviews and applies proposals.

Scheduling an audit loop on a specific machine (cron setup, config location)
is machine-local ops — see [ONBOARDING.md](ONBOARDING.md) Part 1, not here.

### 4c. Cross-proliferating lessons between libraries (the promotion standard)

A lesson climbs only through gates that **tighten with altitude**:

- **Qualified at source** — `canonical` in its own project, OR the same
  pattern found *independently* by ≥2 siblings (shared-source convergence
  counts once, not twice).
- **Generalizes beyond origin** — promote the transferable pattern, never the
  project-specific fact. Litmus: can you state it without naming the origin's
  code? If not, it stays local.
- **Dedup over abstraction** — matching lessons merge (adding origins and
  evidence) rather than duplicate; concrete instances are preserved, because
  aggressive summarization measurably destroys the detail that makes lessons
  usable.
- **Provenance never dropped** — every promoted entry carries `origin:`
  back-links and its falsifier, so it can be traced and revoked. Supersede,
  don't erase.
- **The parent is the intersection of what is reusable, not the union of the
  children.** When in doubt, don't promote.

Downward proliferation (parent → specific children's CLAUDE.md) is the
curator's job — **targeted, never broadcast** (a CLAUDE.md holds roughly
100–150 instruction slots; selective memory beat comprehensive 39% vs 13% —
[research/2026-07-10-memory-governance.md](research/2026-07-10-memory-governance.md)),
slot-budgeted, and behind the same adversarial review. This direction ships
in Phase P3.

**The global memory is two pools** (Decision 11): an **append-only stream**
(warehouse — every candidate lesson from every sweep, dated, provenance
attached) and the **distilled pool** (mart — the top of the audit-loop
hierarchy). The stream is read *only* by a top-level analytical agent hunting
longitudinal patterns (recurrence, demote-recur cycles, cross-project failure
signatures); it is **never retrieval context for working agents**, and its
findings enter circulation only through the distilled pool's promotion gates.

---

## 5. Cross-project development (the integrations protocol)

Full policy: [doctrine/INTEGRATIONS.md](doctrine/INTEGRATIONS.md). The short
version:

- **Data plane:** providers publish `INTEGRATION.md`; consumers file
  file-based exchanges under `integrations/<project>/` —
  `brief.md → response.md → notice.md`. One boundary module per consumer;
  pinned versions; degrade visibly when the provider is absent.
- **Control plane (who commits, who PRs):** **writes stay home** — only a
  repo's residents ever commit to it, because visitors bypass the resident
  harness. Every exchange state has exactly one accountable side (`ball:`
  frontmatter); closure is the job of `status:`, never of `ball:`. A
  cross-repo change is **two linked PRs**: provider lands first (implement,
  version, tag, notice), consumer lands second (bump pin, adapt boundary
  module, verify). Consumer contract tests are consumer-authored,
  resident-landed, and run in the provider's CI — so breaking a consumer
  fails the provider's build automatically.
- **Never blocked:** overdue balls escalate; meanwhile the consumer ships a
  visibly-degraded placeholder and proceeds.

The protocol has carried 45 threads to date, including three amendments to
itself proposed by a consumer and ratified at the human gate (Decision 67).

---

## 6. Governance and halting (fleet rung — partly built)

> Target design for governing a running organ fleet. **Built today:** the
> deterministic gates (leak_gate, CI, `leak_scan.py`), the S3\* sweeps
> (`monitor.py`, `ball_scan.py`, `s4_scan.py`, `kit/currency.py`,
> `kit/kit_audit.py`), the algedonic channel (`algedonic.py`, weekly), and
> notice verification (`retrofit_verify.py`). **Still designed only:** the HALT
> sentinel, the watchdog loop, and the conductor — they await a running organ
> fleet to govern. See Layer 5 and §1a for what is real.

Every consequential guard is **technically enforced, never prose** — the
published incident record (production-database deletions, five-figure runaway
loops) traces to prompt-level-only guards. Concretely: budgets metered outside
any agent's process; freezes = revoked permissions; a `HALT` sentinel file
that every agent's PreToolUse hook checks, stopping the fleet within one tool
call.

Halt triggers come in two severities (ranked list: DESIGN §4a):
**hard trips** (territory violation, budget ceiling, destructive-op gate,
wall-clock timeout) and **pause-and-escalate** (token-rate spike ≈ looping,
no-progress state-hash, oscillation/churn, CI regression, gate-weakening
attempt, PROPOSAL storm = the plan is wrong, stop coding). Halts are cheap
and non-shameful; escalation-on-uncertainty is rewarded. Autonomy is graded
by **reversibility of the change**, not trust in the model. A monitor the
agent can reach is not a monitor: watchdog evidence is externalized and
signed, and verification capacity is provisioned at the pace of what it
audits (Decision 73).

---

## 7. Map of this repo

| Path | What | Status |
|---|---|---|
| [handbook/](handbook/) | The Navigator's Handbook (human operator's manual) and the Gap Integration Schematic (principle → component coverage), living documents audited against the repo | current |
| [ONBOARDING.md](ONBOARDING.md) | Replication + arrival guide (human and agent) — start here on a new machine | current |
| [DESIGN.md](DESIGN.md) | The full research-backed design | current |
| [ROADMAP.md](ROADMAP.md) | Phase-gated direction: C0 done; kit v2 + ecosystem tracks in progress; governor watchdog-monitor next, HALT/conductor/critic deferred | current |
| [DECISIONS.md](DECISIONS.md) | Append-only decision log (75 on record; NOT in numeric order — next is max+1) | current |
| [doctrine/](doctrine/) | Doctrine (auto-loaded, size-budgeted) + INTEGRATIONS + CONVENTIONS (read on demand) + global-install guide | current |
| [kit/](kit/) | The harness factory, **v2.6.3**: survey → manifest → vendored gates. `currency.py` (computed currency), `kit_sync.py` (vendoring), `kit_audit.py`, `commands/` (`/spinup` `/retrofit` `/wakeup` `/breakdown` `/reorient` `/closeout`), `prompts/` (shared wording: close contract, human gates), `session/` (state + registry + batch close + boards), `vendor/kit-gates.sh` | live |
| [harness/](harness/) | Generic Agent Harness (layer 2): agents, hooks, permissions, thin verify template | live |
| [loops/](loops/) | Memory loops — knowledge loop (per-project) + audit loop (cross-project harvest), both canonical here | current |
| [governor/](governor/) | **S3\* + algedonic live** — `monitor.py`, `leak_scan.py`, `ball_scan.py`, `s4_scan.py`, `algedonic.py`, `retrofit_verify.py`, `red_records.py`. HALT sentinel / watchdog loop / conductor still designed (DESIGN §4) | partly built |
| [integrations/](integrations/) | Intake channel — one dir per correspondent; 45 threads | live |
| [registry.json](registry.json) | Canonical sweep/watch roster rules for ecosystem processes (Decision 14) | live |
| [routines/](routines/) | Versioned prompts for recurring routines (the monthly landscape audit, run as a cloud routine; propose-only) | live |
| [research/](research/) | The evidence base, citations preserved — surveys, the VSM mapping, monthly audit proposals, bibliography | current |
| [LIBRARY.md](LIBRARY.md) / [INDEX.md](INDEX.md) | This repo's own hard-won lessons (18 on record), each with evidence and a falsifier | live |
| [briefs/](briefs/) | Design briefs received from the human, kept as the citable original | live |
| [archive/kit-v1/](archive/kit-v1/) | Kit v1, frozen | archived |

**Sibling repos** (own repos, sequenced in ROADMAP → Ecosystem tracks):
[distillery](https://github.com/Julian-B-Smith/distillery) (global memory:
stream + analyst + distilled pool) ·
[dispatch](https://github.com/Julian-B-Smith/dispatch) (daily progress
publishing) ·
[ai-integration-methodology](https://github.com/Julian-B-Smith/ai-integration-methodology)
(the human-epistemics sibling). This repo governs; they execute.

---

## 8. About the author, and working together

This system is built and operated by [Julian Smith](https://github.com/Julian-B-Smith),
who directs the fleet as its sole human: setting goals, holding the gates,
and deciding what survives. The standing integrator role in this repo —
curation, retrofits, the mailbox, the boards — is held by a Claude Code
session under that direction, and the decision log records which rulings were
the human's.

If you are evaluating agentic development for a team, the useful conversation
is not "which model" but "what sits between the agent and main, and who reads
it". The mechanisms here are the current answer; the decision log is what it
cost to learn them.

## 9. Maintenance

Curated by the standing integrator role: canonical-copy discipline (one home
per artifact; every other location is a pointer), README freshness per the
clarity standard, DECISIONS as the append-only trail, periodic dedup sweeps.
**If the same editable content exists in two places, one of them is a bug —
file it.**

README freshness is itself a gate, not a good intention: the *Last verified*
line above is dated, and a README that lies about its repo is treated as a bug
of the same severity as a failing test (clarity standard).
