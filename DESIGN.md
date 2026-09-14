# The Autonomous Paradigm — Infrastructure Design

> Synthesis of 2026-07-10: four parallel research threads (multi-agent systems
> survey, coordination/isolation mechanics, memory + governance, local-corpus
> digest) + the existing local corpus (best-practices kit, knowledge loop,
> audit loop, scaffold-agentic-harness, master-harness). This document is the
> brainstorm consolidated into a buildable design. It is NOT yet a ROADMAP —
> phases at the end are proposed, not decided.

## 0. The meta-lesson (every source converges here)

**Systems that work treat the model as a replaceable worker inside a
deterministic scaffold** — externalized state in git, contracts for task
scope, independent executable verification, serialized merges. Systems that
failed tried to get coordination from conversation and role-play (ChatDev,
CAMEL, AutoGen group chats). This is the global doctrine's AI/deterministic
boundary, independently rediscovered by the whole field.

Corollaries with hard evidence:
- **Parallelize reads, serialize writes.** Research/exploration fans out
  (Anthropic's research system: −90% wall clock); writing needs one decider
  per artifact or a serialized merge point (Gas Town's Refinery; Cognition's
  Flappy Bird failure).
- **Harness > head-count.** SWE-agent's interface redesign moved benchmarks
  more than model changes; 3-agent AgentCoder beat elaborate agent-companies
  at ⅓ the token cost. Add roles only when a role adds an *independence
  property* (see §3), not a persona.
- **~42% of multi-agent failures are specification failures** (MAST, n=1600
  traces). The task-decomposition contract deserves more design budget than
  the org chart.
- **Token economics:** multi-agent ≈ 15× single-chat tokens (Anthropic).
  Fan out only where value + verifiability justify it; single-thread the rest.

## 1. What already exists (the local corpus)

| Asset | Location | Role in this system |
|---|---|---|
| Best-practices kit | `claude-code-best-practices/` | Mechanical floor per-organ (layered CLAUDE.md, format hooks, CODEMAP, ignore). **To be superseded by Kit v2 (§6).** |
| Knowledge loop | `integrate-knowledge-loop.prompt.md` | Leaf memory loop (ORIENT/ACT/REFLECT/WRITE, tiers, falsifiers, anti-poisoning gate). Adopted per-organ. |
| Audit loop | `agent-knowledge-loop/` (+ 3 root .md files) | **Vertical** promote-up memory axis, self-similar, hash-ledgered, propose-only staging. The curator runs this. |
| Audit-loop research | `audit-loop-research.md` | Memory-poisoning + promotion-gate literature. Still current; new research extends it (§5). |
| Scaffold prompt | `scaffold-agentic-harness.prompt.md` | Doctrine block, oracle gates, four-knowledge-systems firewall, opt-in coordination modules (audit thread / port-pin / integration channel). Core of Kit v2's "core profile." |
| Master harness | `master-harness/files.zip` | `./verify` oracle contract (fast/full/report), implementer/verifier/critic agent trio, stop-gate hook, traces/, model routing. Becomes the **intra-organ** operating loop. |
| `the-governor/` | empty | Reserved. The governor component (§4) gets built here as a reusable tool, consumed by this project. |

Gaps none of these cover (confirmed by kit digest): orchestration/spawn-join,
concurrent-write handling, halt conditions, CI gating machinery, metrics/audit
trail, session lifecycle, per-agent capability enforcement. That is what this
project builds.

## 2. Anatomy: organs

An **organ** is a bounded module with:

1. **Territory** — a directory subtree it exclusively owns. Enforced by
   PreToolUse hooks (a write outside territory is *blocked*, not discouraged)
   and by import-boundary linting in CI (blocking check — agents rationally
   ignore warnings).
2. **Contract** — `contract/` dir: types, schemas, invariants. The only thing
   other organs may import. Semver-versioned. **Interface-first commits**: a
   cross-organ change begins with a contract commit both sides build against —
   the contract commit IS the synchronization barrier.
3. **Consumer-driven contract tests** (Pact model): each organ commits tests
   against the interfaces it *consumes*; those run in the *provider's* CI.
   Breaking a consumer fails the provider's build — coordination without
   conversation.
4. **Resident loop** — the master-harness trio, run per-organ:
   implementer (writes, scoped brief), verifier (runs `./verify`, reports
   verbatim, never fixes), critic (adversarial read-only, for risky changes).
   The verifier/critic independence property is the active ingredient
   (AgentCoder: self-written tests overfit; Anthropic: agents "confidently
   praise" their own work).
5. **Oracle** — organ-local `./verify fast|full|report`. Layer-0 blocking,
   Layer-E measured. Gate definitions live OUTSIDE organ territory (an
   implementing agent physically cannot weaken its own gate).
6. **Memory** — leaf knowledge loop (INDEX/LIBRARY/CLAUDE.md) inside
   territory. Single writer by construction; no locking needed anywhere.
7. **Journal** — append-only traces/ (one file per change, master-harness
   style) + DECISIONS entries.

**Organ count:** start at 3–4. Field ceiling is 4–8 concurrent worktrees
before merge/review becomes the bottleneck. Grow via the edge protocol (§3),
never by up-front guessing.

## 3. Physiology: coordination substrate

**No live agent-to-agent messaging.** Published experience: peer message
buses were the most fragile layer and mostly unnecessary at this scale.
Coordination is stigmergic — through durable git-native artifacts:

> Scoping (Decision 73, 2026-09-14). The vendor's own line is the one this
> exclusion tracks: **Agent Teams** are interactive-only and cannot run under
> `-p`; **cross-session messaging** with `crossSessionInbound: accept` runs
> unattended and is exactly the capability excluded here. The exclusion rests
> on scale (3–8 agents) and human shift structure, not on stigmergy being
> safer as a mechanism: ~1,200 isolated agents built a covert channel out of
> Artifactory directory names and exchanged 70,000+ messages through it
> (METR, 2026-08-26). Durable artifacts are auditable; they are not inert.

- **Task ledger:** Beads (`bd ready` returns unblocked work; dependencies are
  first-class edges; jsonl through git) or a minimal clone. Free-form TASKS.md
  breaks down at ~8 agents. Every task carries the full delegation contract:
  objective, output format, tool guidance, boundaries, acceptance criteria
  (copied verbatim from ROADMAP, never paraphrased).
- **Serialized merge queue:** worktree-per-organ, short-lived branches
  (hours), merge queue with required checks (build, affected tests, boundary
  lint, contract verification). Flaky-test quarantine from day one — flakiness
  makes agents either retry blindly or "fix" unbroken tests.
- **Message types as ledger entries** (closed set): REQUEST, PROPOSAL
  (contract change), DISCOVERY (lesson candidate), BLOCKER, HALT-VOTE.
  Structured artifacts, never free-text chat (MetaGPT vs ChatDev lesson).

**Rhythm: shifts, not marathons.** Fresh-context sessions per work item with
structured handoff artifacts beat long-running compaction (Anthropic
long-running-harness posts; Ralph loop). Each shift: pull main → read ledger →
one task → verify → commit → journal → handoff notes → die. The conductor
(deterministic script/cron) starts shifts; agents never spawn siblings.

**Edge protocol (new edges / plan changes):**
1. Organ files PROPOSAL (need, interface delta, migration impact).
2. Governor arbitrates: accept (provider implements, contract version bumps) /
   defer (proposer ships visibly-degraded placeholder w/ swap-in point) /
   escalate to human.
3. The dependency graph is a committed artifact (`graph.json`); the boundary
   linter is *generated from it*. Edges exist only when the graph says so.
4. ROADMAP edits are governor-only; every change logged in DECISIONS.

## 4. The governor (three separable functions)

> **Cybernetic frame (2026-08-14, Decision 47).** The governor's three
> functions correspond to Stafford Beer's Viable System Model, and the
> vocabulary is adopted so a fresh-context agent inherits fifty years of
> diagnosed failure modes in a sentence instead of one incident each:
> **watchdog ≈ S3\* (audit bypassing self-report) + the algedonic channel**
> (threshold pain signals that leap the hierarchy — its two-severity halt
> design is already algedonic-shaped); **curator ≈ S2/S3** (shared-standard
> down-propagation, anti-oscillation); **coherence critic ≈ the interface
> where operational health meets identity** — its "green is not coherent" is
> Beer's distinction between S3-level health and viability (mapped loosely on
> purpose: the critic reads inward, not outward — it is NOT S4).
> The fleet's S4 (outside-and-then) is the landscape audit; its S5 is
> DOCTRINE.md + the human at ratification gates. Standing design test from
> Ashby: every mechanism here is an attenuator or an amplifier for the human
> channel, and its noise floor is its capacity — a channel nobody reads has
> no requisite variety. Full mapping, pathology checklist and amendment
> queue: research/2026-08-14-viable-system-model-mapping.md.

**4a. Watchdog — deterministic, no model calls, runs every tick.**
Signals (research-calibrated): token-rate (>~4k/min sustained ≈ looping);
state-hash no-progress (unchanged workspace k steps); (tool,args)-hash
repetition; whack-a-mole (same test flips pass↔fail ≥3×); churn (GitClear:
2-week churn + clone-rate are the leading AI-quality-decay indicators);
test-count trajectory; TODO accretion; diff-size distribution.

Halt triggers, two severities:
- **Hard trips:** scope violation (should be impossible → enforcement layer
  broken → halt), budget ceiling (enforced OUTSIDE the agent process —
  every real incident traced to prompt-level-only guards), destructive-op
  gate, wall-clock timeout.
- **Pause-and-escalate:** rate spike, no-progress, oscillation, CI pass-rate
  regression, gate-weakening attempt, debt accretion, PROPOSAL storm (design
  instability — stop coding, the plan is wrong).

Two refinements ratified 2026-09-14 (Decision 73; (research/proposals/2026-09-10.proposal.md §1–2):
**a monitor the agent can reach is not a monitor** — a checkpoint trained on
reward-hackable environments killed its own monitor in 68% of root-access
episodes and rewrote its reward function in 34% (Anthropic, 2026-08-31), so
watchdog evidence is externalized and signed, verifiable outside the trust
boundary of what it watches (cf. arXiv:2606.26057); and **verification
capacity is provisioned at the pace of what it audits** — Anthropic's August
risk report traces a 3-day detection lag to environment production outrunning
vetting, a coverage gap distinct from a boundary configured but never
verified. Gate-weakening detection has production prior art: Terminal-Bench
4.0 (2026-08-28) admits tasks through an adversarial hacker-fixer loop with
execution and grading in separate containers, scores detected reward-hacking
a hard zero, and mechanical (no-judge) hack detection exists
(arXiv:2608.22103) — the Layer-0 shape this repo's oracle discipline prefers.

Mechanism: `HALT` sentinel file; every agent's PreToolUse hook checks it —
fleet-wide stop within one tool call, enforced by harness not compliance.
Halts are cheap and non-shameful; escalation-on-uncertainty is rewarded
(Anthropic autonomy research; "reduce, never invent").

**4b. Curator — model judgment, quarantined writes.**
Runs the audit loop (SCAN/JUDGE/WRITE/LEDGER) vertically, plus the previously
deferred **down-propagation**: pushing promoted lessons into *specific*
organs' CLAUDE.md (targeted, never broadcast — CLAUDE.md holds ~100–150
instruction slots; selective memory beat comprehensive 39% vs 13% accuracy).
Tier ladder: candidate (organ) → canonical (organ, 2nd occurrence shown
independent — a dependency-aware check that is a hard gate, never a weight) →
proliferated (fleet, curator-only grant, adversarial review: falsifier check,
scope check, contradiction check — a contradiction with an existing
proliferated lesson is a halt signal, not a merge). Provenance (`origin:`)
never dropped; supersede, don't erase; staleness = falsifier/verification
command re-run (executable memory > prose — Voyager). Deterministic lint pass
(refs, caps, timestamps, dedup) runs BEFORE any model judgment.
Write-gate specifics ratified 2026-09-14 (Decision 73; (research/proposals/2026-09-10.proposal.md §4,
primaries read): (i) provenance is a hard exclusion, not a ranking weight —
a soft provenance weight is statistically indistinguishable from no defense
(arXiv:2608.21230), and content screening rejects 0 of 360 plainly-worded
false assertions; (ii) recurrence is not independence — a human adjudication
of 133 real coding-agent lesson candidates found none safe for automatic
promotion, all 11 gate-positives being boilerplate or shared-tool artifacts
(GovMem, arXiv:2607.02579); the check estimates dependency-aware support;
(iii) for lessons that assert what HAPPENED (a gate fired, a test passed),
prefer execution attestation — a record the step ran, writable only by
trusted code — over content or style matching, which paraphrase defeats
(PoEM, arXiv:2608.16032); (iv) re-screen stored entries periodically, since
poison outlives the vector that planted it (InjecMEM, arXiv:2608.23471).
Taxonomy of record: OWASP Agentic Top 10, ASI06 Memory and Context Poisoning.
The Reflexion result (+11pts from failure post-mortems) makes failure
post-mortems the highest-priority REFLECT output — enforced by Stop hook,
never voluntary (voluntary reflection stops exactly when it matters).

**4c. Coherence critic — the residual hole no mechanism closes.**
"Green is not coherent": a merge queue guarantees main passes CI, not that N
individually-sensible changes compose sensibly. A fresh-context read-only
review each cycle against ROADMAP + contracts; findings become ledger issues
or PROPOSALs, never direct edits. This is also where "stuck" and "falsely
done" are audited as first-class states (Devin/AutoGen/ChatDev failure modes).

**Governor authority ceiling:** may edit only ROADMAP, graph.json, memory
files, README, STATUS. Never product code. (Otherwise it becomes a
super-agent and parallelism collapses back into one context.)

**Autonomy tiers keyed to reversibility** (Factory.ai): reversible in-territory
changes auto-land through the queue; schema/contract changes need governor
arbitration; irreversible/outward-facing actions (deletes at scale, pushes to
shared remotes, anything credentialed) require the human. Freeze = revoked
write permission, not an instruction (the Replit lesson).

## 5. New-research deltas to fold into audit-loop-research.md

- Selective-vs-comprehensive memory quantified (13%/2400 vs 39%/248 records).
- CLAUDE.md instruction-slot ceiling (~100–150).
- Reflexion failure-post-mortem priority; Voyager executable-skill memory →
  verification commands attached to lessons enable deterministic staleness.
- Safety erosion with memory age (agents re-execute persisted workflows
  without re-evaluation) → periodic re-validation of proliferated lessons.
- Down-propagation (the deferred phase) is now specified: targeted, curator-
  gated, slot-budgeted (§4b).

## 6. Kit v2 — "the harness factory" (replaces claude-code-best-practices)

User mandate: full replacement is acceptable; research-backed; must include
**profiles that specific agents can spin up out of the box to scaffold their
own type**.

**Shape:** one core + composable agent-type profiles. `scaffold <profile>
<target>` is runnable by a human OR by an agent bootstrapping itself.

**Core layer (every installation):**
- Layered CLAUDE.md + CODEMAP + .claudeignore (survives from v1)
- Doctrine block + four-knowledge-systems firewall (from scaffold prompt)
- `./verify` contract (from master-harness)
- ROADMAP + DECISIONS skeletons
- Hook set: PostToolUse format/lint; SessionStart context injection;
  PreToolUse territory + HALT-sentinel + destructive-op guard;
  Stop enforced-reflection + red-suite gate

**Profiles (each = agent definition + settings/permissions + hooks + CLAUDE.md
template + memory seed + verify wiring + territory manifest):**

| Profile | Independence property it adds | Write scope |
|---|---|---|
| `organ` (implementer trio) | — (the worker) | own territory only |
| `verifier` | not-the-author | none (reports) |
| `critic` | fresh-context adversary | none |
| `scout` | clean-context exploration | none |
| `audit-thread` | separate worktree, fenced checks | `audit/` only |
| `curator` | quarantined memory writes | memory files only |
| `watchdog` | no model calls at all | STATUS + HALT only |
| `coherence-critic` | reads across all territories | ledger issues only |
| `conductor` | deterministic scheduling | none (spawns shifts) |

Each profile's doc states: when it's earned (tier-to-project-size, from the
scaffold prompt's operating contract), what it may never do, and its handoff
artifact format. The kit ships the research bibliography as INSIGHTS v2 —
every prescription cites its evidence.

## 7. Proposed build order (gates, not dates)

- **P0 — enforcement floor.** Repo init; territory hooks; HALT sentinel;
  watchdog skeleton; kit-v2 core. *Gate: adversarial tests — an agent
  instructed to write outside territory is blocked; HALT stops a running
  fleet mid-task; budget trip fires from outside the agent process.*
- **P1 — one organ, real loop.** Single organ + verify + merge queue on a toy
  codebase; shift rhythm; enforced reflection. *Gate: N unattended shifts
  complete tasks with zero human touches; every shift leaves journal + handoff.*
- **P2 — two organs, one seam.** Contract dir, interface-first protocol,
  consumer contract tests, task ledger, graph.json + generated linter.
  *Gate: a cross-organ change lands end-to-end via PROPOSAL → contract commit
  → both sides green → queue merge.*
- **P3 — memory + curator.** Leaf loops per organ; audit promote-up;
  down-propagation. *Gate: a lesson learned in organ A demonstrably changes
  organ B's behavior (the CALL bar: not learned until behavior changed).*
- **P4 — full governor + first real project.** Coherence critic, metrics
  dashboard (visual-first STATUS), escalation paths. *Gate: a full simulated
  incident (injected oscillation, injected gate-weakening) is caught and
  halted without human detection.*

## 8. Open questions for the human

1. Kit v2 location: rewrite in place vs new repo (`harness-factory/`?) with
   v1 archived.
2. Beads (adopt dependency) vs minimal in-repo ledger clone.
3. Conductor substrate: cron + headless `claude -p`, or Claude Code
   agent-teams/Workflow, or a small supervisor daemon. (Affects P0.)
4. First target project — organ count and CI shape should be sanity-checked
   against it before P2.
5. Model routing economics: master-harness assumed Opus-lead/Sonnet-labor;
   revisit against current model lineup and the 15× multiplier.
