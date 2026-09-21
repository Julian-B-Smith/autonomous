---
brief: gardener-loop-and-fence
from: julian
to: autonomous
ball: autonomous
date: 2026-09-19
status: proposed
response_expected: brief-response with a spin-up survey, not code
---

# Brief: The Fence and the Loop

Two coupled experiments. They are ordered: the Fence is a precondition for running the Loop unattended.

- **The Fence** — deterministic pre-action authorization + snapshot/rollback sandboxing, so an agent can run for hours with no possibility of a destructive write outside its target repo.
- **The Loop** — an outer loop that reads the distillery's lesson stream, execution traces, and scores, proposes edits to harness code and doctrine, evaluates them against a fixed task set, and stages them for human-gated application.

Together these are the first named tools of Machine Horticulture: the fence that makes the garden safe to leave overnight, and the loop that lets it tend itself.

## Why now

The state of the art in Sept 2026 has converged on the harness as the binding constraint, not the model. The specific developments this brief responds to:

1. **Meta-Harness** (Lee et al., Stanford, arXiv:2603.28052, Mar 2026) — an outer-loop system that searches over harness *code*, with an agentic proposer that reads the source, scores, and execution traces of every prior candidate through a filesystem. Discovered harnesses beat hand-engineered baselines on TerminalBench-2. This is our distillery with a proposer bolted on and a scoreboard in front of it.
2. **Observability-driven harness evolution** (arXiv:2604.25850) and a community Claude Code plugin ("Harness Evolver") that evolves harnesses via multi-agent proposers + git-worktree isolation. Evaluate for patterns; do not install.
3. **Intent-taxonomy permission guards** ("nah", APort, Open Agent Passport spec, Mar 2026): tool calls mapped to intents (`filesystem_delete`, `network_outbound`, `lang_exec`, ...) and evaluated against a declarative policy *before* execution, with a signed audit record. Key claim: the same binary is benign or destructive depending on its arguments, so command-name allow/deny lists are not reproducible safety.
4. **Snapshot-fork microVM sandboxes** (Mitos and the checkpoint/rollback research line, e.g. DeltaBox) — clean isolated starting states per session, fork-and-branch execution. This is our tree-based branching-history principle applied to the whole execution environment.
5. **Anthropic's `sandbox-runtime`** — OS-level filesystem + network restriction for arbitrary processes. Lightest candidate for the fence's bottom layer.

## Doctrine constraints (non-negotiable)

- AI/deterministic boundary holds throughout: the proposer *proposes*; deterministic code decides what gets scored, applied, and rolled back. The authorization layer is deterministic code, never model-based screening.
- Oracle discipline: both experiments expose `./verify fast|full`. The Loop's evaluation set is itself gated — no proposal can weaken a gate, and a proposal that edits the evaluator is rejected by construction.
- Reduce-never-invent: every external project above is a *pattern source*, handled the way the `handoff` plugin was handled — transplant what survives our concurrency and file-canonical constraints, install nothing.
- Right-sized architecture chosen explicitly in the survey response, not defaulted.
- Model routing stays human-gated (Opus for proposer/judgment roles, Sonnet for scoped execution, Haiku for scout/verbatim).
- Writes stay home. The Loop may read across repos; it writes only to its own repo and to a staging directory that Julian promotes by hand.

## Workstream A — The Fence

### Goal
A containment layer that any project can opt into, such that an unattended session physically cannot: delete or overwrite files outside its target repo (worktree), make outbound network calls outside an allowlist, or execute a destructive git operation (force-push, branch delete, history rewrite) without a human token.

### Shape
Three layers, each deterministic, each independently testable:

