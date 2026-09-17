# kit — Harness Kit v2 ("the harness factory")

**Status: to build.** Spec: [DESIGN.md §6](../DESIGN.md). Replaces kit v1
(frozen at [archive/kit-v1/](../archive/kit-v1/)) per user mandate.

Shape: **one core + composable agent-type profiles**, where
`scaffold <profile> <target>` is runnable by a human OR by an agent
bootstrapping its own type.

**Front door: the spin-up survey.** When a new project directory is created,
the scaffold conducts a standard, repeatable interview — a fixed question
list about scope — and writes the answers to a committed
`project.manifest.json`. Deterministic scaffolding then runs FROM the
manifest (AI conducts the interview; deterministic code applies the
templates — the AI/deterministic boundary applied to setup itself). The
manifest is re-runnable: change an answer, re-run scaffold, review the diff.
Draft question list (refine during the v2 build):

1. **What is it?** library/engine · app · service · pipeline · experiment
2. **Architecture rung** (the menu, never defaulted): single thread ·
   thread + subagents/verifier · organ fleet — with what earns each rung
3. **Domain core**: the hard exact logic an LLM must never own (drives the
   deterministic-boundary wiring and golden-oracle choice)
4. **Oracle shape**: strict pinned goldens vs invariants-only; CI matrix vs
   single-version smoke
5. **Second implementation planned?** (→ port-pin module)
6. **Consumers / is it a consumer?** (→ integrations channel + INTEGRATIONS
   policy wiring)
7. **Parallel audit thread earned?** (→ audit-thread profile)
8. **Knowledge-loop tags**: the 3–6 categories of hard-won knowledge worth
   accumulating here
9. **Lifespan & autonomy tier**: throwaway experiment vs long-lived; how much
   unattended operation is intended (drives governance strictness)

Each answer maps to a deterministic action (install module X, wire hook Y,
seed file Z) — the survey is the human-facing face of the manifest, and the
manifest is the machine-facing face of the survey. **Delivery:** each
question is one AskUserQuestion poll, and ratification of the resulting
manifest is one more (`kit/prompts/_human-gates.md`, Decision 74).

**ROADMAP rule — Prior Art bookends (Decision 30).** Every scaffolded ROADMAP
carries two standard phases: **Phase 0 — Prior-art landscape (agent swarm)**
before the design is committed, and a **pre-ship Prior-art & IP re-scan**
before any public release. Both fan out research agents; the late one adds a
patent/IP landscape pass for anything commercializable (VSTs especially — see
autonomous VISIBILITY.md on disclosure/patent timing). Findings land in
`docs/prior-art.md`, dated and cited. In the ROADMAP skeleton
([scaffold-agentic-harness.prompt.md](scaffold-agentic-harness.prompt.md)).

**Manifest rule — no status prose (Decision 28).** The manifest holds survey
answers + (for composites) the territory registry: near-static facts. Phase
state lives in ROADMAP.md ONLY; the manifest `status` field is just a
ratification date + `"see ROADMAP"`. A status paragraph in the manifest is a
second home for a fact ROADMAP already owns — it WILL drift (observed:
Orrery's grew to 447 chars re-edited in parallel with its ROADMAP).

**Gate rule — assert the EFFECTIVE state, never the DECLARED state
(autonomous LIBRARY L0001 + L0002; two-consumer signal, 2026-08-14).** Every
gate the kit ships or a project writes must prove the *result*, not the
*artifact that is supposed to produce it*. Two independent derivations in one
week, from opposite ends of the fleet: (a) `sshd -T` on a live box showed
password auth ON behind a script that had `sed`'d it off — the config *file*
was hardened, the *effective* config was not (cloud-init drop-ins are Included
first; first-value-wins). (b) A `git grep -E` gate using `\b` matched nothing
and would have shipped permanently green — the gate *existed*, it had never
*fired*. Same failure shape: reading the declaration where only the effect
counts. So: a hardening script asserts with `sshd -T`/`ufw status`, never by
grepping the file it wrote; a detector is proven by planting a known-bad and
watching it fire, a known-good near-miss and watching it stay quiet, THEN the
clean tree; a scheduled job is proven by the artifact's mtime moving, not by
`launchctl list` saying loaded (Decision 42). "Installed", "configured",
"present" are declared states. Only "fired", "refused", "moved" are effective.

**MCP-server retrofit check (LIBRARY L0003).** For a repo exposing an MCP
server, the SDK-2.0 question is NOT "does the import resolve" — a
try-2.x/fall-back-1.x shim makes it resolve on both. It is "does the server
touch anything beyond `@tool` and `.run()`?" The shim is safe only on that
shared surface; a server reaching into 1.x FastMCP internals passes the import
and fails at first call. Prove both ways (fresh 2.0 venv AND the old pin)
before dropping any pin.

**The architecture menu** (doctrine: right-size the agent architecture) is
question 2: single-threaded agent → thread + subagents/verifier → organ
fleet. The fleet is a visible option at the outset, never the default.
Profiles beyond `organ` install only on the rung that needs them.

- **Core layer** (every installation): layered CLAUDE.md + CODEMAP +
  .claudeignore; doctrine block + four-knowledge-systems firewall (from
  [scaffold-agentic-harness.prompt.md](scaffold-agentic-harness.prompt.md),
  canonical here); `./verify` contract (from [harness/](../harness/));
  ROADMAP + DECISIONS skeletons; **the knowledge loop, default-on**
  (Decision 11 — tags seeded from survey Q8; the write gate is the bloat
  safeguard, not absence of the loop); hook set (PostToolUse format/lint,
  SessionStart context, PreToolUse territory + HALT + destructive-op guard,
  Stop enforced-reflection + red-suite gate).
- **Profiles** (each = agent definition + permissions + hooks + CLAUDE.md
  template + memory seed + verify wiring + territory manifest): `organ`,
  `verifier`, `critic`, `scout`, `audit-thread`, `curator`, `watchdog`,
  `coherence-critic`, `conductor`. Each profile documents when it's earned,
  what it may never do, and its handoff artifact format.
- **CI is part of the core.** [templates/ci.github.yml](templates/ci.github.yml)
  → each repo's `.github/workflows/ci.yml`: GitHub Actions runs `./verify fast`
  mirroring the local Stop-hook gate ("CI mirrors the Stop hook"). It runs the
  project's ONE oracle in the cloud — not new checks. Ships with `/spinup`,
  added to existing repos by `/retrofit`. `verify full` runs in CI only where
  the runner supports it (audio-plugin `auval`/codesign is macOS-only + human-
  run → those repos CI `fast` only).
- **CI-minutes budget (Decision 31).** Only PRIVATE repos spend Actions minutes
  (free tier: 2000/mo; public repos unlimited). The template defaults
  economical: PRs + pushes-to-main only (not every branch push), `concurrency`
  cancels superseded runs, `paths-ignore` skips docs-only changes, and heavy
  macOS builds (~10× Linux minutes) stay OUT of CI (`full` is local/human).
  Watch the private + heavy (JUCE/C++) repos first — they are the drain.
- **INSIGHTS v2**: every prescription cites its evidence in
  [research/](../research/).

Known v1→v2 deltas already identified: reflection-trigger default is
mode-dependent (voluntary interactive / hook-enforced autonomous); the Stop
hook's "can't read the session" caveat is outdated (transcript access exists);
boundary constraints move from prose to PreToolUse hooks + CI linters.
