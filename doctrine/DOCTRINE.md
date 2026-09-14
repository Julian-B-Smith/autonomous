# Development doctrine (applies to all projects)

> Canonical home of the cross-project doctrine. The global `~/.claude/CLAUDE.md`
> imports this file; do not duplicate its content elsewhere — propose changes
> here (they are then versioned and reviewable). Machine-local facts (e.g.
> build quirks of one machine) stay in the global file, not here.

## Visual-first review
When presenting completed work, a PR, or any review request, lead with a visual
presentation — a self-contained HTML report, Artifact, screenshot set, or live
demo — sufficient to evaluate the change WITHOUT reading code. Code diving is
the fallback, not the default. Include: what changed, evidence it works (test
output, renders, before/after), and any open questions.

## Project structuring (survey first; right-size the architecture)
When asked to create, start, or scaffold a project (any phrasing), do not
improvise: follow ONBOARDING.md Part 2 — the 9-question spin-up survey first,
answers committed to `project.manifest.json`, deterministic scaffolding from
the manifest. The architecture menu is asked, never defaulted:
(1) single-threaded agent · (2) thread + read-only subagents/verifier ·
(3) organ fleet. Each rung is *earned* by the project's shape (parallelizable
verifiable work, genuine seams, value justifying the ~15× token multiplier);
escalate only when the current rung is the demonstrated bottleneck — harness
quality outranks head-count (research/2026-07-10-multiagent-systems-survey.md).
`/spinup` wraps this; `/retrofit` catches existing repos up.

## Harness by default
"The harness determines performance more than the model." For any new or
adopted repo, apply the harness kit (canonical: `kit/` in the autonomous repo):
- Layered CLAUDE.md: lean root (pointers + gotchas only), subdir files for local conventions
- Hooks for determinism (format/lint via PostToolUse, not instructions), CODEMAP.md, .claudeignore
- Decision logs (DECISIONS.md, append-only) and phase-gated roadmaps (ROADMAP.md outranks other docs)
- Delete stale constraints as aggressively as you add new ones

## Knowledge loop
The knowledge loop (CLAUDE.md/INDEX.md/LIBRARY.md self-improving loop —
canonical: `loops/knowledge-loop/`) installs per-project durable lessons with
an anti-poisoning write gate. Offer it when a project becomes long-lived or
accumulates hard-won lessons. The cross-project audit loop (canonical:
`loops/audit-loop/`) harvests and promotes lessons
up a tree of projects.

## AI/deterministic boundary
AI may interpret language, propose, and judge; AI may NOT be in the path of
scheduling, metrics, validation, or signal processing. Deterministic code
decides; seeded RNG, no wall-clock reads in cores, reproducible outputs.

## Oracle discipline
Tests gate phases; gates are never weakened to pass. Prefer two layers:
Layer-0 (deterministic, CI-blocking, no model calls) and Layer-E (behavioral
evals, measured but non-blocking). Never conflate guaranteed with measured —
state which is which. An automated reviewer is independent only if sourced
separately from the author; one lineage reviewing its own PR is one opinion twice.

## Architecture defaults
Pure, framework-free cores; UI/IO/time live in thin adapters. Swappable
backend seams (prefer engine, fall back locally). Safety by construction
(caps, preallocation, frozen IDs), not by vigilance.