1. **Pre-action guard** — a Claude Code hook that intercepts every tool call, classifies it into an intent taxonomy by *arguments* (not command name), evaluates against a per-project policy file, and either permits, denies, or holds for human confirmation. Every decision appended to a signed/hashed audit log in `traces/`.
2. **OS-level sandbox** — filesystem and network restriction on the process itself (evaluate `sandbox-runtime` first; fall back to container + network policy). This is the layer that holds when layer 1 is bypassed or misconfigured.
3. **Snapshot/rollback** — session starts from a snapshot; state is checkpointed at phase gates; any rollback is a branch, not an undo. Start with git worktrees + filesystem snapshots; note microVM forking as the upgrade path, not the first move.

### Acceptance criteria
- An adversarial test suite (`./verify full`) that attempts each forbidden action class through at least three different tool surfaces (bash, file-edit tool, subagent) and confirms every attempt is blocked at layer 1 *and* independently at layer 2.
- A trace exists for every intercepted call; the trace is reproducible from the policy file + the call.
- A clean session can be started, run a scripted destructive-attempt task, be rolled back to its snapshot, and diff to zero.
- The policy file is readable by a non-technical reader. This is a consulting artifact as much as a safety artifact.

### Non-goals
- No network listeners, no A2A, no cross-machine authorization — the earlier A2A verdict stands.
- No model-based "is this safe?" screening as a load-bearing layer. It may exist as advisory annotation only.

## Workstream B — The Loop

### Goal
An outer loop, run inside the Fence, that turns the distillery's append-only lesson stream into scored, staged proposals against harness code and doctrine — CLAUDE.md layers, slash-command prompts, hook logic, verify scripts, the spin-up survey itself.

### Shape
- **Scoreboard first.** Before any proposer exists, define a fixed evaluation set: 8–15 bounded tasks drawn from real recent work across at least three repos (a plugin build task, a refactor, a docs/README task, a retrofit). Each has a deterministic score and a cost/token budget. This is the hard part and the part most likely to be skipped. Without it the gardener is blind.
- **Proposer** reads, via the filesystem: all prior candidates' source, scores, and traces; the distillery stream; DECISIONS.md across repos. It proposes *one* bounded diff per iteration with a written rationale.
- **Evaluator** runs the candidate harness against the evaluation set in isolated worktrees, in parallel, inside the Fence. Records scores and cost.
- **Staging** — winning candidates land in `staging/` with a proposal record. Nothing is applied to global CLAUDE.md or any project doctrine without Julian's promotion. A `/promote` step (or extension of `/breakdown`) surfaces staged proposals at end of day.
- Every state in the search is a node in a tree; branches, never a linear list.

### Acceptance criteria
- Evaluation set runs end-to-end on the *current* harness and produces a baseline score and cost, reproducibly (seeded, no wall-clock).
- At least one full proposer→evaluator→staging iteration completes unattended inside the Fence with a complete trace.
- A proposal that attempts to edit the evaluator, weaken a gate, or write outside staging is rejected and the rejection is traced.
- A proposal that edits itself out of the audit log is impossible, not merely disallowed.

### Non-goals
- Not optimizing model weights, prompts-as-strings only (Meta-Harness's point is that the harness is *code*), or per-task prompt tuning.
- Not adopting LangGraph or any control plane; the earlier verdict (lightweight supervisor for single-project trials) stands unless the survey response argues otherwise with specifics.

## What I want back (the response)

A brief-response, not code, containing:

1. The spin-up survey answers for each workstream as separate repos (or a single repo with two organs — argue for one).
2. Explicit architecture rung per workstream from the three-rung menu, with reasoning.
3. A pattern-transplant table: for each external project named above, which patterns survive our constraints, which don't, and why. Same format as the `handoff` evaluation.
4. A proposed evaluation set for the Loop — task candidates, where they come from, how each is scored — so I can veto/replace tasks before anything is built.
5. A risk register. At minimum: sandbox-escape capability of current models (SandboxEscapeBench exists; assume the model can find holes), proposer reward-hacking the evaluator, cost blow-up from parallel evaluation, and my own tendency to skip the scoreboard and go straight to the proposer.
6. The first three phase gates for ROADMAP.md.
7. Open questions you need answered before spin-up.

Ball returns to me on delivery.
