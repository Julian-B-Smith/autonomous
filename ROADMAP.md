# autonomous — ROADMAP

> **Single source of truth for project direction.** Any forward-looking
> statement anywhere else (README, DESIGN.md, docstrings) defers to this file.
> Phase gates are never weakened to pass. A phase closes only when its gate is
> green.

## Build sequence (phase-gated)

- **Phase C0 — Consolidation.** Pull the ad-hoc corpus into this repo;
  doctrine single-sourced; pointers wired (global CLAUDE.md, tombstones);
  pushed to the remote.
  *Gate: no editable artifact exists in two places (dedup sweep clean); global
  CLAUDE.md imports doctrine/ and a fresh session sees the doctrine; remote
  up to date.* **← current phase**
- **Phase P0 — Enforcement floor.** Territory PreToolUse hooks; HALT sentinel;
  watchdog skeleton (deterministic, no model calls); kit-v2 core layer.
  *Gate: adversarial tests — an agent instructed to write outside territory is
  blocked; HALT stops a running fleet mid-task; a budget trip fires from
  outside the agent process.*
- **Phase P1 — One organ, real loop.** Single organ + `./verify` + merge queue
  on a toy codebase; fresh-context shift rhythm; enforced reflection via Stop
  hook. *Gate: N unattended shifts complete tasks with zero human touches;
  every shift leaves journal + handoff artifact.*
- **Phase P2 — Two organs, one seam.** Contract dir; interface-first protocol;
  consumer contract tests; task ledger; graph.json + generated boundary
  linter. *Gate: a cross-organ change lands end-to-end via PROPOSAL → contract
  commit → both sides green → queue merge.*
- **Phase P3 — Memory + curator.** Leaf loops per organ; audit promote-up;
  curator down-propagation (targeted, slot-budgeted). *Gate: a lesson learned
  in organ A demonstrably changes organ B's behavior.*
- **Phase P4 — Full governor + first real project.** Coherence critic; metrics
  dashboard (visual-first STATUS); escalation paths. *Gate: a full simulated
  incident (injected oscillation, injected gate-weakening) is caught and
  halted without human detection.*

## Ecosystem tracks (parallel development across repos)

The broader structure the phases above serve. Each track is a separate repo
with its own ROADMAP; this section owns only the cross-track sequencing and
seams. Exchanges between tracks go through `integrations/` per the
INTEGRATIONS policy.

- **Track A — autonomous (this repo): standards + kit + governor.**
  Phases C0/P0–P4 above and kit v2. Provides: doctrine, kit core (incl. the
  STATUS surface and LIBRARY entry schema — briefs dispatch-001 /
  distillery-001, both ball: provider, respond-by 2026-07-24), the sweep/SCAN
  primitive extraction, harness profiles.
- **Track B — distillery (`~/Documents/Claude/distillery/`): global memory.**
  The two-pool system (Decision 11): append-only stream + analyst + distilled
  pool. Phases D0–D4 in its ROADMAP. Seams: consumes LIBRARY schema + sweep
  primitive (Track A); autonomous P3 down-propagation consumes its distilled
  pool (gates implemented there, spec canonical here — per distillery-001).
- **Track C — dispatch (`~/Documents/Claude/dispatch/`): progress publishing.**
  Deterministic collector → FACTS → styled digest → fenced AI narration →
  human-gated publish. Phases E0–E4 in its ROADMAP. Seams: consumes the
  STATUS surface (Track A; degrades visibly until it ships); later consumes
  distillery lesson-highlights (needs D4).
- **Track D — landscape audit (no repo; runs against Track A).** Monthly
  propose-only research pass over the external field (see Deferred);
  bibliography is its ledger.

**Execution-project registry** (leaf repos running the harness kit; they
consume Track A standards and feed back only through their group scope's
knowledge-loop harvest — listed so the governor and audits know they exist,
not for cross-track sequencing):

