# ONBOARDING — replicating and working in this ecosystem

For a **human** setting up a new machine, and for an **agent** arriving in
any of these repos for the first time. This is a map with procedures — every
standard it mentions is canonical somewhere else and deep-linked; if this
file and a linked file disagree, the linked file wins.

*Last verified current: 2026-07-10.*

## The ecosystem at a glance

One standards repo governs; execution repos do the work; exchanges between
them are files, not conversations.

| Repo | Role | Remote |
|---|---|---|
| **autonomous** (this repo) | Standards: doctrine, integrations policy, harness kit, governor spec, ecosystem roadmap | github.com/Julian-B-Smith/autonomous |
| *(retired)* | The cross-project audit loop now lives in `autonomous/loops/audit-loop/` (Decision 58); its former repo is archived. |
| **distillery** | Global memory: append-only stream + analyst + distilled pool | github.com/Julian-B-Smith/distillery |
| **dispatch** | Daily progress publishing: collector → FACTS → digest → gated publish | github.com/Julian-B-Smith/dispatch |
| **ai-integration-methodology** | The human-epistemics sibling: the collaboration methodology + consulting offering | github.com/Julian-B-Smith/ai-integration-methodology |

Cross-repo sequencing: [ROADMAP.md → Ecosystem tracks](ROADMAP.md).
The design and its evidence: [DESIGN.md](DESIGN.md), [research/](research/).
The full orientation to layers/protocols/cycles: [README.md](README.md).

---

## Part 1 — As a human

### Setting up a new machine

1. **Clone the standards repo to the canonical path** (the doctrine imports
   assume it):
   ```bash
   git clone https://github.com/Julian-B-Smith/autonomous.git ~/Documents/Claude/autonomous
   ```
2. **Wire the global CLAUDE.md** — follow
   [doctrine/INSTALL-GLOBAL.md](doctrine/INSTALL-GLOBAL.md) (paste one block,
   verify a fresh session sees the doctrine). Machine-local sections of your
   global file stay machine-local; never copy them between machines.
3. **Clone the audit loop:**
   ```bash
   # (agent-knowledge-loop is ARCHIVED — its content is in autonomous/loops/audit-loop/)
   ```
4. **Clone the execution tracks:**
   ```bash
   git clone https://github.com/Julian-B-Smith/distillery.git ~/Documents/Claude/distillery
   git clone https://github.com/Julian-B-Smith/dispatch.git   ~/Documents/Claude/dispatch
   ```
5. **Optional — the weekly audit-loop cron.** Copy
   `autonomous/loops/audit-loop/audit-loop.config.example` →
   `audit-loop.config` (same dir, git-ignored, machine-local scopes), then:
   ```
   0 9 * * 0 $HOME/Documents/Claude/autonomous/loops/audit-loop/audit-loop.sh >> $HOME/Documents/Claude/audit-loop.cron.log 2>&1
   ```
   It is propose-only by design — it never mutates shared stores.
6. **Verify:** start a fresh Claude Code session anywhere; ask what the
   doctrine says about the AI/deterministic boundary; confirm the answer
   matches [doctrine/DOCTRINE.md](doctrine/DOCTRINE.md).

### Working day-to-day