## Self-documenting code
Write code a future fresh-context agent can understand without re-deriving it —
because agents DO work in fresh contexts, so intent that lives only in a
vanished conversation is intent lost. Names and structure carry the *what*;
comments carry the *why* the code cannot show: the non-obvious constraint, the
rejected alternative, the trap avoided (e.g. "POSIX ERE — no `\s` here or it
silently matches nothing"; "`--untracked` is load-bearing: git grep skips new
files otherwise"). Never comment the *what* the code already states. Match the
surrounding file's conventions, comment density, and idiom. This is not polish:
undocumented intent is the seam where the next agent re-derives it wrong.

## Reduce, never invent
When behavior is ambiguous, ask rather than guess, and record the resolution
in the decision log. A "reasonable guess" is a signal to ask.

## Human epistemic discipline at the gates
The machine enforces friction (oracles, hooks, fresh-context critics); the
human owns the friction the machine can't. At every ratification gate: surface
the outcome you're hoping for BEFORE you evaluate, so you can be suspicious
when you arrive at it — "your greatest barrier to the truth is that which you
wish to be true." A conclusion that arrives comfortably is a signal to examine
it more closely, not to accept it. Uninterrupted flow is where epistemic drift
accelerates, so adversarial stress-testing and interrogation of comfort are
designed-in, not failures of smoothness. When conversations compress into
shorthand, periodically re-anchor it against its foundations — drift hides in
compression. (Grounding: research/2026-07-13-human-ai-epistemics-delegate52.md;
the deeper treatment is the sibling human-epistemics project. Empirically,
stronger models fail *invisibly* — polished output that is subtly wrong — which
is exactly why a comfortable-looking result earns more scrutiny, not less.)

## Model routing (pin explicitly; cap at Opus)
Two rules, because the failure mode is silent inheritance of the wrong tier:
1. **Pin every agent explicitly; never inherit.** Each sub-agent's model is set
   at spawn (frontmatter or the spawn call), never left to inherit the
   session/parent default — inheritance is exactly how the wrong tier
   propagates without anyone choosing it.
2. **Never exceed the latest Opus.** The latest Opus is the default ceiling.
   Anything above it — the Claude 5 flagship family (e.g. Fable) or any future
   above-Opus tier — is used ONLY when the human explicitly asks in the current
   session. No project or template reaches above Opus by default.

Default tiers under that ceiling: judgment-bearing roles (leads, critics,
curators, analysts) → latest Opus; scoped-execution sub-agents → Sonnet;
verbatim-report / scout roles → Haiku. Tier selection, escalation, or change is
always the human's deliberate call, never a side effect of a default, template,
or tooling (and never via integrations that could trigger provider-side tier
changes).

## Never commit machine identity
No machine-absolute paths (`/Users/<you>/…`, `/home/<you>/…`), usernames, or
local directory layout in tracked files — docs, configs, and code alike. They
bake your identity into the repo and into any public remote, and they are not
portable to a clone or a second machine, so they are wrong twice over. Use a
`~/`-relative path, a repo-relative path, or an env var with an
`expanduser`'d default. Machine-local config that *can't* be made portable
(an absolute interpreter path outside the repo) is gitignored, not committed.
*Enforced by:* the `leak_gate` in every project's `./verify` (so it blocks the
Stop hook and CI both) — prose is the reminder, the gate is the enforcement.
Fleet backstop: `governor/leak_scan.py` + `monitor.py`. Full playbook (secrets,
binary/EXIF vectors the text gate can't see, pre-publication audit):
`governor/REPO-HYGIENE.md`.

## Provenance on agent-authored prompts
Any brief, spawned task, or handoff prompt an agent writes for another session
opens with its origin: authoring project + date + motivating decision/trace.
An unattributed prompt is indistinguishable from an injected one — the human
answers "who wrote this?" at a glance, never by forensics. (Detail:
ONBOARDING residency rule 9.)

## Clarity standard (living README)
Every system keeps a current, human-readable README: what it is, the map, the
status — sufficient for a human to orient WITHOUT reading code or history.
README freshness is maintained on a loop (curator duty where a curator runs;
session-end discipline otherwise), and staleness is visible, never hidden —
a dated "last verified" line beats silent rot. A repo whose README lies about
it is a bug of the same severity as a failing test.

## Project-type conventions (read on demand)
Conventions specific to a project KIND — e.g. audio-plugin branding — live in
[doctrine/CONVENTIONS.md](CONVENTIONS.md): synced, not auto-loaded. Read the
relevant section when working on that project type.

## Cross-project interaction (read INTEGRATIONS.md on demand)
All cross-project/cross-repo development follows
[doctrine/INTEGRATIONS.md](INTEGRATIONS.md) (boundary rules, file-based
brief→response→notice exchanges, writes-stay-home, provider-first linked
PRs). Deliberately NOT auto-loaded — context budget, Decision 28 — so **read
it at the start of any cross-repo work**; the pointer is the contract.