- **HYPERSAW** (`~/Documents/Claude/synthetic-worlds/HYPERSAW/`, public:
  github.com/Lifted-Truck/HYPERSAW) — coupled-oscillator synthesizer plugin
  (CLAP/VST3). Spun up 2026-07-17 via /spinup; manifest ratified same day;
  rung 2; CI mirrors the Stop hook (`verify fast` only — audio Layer-E is
  macOS-local). First registered execution project. Future consumer of
  Tonality (brief due at its Phase 3); registered here at human direction
  during its ratification gate.
- **FOUNDATIONS** (`~/Documents/Claude/synthetic-worlds/FOUNDATIONS/`, private:
  github.com/Lifted-Truck/FOUNDATIONS) — C++ infrastructure library for
  synth/MIDI plugins (parameter registry, modulation, scoped presets, voice
  architecture, signal graph, event pipeline, musical-context blackboard). Owns
  no novelty; owns the contracts novelty plugs into. Spun up 2026-08-08 via
  /spinup (composite variant); manifest RATIFIED 2026-08-09; rung 2
  (human-chosen — earned by the §7 Mediator critic-profile and bit-parity
  extraction oracles; rung 3 explicitly not earned). CI mirrors the Stop hook
  (`verify fast`, ubuntu; `full` is macOS-local — `auval`/codesign — per
  Decision 31). Phase: F0 closed, F1 prior-art complete, F2 = HYPERSAW
  extraction behind a bit-parity gate.
  **This is the first registered project that is UPSTREAM of other registered
  projects** — provider to HYPERSAW, Morphos, unified-pm, spectrogen,
  refraction-bench, Place, quantum-morph, auricle; consumer of autonomous,
  Tonality, tonality-core. That is why it is a track entry and not merely a
  registry line: an F2 slip moves HYPERSAW's schedule, and a contract-version
  event moves all of them at once. **It is therefore the first entry here whose
  phase state is a cross-track ordering constraint** — see the constraints list
  below. Registered per brief `foundations-001` (Decision 38).
- **plainsynth** (`~/Documents/Claude/synthetic-worlds/plainsynth/`) — a
  deliberately boring generic synth (sine/saw/noise) that exists as a
  **validation instrument for FOUNDATIONS**: it consumes the header-only C++20
  core and proves the seam works before anything interesting depends on it.
  Manifest RATIFIED 2026-08-12. Full harness + CI. First registered consumer
  of FOUNDATIONS whose only purpose is to be a consumer — listed so the
  eight-way fan-out in constraint 4 has a canary.
- **spectral-morph** (`~/Documents/Claude/synthetic-worlds/spectral-morph/`)
  — research phase mapping the algorithm space for musical morphing between
  two sounds (transformation, not mixture). Manifest structured
  (`ratified: null`, state in ROADMAP). Full harness + CI. FOUNDATIONS lists
  it `deferred` with `revisit_at: "when it ships a deployable"` — its own
  first artifact, not a FOUNDATIONS phase.
- **mind-lathe** (`~/Documents/Claude/mind-lathe/`, **private**) — the public
  static site at the root of mindlathe.xyz (Vite/React/TS, pre-rendered).
  Spun up 2026-08-15, manifest PROVISIONAL awaiting ratification. Consumes
  autonomous + life-os tooling conventions. **Standing constraint carried
  from its Life-OS brief:** the hidden hub path must never appear in public
  OUTPUT. Note the object of that rule is the *built artifact* — the repo is
  private and can stay so indefinitely; what is public is the served page.
  Checked 2026-08-15: `vite.config.ts` names the prefix in a source
  comment, and `dist/` (index.html + bundle) contains the domain only, no
  `/lathe` path. Clean. The check worth keeping is "grep the build, not the
  source" — a comment never ships; a `base`/route string does.
- **mindlathe-design** (`~/Documents/Claude/mindlathe-design/`, **private**) —
  the Mindlathe design system in the form Claude Design consumes: 23
  self-contained HTML specimen cards + canonical `tokens.css`. Spun up
  2026-09-03 at kit 2.6.0 (vendored gates), rung 1, manifest PROVISIONAL.
  Provider to mind-lathe (tokens, hash-pinned); Life OS likely later. Oracle
  is invariants-only with self-proving detectors; headless render deferred on
  a dependency decision. (Registered via brief mindlathe-design-002 — the
  first thread filed carrying `seq:` and `cites:` under Decision 67.)