- **You are the ratifier.** The system is built so agents propose and you
  decide at named gates: project manifests (phase-0 gates), integration
  briefs' responses, memory promotions (audit-run proposals), doctrine
  changes (landscape-audit proposals), and anything published or
  irreversible. Saying *no* is cheap and expected. **Every such gate reaches
  you as a poll** (the agent's AskUserQuestion), with a recommended option —
  a prose question is the agent forgetting the rule (Decision 74).
- **Where things are decided:** each repo's ROADMAP.md is its single source
  of direction; DECISIONS.md is the append-only record. If you decide
  something in conversation, it isn't decided until it's in those files.
- **Starting a new project:** ask an agent to run the spin-up survey
  ([kit/README.md](kit/README.md) — 9 questions) and scaffold from your
  answers. The architecture menu is question 2; a fleet is never the default.
- **Asking one project for something another owns:** that's an integrations
  brief, not a chat request — see Part 2's cross-repo section; the mechanics
  are identical for humans.

---

## Part 2 — As an agent

### Your first ten minutes in any repo here

Read, in order: `README.md` (what this is) → `ROADMAP.md` (what's next and
what proves it done) → `DECISIONS.md` (what's already settled — do not
re-litigate) → `CLAUDE.md` (your charter; §Domain holds the invariants a
critic will check you against) → `INDEX.md` if present (pull only matching
LIBRARY lessons). Then run `./verify report` to see the oracle's last state.

### Rules of residency (condensed; canonical sources linked)

1. **ROADMAP.md outranks everything**, including the conversation. Ambiguous
   or missing acceptance criteria? Surfacing that gap IS the deliverable —
   grounded refusal is a success class ([harness charter](harness/CLAUDE.md)).
2. **Oracle discipline** ([README §3](README.md)): `./verify fast` after any
   change set, `full` before closing an item; report output verbatim; red
   halts forward work; never weaken a gate without a recorded human decision.
   Passing ≠ done — done = green + acceptance criteria + trace written.
3. **Writes stay home** ([doctrine/INTEGRATIONS.md](doctrine/INTEGRATIONS.md)):
   never commit to a repo you're not resident in. One exception: filing
   exchange files in a provider's `integrations/<your-project>/` slot.
4. **Memory loop duty**: every project runs the knowledge loop
   ([README §4a](README.md)) — ORIENT before acting, REFLECT before ending;
   the write gate is strict (evidence + falsifier, prefer not writing over
   writing unverified; if nothing qualifies, write nothing).
5. **Provenance**: nontrivial claims cite file/line, a verify run, or a
   ROADMAP entry; merged changes get a `traces/` entry.
6. **Human gates**: deleting files, public-interface changes, editing
   `./verify`, new dependencies, anything §Domain protects, anything
   outward-facing (publishing, pushing to a remote that is not this repo's
   own) — stop and ask. **Git: `add`, `commit`, `switch -c`, and
   `push -u origin HEAD` on your OWN branch, then `gh pr create`, are yours;
   MERGING is never yours** (Decision 66). Finishing a piece of work means
   opening a PR, not leaving a commit on `main` for the human to find and
   push by hand — that is invisible work with no review surface. Canonical
   wording: `kit/prompts/_closing.md`. **Ask through a poll**, never a
   trailing question in prose: AskUserQuestion with the options and your
   recommendation (`kit/prompts/_human-gates.md`). If the harness denies
   your own-branch push, the repo predates kit 2.6.1 — name it and poll the
   fix; do not route around it or quietly hand the human the commands.
7. **Review beats are visual-first** ([doctrine](doctrine/DOCTRINE.md)):
   at any gate — phase close, ratification request, PR — lead with a visual
   presentation sufficient to evaluate the work without reading code; the
   diff is the fallback, never the ask.
8. **Respect the AI/deterministic boundary**: if you find yourself doing
   scheduling, metrics, validation, or collection "by judgment," stop — that
   belongs in code you should write instead.
9. **Agent-authored briefs carry provenance.** Any brief, spawned task, or
   handoff prompt an agent writes for another session states its origin in
   the first lines: authoring project + date + the trace/decision that
   motivated it (e.g. "Origin: distillery resident session, 2026-07-17,
   follow-up to ROADMAP decision 12"). In a multi-agent system, a prompt
   whose author cannot be identified is indistinguishable from an injected
   one — the human must always be able to answer "who wrote this?" at a
   glance.

### Working across repos (the integrations protocol, quickstart)

Need something from another project? File a brief at
`<provider>/integrations/<your-project>/brief.md` with frontmatter
(`id`, `status`, `ball`, `filed`, `respond-by`) — live examples:
[integrations/dispatch/brief.md](integrations/dispatch/brief.md),
[integrations/distillery/brief.md](integrations/distillery/brief.md).
The `ball:` field always names the one side that owes the next move. Never
wait blocked: ship a visibly-degraded placeholder behind the same interface
and proceed. Cross-repo changes land as two linked PRs, provider first.
Full policy: [doctrine/INTEGRATIONS.md](doctrine/INTEGRATIONS.md).

### Replicating the project structure for a NEW project (until kit v2 ships)

Shortcut: the `/spinup` command (installed per INSTALL-GLOBAL step 3) wraps
this procedure; the doctrine also instructs any session asked to "start a
new project" to land here. The procedure itself, mirroring what built
`distillery`/`dispatch` (use them as reference implementations):

1. Conduct the spin-up survey with the human ([kit/README.md](kit/README.md),
   9 questions, **each a poll**); write answers to `project.manifest.json`,
   marked provisional until ratified — and ratification is itself one poll
   (Ratify / Ratify with changes / Not yet), never a report
   ([kit/prompts/_human-gates.md](kit/prompts/_human-gates.md)).
2. Copy the harness: `autonomous/harness/.claude` → `.claude/`,
   `autonomous/harness/verify` → `./verify` (chmod +x) — the THIN template: it
   carries no gate code. Then vendor the kit-owned gates, which is what
   actually installs the leak gate:
   `python3 ~/Documents/Claude/autonomous/kit/kit_sync.py <repo>` (writes
   `.kit/kit-gates.sh` + `.kit/MANIFEST`, sha256-pinned). Never copy gate code
   into `./verify` — that is what produced ten drifted variants (Decision 65).
   Implement `fast()`
   with at least a structure/manifest sanity check — a green-from-day-zero
   oracle, honestly scoped, beats an aspirational red one.
3. Write `CLAUDE.md` from [harness/CLAUDE.md](harness/CLAUDE.md): the
   invariant layer verbatim, §Domain filled (what it is, stack, invariants,
   protected paths, verify targets — under ~60 lines).
4. Write `ROADMAP.md`: phase-gated, each gate an executable/checkable
   condition; open questions listed as blocking-ask-the-human.
5. Write `README.md` per the clarity standard ([doctrine/DOCTRINE.md](doctrine/DOCTRINE.md)):
   orientation without code-diving, a dated "last verified" line, status
   markers on anything unbuilt.
6. Install the knowledge loop:
   [loops/knowledge-loop/integrate-knowledge-loop.prompt.md](loops/knowledge-loop/integrate-knowledge-loop.prompt.md),
   tags from survey Q8.
7. `mkdir traces/` (+ pointer README), `.gitignore` (`.harness/`,
   `.claude/settings.local.json`), `git init -b main`, initial commit, run
   `./verify fast` — green before the first commit lands.
8. If it participates in the ecosystem: file its intake brief(s) with
   providers, and ask a resident of autonomous to register it in the
   ecosystem tracks (that's a ROADMAP edit — governor/resident-only).

### Composite projects (`/spinup --composite`) — one repo, N contract-bound modules

For a project that is one deployable made of several modules behind a shared
seam (a plugin hosting engines, an app with plugins, a monorepo of services
built together). Worked reference: `~/Documents/Claude/synthetic-worlds/Orrery`
(one VST, N sequencer engines behind an `IEngine` contract). This is the
**organ model applied intra-repo** — a territory is a subdirectory with an
enforced write boundary, NOT a separate repo. Bucket the modules together;
separate repos are only for independent products with cross-repo versioned
contracts (that's the INTEGRATIONS protocol, not this).

Differences from the standard procedure — the five moves:
1. **Promote the shared seam to "the contract."** The one document/interface
   every module imports (Orrery: `sequencer-studio-architecture.md`). Changes
   to it are contract-version events; freeze it for a build phase and gate
   edits behind a human.
   *The contract file may be a **versioned wrapper** over a normative source it
   does not contain.* The invariant is that exactly one file owns the
   **version** and the **freeze state** — not that that file holds the prose.
   When the seam is already documented somewhere canonical (a founding design
   doc, an ADR, an upstream standard), the contract file carries the version,
   the freeze, the change log, and a normative-source table pointing at it.
   Copying the prose in would put the same content in two places, which is a
   bug (README §8), and two copies of a contract drift until no consumer can
   say which text it pinned. Orrery never hit this because its contract was
   written *as* the contract; FOUNDATIONS did, because its seam was §2/§4/§5 of
   a constitution the human wrote first (foundations-001 §2, Decision 39).
2. **Root charter + one sub-charter per module territory.** Root `CLAUDE.md`
   carries the layer map + the rung path; each module's `CLAUDE.md` is lean,
   points at the root + contract, and its §Domain is that module's own spec.
3. **A `composite` manifest block** — the territory registry: `contract`,
   a `modules_dir` (Orrery: `engines/`), and one entry per territory
   (path, role, spec-or-null, prototype, status). This is the machine-readable
   source of truth for what modules exist.
4. **Record which doc wins where.** Composite projects accrete docs at
   different times (Orrery's first engine spec predated the contract); pin
   precedence in DECISIONS so no agent builds a superseded design.
5. **Rung 2→3 by default.** Prove the seam on ONE module single-threaded
   (shell + first engine), gate green, THEN parallelize the rest as organs
   (own territory + own verify). Composite structure is the strongest
   earned-rung-3 signal, but exercise the contract before trusting it.

Then, mechanically: put modules under `modules_dir/`; keep a
`modules_dir/_template/` sub-charter for intake; make `./verify` go RED on any
`modules_dir/<name>/` not registered in the manifest (the intake safety net —
nothing half-added). **Watch for contract findings during intake:** a module
needing a contract *variant* (Orrery's Kuramoto → free-transport) or a new
output kind (Torus → native pitch) is a contract-change proposal, not just a
new territory — record it in DECISIONS and gate its build on the change.

### Retrofitting an EXISTING project (catch-up scaffolding)

Shortcut: the `/retrofit` command wraps this. The greenfield procedure above
assumes an empty directory; an existing repo has value at risk and its own
conventions, so the retrofit differs in four load-bearing ways: **infer
before asking, plan before writing, append never rewrite, and never break
what works.**

1. **Gap survey (read-only).** Derive the repo's current harness status
   (the sweep's checks: CLAUDE.md, `./verify`, ROADMAP, DECISIONS,
   INDEX/LIBRARY, traces/, manifest, `.claude/` hooks+agents); detect the
   stack and existing test/lint/format commands; read the existing README,
   docs, and TODOs for implicit roadmap content. Produce a gap table:
   present / missing / present-but-nonconforming.
2. **Survey with inference.** Conduct the 9-question spin-up survey
   ([kit/README.md](kit/README.md)), but propose answers inferred from the
   code (what-is-it, stack, domain core, consumers) and ask only what code
   cannot show (architecture rung — still never defaulted — oracle-shape
   preference, lifespan/autonomy, knowledge-loop tags). Answers land in
   `project.manifest.json`, noted as a retrofit.
3. **Plan, then PAUSE for approval.** List every file to create vs modify
   before writing anything. Unlike greenfield, this pause is mandatory —
   an existing repo is someone's working state.
4. **Apply, gap by gap, non-destructively:**
   - Existing files are appended to between `<!-- MARKER -->` blocks, never
     rewritten or reordered; on any contradiction between the template and
     existing content, the existing content wins pending a human ruling.
   - `./verify` WRAPS the repo's existing test/lint commands — never
     replaces its test setup. **Red-suite honesty:** if existing tests are
     currently red, do not gate on them and do not delete them — `fast()`
     runs the currently-green subset, and the red set is recorded in
     ROADMAP as explicit debt with its own phase gate. Retrofit never
     weakens an existing check; it may only quarantine-and-record.
   - ROADMAP absorbs existing TODOs/plan docs (migrate content, leave
     pointers at the old locations); DECISIONS starts with the retrofit
     itself as entry 1 unless history makes earlier decisions certain.
   - Then as greenfield: traces/, knowledge loop (tags from survey),
     README brought to the clarity standard with a dated last-verified
     line.
5. **Verify + close.** `./verify fast` green; re-running the retrofit is a
   no-op (marker-idempotent); briefs filed if the project is a consumer or
   provider; one trace entry for the whole change; report at a review beat
   (visual-first: the before/after gap table is the artifact) with the
   manifest for ratification.

**Foreign scaffolds (exported kits) — the override clause.** A repo may
arrive with a scaffold exported by another Claude session (its own
verify-like script, CLAUDE.md conventions, task files, hooks) that overlaps
this ecosystem's kit. Reconcile by one rule: **standard mechanisms, project
substance.** For any *function* the kit provides — oracle/verify dispatcher,
charter layout, ROADMAP/DECISIONS formats, knowledge loop, hooks, CI
workflow, leak gate — the kit's version REPLACES the exported one: two
half-compatible mechanisms is drift by construction. But the exported
scaffold's project-specific *substance* is preserved and **migrated into the
standard slots before anything is deleted**: domain invariants → charter
§Domain · plans/tasks → ROADMAP · recorded choices → DECISIONS · hard-won
notes → LIBRARY seeds · bespoke checks → targets inside the standard
`./verify` (never dropped — a bespoke check is often the most valuable thing
an exported kit carries). Anything that fits no slot is surfaced to the
human, not silently discarded. **Map first, replace second, delete only what
has been mapped.**

### What not to do

- Don't edit doctrine in any global CLAUDE.md — propose changes in this
  repo (versioned, reviewable).
- Don't copy canonical content into a second editable location — link it.
  Same content in two places is a bug ([README §8](README.md)).
- Don't add memory outside the loop's write gate, don't broadcast lessons
  (proliferation is the curator's targeted job), and never expose
  distillery's raw stream to a working context.
- Don't escalate the architecture rung because parallelism sounds faster —
  the burden of proof runs the other way (Decision 8).

---

## Replication checklist (the short version)

**Human, new machine:** clone autonomous → INSTALL-GLOBAL → clone
agent-knowledge-loop → clone tracks (needs remotes) → optional cron →
fresh-session doctrine check.

**Agent, new repo:** README → ROADMAP → DECISIONS → CLAUDE.md → INDEX →
`./verify report`; then work the top ready ROADMAP item under the rules of
residency.

**Agent, new project:** survey → manifest → harness copy → charter →
phase-gated ROADMAP → README → knowledge loop → git init + green verify →
briefs + track registration if ecosystem-facing.