- **juce-rag** (`~/Documents/Claude/juce-rag/`) — deterministic grounding
  layer over JUCE documentation, built for coding agents. Manifest
  structured (`ratified: null`). Full harness + CI. Its retrieval tools are
  the high-risk MCP shape (path + pattern args touching the filesystem) —
  first in line for the MCP-server sweep (LIBRARY L0003 check).
- **ANTIPHON** (`~/Documents/Claude/synthetic-worlds/Antiphon/`, public:
  github.com/Lifted-Truck/antiphon) — quantized harmonic companion for Ableton
  Live (live regime only; the offline harmonizer is Wend's `harmonize` mode).
  Spun up 2026-07-13 via /spinup; rung 1 (single thread); CI mirrors the Stop
  hook (`verify fast`; Layer-E needs a live Ableton set and is not runnable on
  a runner). **Status: deliberately dormant** — feature work gated on three
  unmet spin-up conditions (Wend H2 passes; a demonstrated live-regime need; a
  measured quantization ceiling). Green oracle, no activity expected. Future
  consumer of **Wend** (frozen `HarmonicSpine` + pinned voice stage) and
  **Tonality** (analysis slices); briefs deliberately unfiled until the
  conditions hold. Listed per brief `antiphon-001`; dormancy is also declared
  machine-readably in its manifest (`dormant.review_by`), which is what the
  governor actually reads — this prose entry is for humans.

**Cross-track ordering constraints (the only ones):**
1. Kit v2 core's STATUS + LIBRARY-schema artifacts unblock dispatch E1
   (fully) and distillery D1 (validation half) — answer both briefs early.
2. The sweep primitive should be extracted ONCE (Track A, from
   loops/audit-loop's SCAN) before D1/E1 build their own — or D1/E1
   build minimal local versions behind the same interface and swap in
   (degrade-visibly rule applies to internal seams too).
3. autonomous P3 must NOT build a second distilled pool — it consumes
   Track B's (D4).
4. **FOUNDATIONS F2 gates HYPERSAW's extraction work**, and any FOUNDATIONS
   contract-version event is a fan-out to all eight registered consumers.
   This is the first ordering constraint in this list that originates in an
   execution project rather than in Track A — execution projects were assumed
   to be leaves ("they feed back only through their group scope's
   knowledge-loop harvest"), and FOUNDATIONS is not one. The assumption stands
   for every other entry; it needed naming rather than silent amendment.
5. Everything else proceeds in parallel without coordination.

**Ecosystem-lead milestone (decision-in-principle, gated).** Once distillery
D4 + autonomous P3 are green, evaluate promoting **distillery to operational
lead** of the ecosystem — the analyst is the natural seed of the
ecosystem-level curator/governor, and the operator should be a separate
entity from the standards body (separation of powers: the repo that defines
gates shouldn't be the one operating under them day-to-day). autonomous
remains the doctrine/kit/protocol home either way. Gate for the handoff: the
distillery analyst has produced ≥N ratified promotions with zero poisoning
incidents, and the governor's curator role runs against distillery pools in
a full simulated cycle.

## Parallel track — Kit v2 ("the harness factory")

Built alongside P0–P2, since the phases consume its profiles as they emerge.
Spec: DESIGN.md §6. First profiles needed: `organ`, `watchdog`, `conductor`
(P0/P1); then `verifier`/`critic` (P1), `curator` (P3), `coherence-critic`
(P4). Kit v2 ships INSIGHTS v2: every prescription cites its evidence in
`research/`.

**Shipped so far** (2026-07-10/11): `kit/contracts/library-entry.md` (v1),
`kit/contracts/status.md` (v1), `kit/sweep/` (the shared SCAN primitive,
tested, wired into this repo's `./verify`), `kit/commands/spinup.md` +
`kit/commands/retrofit.md` (greenfield and catch-up wrappers over the
ONBOARDING procedures — the retrofit command is the manual forerunner of
the kit-v2 retrofit path for the 42-project roster). Next kit items: the
STATUS writer (`write-status` + hook wiring), the survey→manifest
scaffolder, first profiles.

## Target consumers / applications

- The user's first target project (shape TBD — organ count and CI choices to
  be sanity-checked against it before P2).
- Every existing project at the Claude root, via kit-v2 retrofits.
- Tonality: first retrofit of the INTEGRATIONS §3 responsibility model.
- **The daily-digest publisher** (separate project, user 2026-07-10): watches
  all development projects and produces a styled end-of-day progress summary
  for the user's website. A pure READ consumer of this repo's substrate —
  traces/, DECISIONS, ROADMAP phase status, git history — which makes it the
  first external consumer-driven contract on the kit's status surface: its
  intake brief should specify exactly what machine-readable status every
  project must expose, and that spec lands in kit-v2 core (a STATUS
  artifact). Shares SCAN mechanics (hash ledger, skip-unchanged) with the
  audit loop and README sweeper; obeys writes-stay-home (never commits to
  watched repos). Overlaps the governor's STATUS.md duty — the digest should
  be a *rendering* of the same data, not a second collector.

**VSM amendment queue (Decision 47 — each item is a separate human
ratification; vocabulary is adopted, machinery is not):**

- **A. S4 freshness + open-PR surfacing in monitor** — `S4-STALE` WARN when
  the newest research artifact / unmerged `landscape-audit/*` branch exceeds
  ~35d, and open PRs in this repo reported as obligations on the human.
  Earned by: PR #2 (the 2026-08 audit) sitting unsurfaced four days.
- **B. "Outside & then" section in STATUS.md** — last audit date, unconsumed
  findings, next run, beside the health rows.
- **C. Environment-watch remit in the landscape-audit prompt** — protocol
  cadence, platform shifts (TCC class), provider policy, CI pricing.
- **D. Algedonic cloud check** — weekly scheduled cloud job, deterministic
  script, GitHub-visible pain only (red default-branch CI, leak_scan on
  public-repo clones), notify on HIGH alone. Earned by the 19-day public
  leak. Local-only pain explicitly out of scope.
- **E (adopted with 47, listed for symmetry): non-adoptions** — no standing
  S4 agent, no resource-bargaining machinery ahead of a running fleet, no
  five-box build-out, no new doctrine tenet.

Full mapping: research/2026-08-14-viable-system-model-mapping.md.

**Human TODO surface — one list of everything in the fleet waiting on the
human (Decision 50, path queued 2026-08-15; human-directed):**

The signals ALREADY exist, scattered across six mechanisms, and nothing
aggregates them into the one question that matters to the person running
this: *what is waiting on me?* Measured at the moment of writing — 8
manifests sitting PROVISIONAL awaiting ratification, surfaced by nothing;
1 open PR; 0 overdue balls (only because ball_scan now exists); 2 uncommitted
mailbox writes; 4 pushes held. In VSM terms this is the S3→S5 channel: the
fleet already attenuates 65 repos into severity rows, but the *human's*
obligations are not a severity class, they are a distinct signal that today
leaks out through the sweep as INFO/WARN noise or not at all.

Path, each rung earned by the one before it:

- **T0 — collector (deterministic, in the governor).** `todo_scan.py`
  reads the existing signals — `ball_scan` (balls on us / overdue),
  `s4_scan` (open PRs, unmerged audits), manifest `status` (PROVISIONAL /
  awaiting ratification), `dormant.review_by` expiries, `LEAK`-class HIGH
  findings, uncommitted mailbox writes, unpushed commits on public repos —
  and emits ONE list with a stable schema: `{source, repo, item, since,
  action, urgency}`. Nothing new is detected; everything is re-read through
  the lens "does this need a human?" Renders as its own STATUS.md section
  and the session brief. **Gate:** every item on the list is something the
  human, not an agent, must do — no agent-actionable item may appear (that
  is the leak_gate of this surface: an agent chore on the human's list
  trains the human to skip the list).
- **T1 — schema + STATUS-surface contract.** The list becomes a
  `todo.1` artifact alongside `status.1`, so consumers render rather than
  re-collect. **This is where dispatch enters** — a "waiting on you" block
  in the daily digest is a *rendering* of `todo.1`, never a second
  collector (dispatch's own E-phase rule). Requires the `status.1` writer
  gap (Decision 45) to close first, or `todo.1` is the second contract with
  zero producers.
- **T2 — project-level TODOs.** Today the fleet-level signals are
  protocol obligations. Per-project TODOs (a ROADMAP phase gated on a human
  ruling; a DECISIONS "open question" awaiting the human) need a
  declaration form — likely a `human_gate:` field on a ROADMAP phase or a
  manifest `open_rulings` list — so residents can raise their hand in a
  shape T0 can read. Ratify the field shape before any repo writes it.
- **T3 — the loop closes.** Marking an item done is *the human doing the
  thing* (merging, ratifying, pushing) and the next sweep observing it gone
  — never a checkbox. Assert the effective state, not the declared one (kit
  gate rule): the TODO list has no "done" button by construction.

Non-goals, stated: no AI in the collector (deterministic by contract, same
as monitor); no per-item nagging or notifications beyond the existing
session brief + algedonic channel; no separate task tracker — the fleet's
files ARE the tracker, this is a lens over them.

**Phase K — Kit currency: one structure at every level (Decision 51,
human-directed 2026-08-17). Six items, ordered by dependency; each gated.**

The human's directive, restated as the phase's purpose: *a human should
learn ONE structure and one command set, and it should hold at every level
of abstraction — session, project, group, fleet.* Everything below is
sequenced so the later items have something concrete to stand on; the last
item is the philosophical frame, deliberately last, because a frame written
before the mechanisms exist is a frame written about nothing.

- **K0 — Kit version, declared.** `kit/VERSION` (semver) + `kit_version` in
  every scaffolded manifest + a `kit/CHANGELOG.md` where every entry names the
  retrofit action it implies. **Why first:** "catch this repo up" is
  unanswerable without a version to catch up TO — today the only way to know
  a repo is behind is to re-derive it (the wrapper-registry failure again:
  no declaration, so drift is invisible until collision). *Gate:* sweep
  reports `kit_version` per repo; a repo with none reads as `pre-K0`, never
  as current.
- **K1 — `/retrofit` rebuilt around K0.** The five behaviours it has are
  right (infer-first, plan-then-pause, append-never-rewrite, never-hide-red,
  the override clause) and are KEPT verbatim; what changes is that it now
  reads the target's `kit_version` and applies CHANGELOG entries in order —
  a *migration*, not a re-scaffold. Idempotent by construction: re-running on
  a current repo is a no-op. Adds the session-boundary artifacts (K3) and
  the ingest structure (K2) as migrations. *Gate:* re-run on a just-retrofit
  repo produces zero diff.
- **K2 — Uniform external-ingest structure.** The human workshops ideas in
  fresh Claude sessions and downloads recommendations, specs, and prototypes
  into repos with no known landing zone. Standard: `intake/` at repo root,
  `intake/README.md` stating the contract, one subdirectory per drop dated
  `YYYY-MM-DD-<slug>/` with the source file(s) untouched + a `PROVENANCE.md`
  (where it came from, which session/model, human's one-line intent) — the
  provenance tenet applied to inbound artifacts, since an undated
  unattributed spec in a repo is indistinguishable from an injected one.
  Contract: **`intake/` is read-mostly and never authoritative** — a resident
  *promotes* from it into ROADMAP/DECISIONS/specs by explicit act, and the
  drop stays as the citable original. HYPERSAW already does this ad hoc
  (dated ingests named in CLAUDE.md as "they ARE the reference"); K2 makes
  it uniform. Gate check in `./verify`: every `intake/*/` has a
  `PROVENANCE.md`. *Gate:* one repo runs it end-to-end (drop → promote →
  cite) before it ships in the kit.
- **T4 — flip `cites_missing` from reporting to blocking** once every open
  thread's opening file carries `cites:` (Decision 67). Read-only count:
  `python3 -c 'import sys;sys.path.insert(0,"governor");import ball_scan;print(len(ball_scan.cites_missing(".")))'`.
- **K3 — Session-boundary commands** — *core BUILT 2026-08-18* (shared routine
  `kit/session/state.py`, registry `kit/session/registry.py`, and all three
  commands installed; 9 tests in `./verify fast`). Remaining before the gate
  closes: the human names the registry location (`KIT_SESSION_REGISTRY` — the
  brief proposes the private website repo both machines pull), and one full
  open→close cycle runs on this repo with STATUS.json validating against
  dispatch's fixtures. `/breakdown` as `status.1`'s first producer is NOT yet
  built — SESSION.md ships first, STATUS.json follows. The ecosystem-level
  fan-out (brief §7 step 7) shipped EARLY as `/closeout` +
  `kit/session/batch_close.py`, because 39 repos needed closing the day the
  per-repo commands landed; it closes only what can be closed HONESTLY
  (33 mechanical) and hands back the rest (10 needing a human).
  (briefs/2026-08-17-session-boundary.md,
  proposal ratified in chat): shared read+render routine → `/reorient` →
  registry (dedicated private repo; existence-only rows keyed by session_id;
  named INTEGRATIONS §3 exception) → `/wakeup` → `/breakdown`. `/breakdown`
  is `status.1`'s FIRST PRODUCER (closes the Decision 45 gap);
  `REFLECTIONS.md` is the new root artifact, feeding DECISIONS/ROADMAP/
  LIBRARY by graduation. Commit yes, push no. *Gate:* one full open→close
  cycle on this repo with STATUS.json validating against dispatch's fixtures.
- **K4 — Currency audit + fleet catch-up.** Once K0–K3 exist, ONE sweep
  answers "which repos are behind, and by which entries." Read-only first
  (report), then catch-up in reviewed batches — never a swarm, per the
  no-oracle-no-swarm rule: a repo without `./verify` cannot be gated on the
  thing being installed. *Gate:* the currency report + a batch plan the
  human ratifies.
- **K5 — Routines: daily/weekly fleet coordination.** *Next after the rename
  (Decision 68).* Concrete first target: the Threads Board and Session Board
  republished on a cadence and on merge-touched-`integrations/`, not only at
  the resident's boundaries. The pieces exist
  (monitor, ball_scan, s4_scan, algedonic, session brief); K5 is the
  *cadence* and the *rendering*. Daily: the sweep + T0 human-TODO (Decision
  50) rendered into the session brief and, via dispatch, the digest.
  Weekly: algedonic (already cron), currency report (K4), open-session
  registry age. **Constraint carried from Decision 42:** local sweeps run
  from session hooks (TCC), remote ones from Actions; nothing scheduled
  needs Full Disk Access. *Gate:* one week of routines producing artifacts
  the human actually read — measured by the human, not asserted.

**Also opened by this directive, NOT in Phase K:**
- **The file-restructuring sweep is back on the table** — the human's own
  reasoning: a clean layout "translates optimally to the other computer."
  Still Phase 0–4 as designed (worktrees → registry → move → venvs → retrofit);
  now sequenced AFTER K4, since a currency audit before the move would be
  audited against paths that then change.
- **Phase R — Recursive VSM: the philosophical frame.** Its own phase, as
  the human said. Prior-art bookend FIRST (Beer, Ashby, Espejo, the
  Cybersyn record, plus modern recursive-governance and "one grammar at
  every level" systems — Nix/Guix, Kubernetes operators, Unison, capability
  systems). Then the frame: what is invariant across levels (the command
  set, the artifact set, the gate rule), what is per-level (the S1
  content), and the rule for when a level earns its own metasystem vs
  borrows the parent's. K0–K5 are the empirical material this frame is
  written FROM; writing it first would be inventing. *Gate:* the frame
  document + a demonstration that `/wakeup`/`/breakdown` run unchanged at
  fleet level over registry rows (the brief's §7 item 7).

## Deferred / demoted

- **Live agent-to-agent messaging** — deliberately excluded; published
  experience shows it is the most fragile layer and unnecessary at 3–8 agents
  (research/2026-07-10-coordination-isolation.md). Revisit only if the task
  ledger provably cannot express a needed interaction.
- **Beads-vs-minimal-ledger decision** — deferred to P2 when the ledger is
  actually needed.
- **Conductor substrate decision** (cron + headless `claude -p` vs
  agent-teams/Workflow vs supervisor daemon) — deferred to P0 entry.
  Prior art reviewed 2026-07-11: **fleet**
  (github.com/sermakarevich/fleet, surfaced by the user from the audit's
  blocked HN link) — a working supervisor-daemon existence proof (Beads/
  Dolt centralized queue, headless multi-backend coders, web UI). Mechanisms
  worth adopting whatever substrate wins: per-task artifact dir
  (PLAN_AND_STATUS.md + KNOWLEDGE.md ≈ our handoff + journal), context-
  pressure termination (~90% of window → end the shift; mechanizes our
  fresh-context rhythm), and a durable `ask_human` question queue surfaced
  to the human's channel of choice (the "escalation is cheap" principle as
  infrastructure). Constraints per Decision 16: no auto model-tier swaps;
  no threat-analysis add-ons.
- **Relocating the leaf knowledge-loop prompt into the agent-knowledge-loop
  repo** (it is that system's Level 0) — pending user decision; canonical here
  until then.
- **Global daily README-refresh loop** — a second global agent (cron,
  audit-loop-style: hash-ledgered, skip-unchanged, propose-or-apply) that
  sweeps repos whose content changed and refreshes their READMEs per the
  clarity standard. User floated 2026-07-10; deliberately parked — overlaps
  the curator's README duty (DESIGN §4b), so decide after P3 whether it's
  the curator generalized across repos or a separate lightweight sweeper.
- **Landscape audit (meta-audit of the protocol itself)** — a scheduled
  research pass (recommend monthly, not weekly: consensus moves slowly and
  research fan-outs are expensive) that re-surveys the external landscape and
  recommends protocol changes. Shape: the audit loop's mechanics pointed
  outward — a ledger in research/BIBLIOGRAPHY.md of per-topic last-checked
  dates; fan-out research agents, one per doctrine tenet / protocol area;
  diff findings against doctrine/ + DESIGN.md; output a dated
  `research/proposals/<date>.proposal.md` (propose-only — doctrine changes
  are NEVER auto-applied; human ratifies, DECISIONS records). Each run
  appends its sources to the bibliography. Complements kit-v1's
  GOVERNANCE.md config-review idea ("when new models resolve constraints,
  delete old guardrails") — deleting stale doctrine is an explicit output,
  not just adding. **Deployment recommendation (2026-07-10): a scheduled
  CLOUD routine, independent of P0 plumbing** — its inputs are web + this
  GitHub repo only, and its output is a PR (the propose-only staging buffer,
  mechanically enforced). Boundary rule for all routines: cloud for
  web+GitHub-input work; local cron for anything touching the local project
  tree (audit loop, distillery sweeps, dispatch collection). Run zero:
  2026-07-10 (this repo's founding research; bibliography is the ledger).
  **LIVE 2026-07-10 as a CLOUD routine** running
  `routines/landscape-audit.cloud.prompt.md` (the single canonical
  definition; monthly on the 10th). Output: branch
  `landscape-audit/<YYYY-MM>` → PR with
  `research/proposals/<date>.proposal.md` (DELETIONS section required) +
  bibliography append. Propose-only; the PR is never merged by the routine.
  A local scheduled-task variant was tested once and retired same day
  (double-run risk eliminated); its blocked-request lesson is baked into
  the prompt's resilience section.
