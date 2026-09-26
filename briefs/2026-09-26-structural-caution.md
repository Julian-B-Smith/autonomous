# Structural Caution — Recommendation Packet

Sep 26, 2026 · @Julian Beall Smith

## Brief

Recommendation: move caution in the agentic dev process from run-time repetition by Julian to design-time structure enforced by hooks, budgets and a slow audit loop, so his attention goes only to setpoints and exceptions.

This packet is a brief for the autonomous agent. It carries the reasoning from a design conversation on 2026-09-21 and 2026-09-26, a research pass on current hook and guardrail practice, and a phased order of work with acceptance criteria. It does not prescribe file layouts; the agent decides those against the existing doctrine.

Diagnosis in one paragraph: control systems break down when they need perpetual manual input from management. Operational errors are absorbed by redundancy and fast feedback. Errors at the top are not, because the top sets the reference signal the inner loops track. A lapse there is invisible from inside and compounds. The fix is not more caution from Julian but a different kind: ratchets set once, budgets checked by dumb code, and a pain channel that interrupts him only on breach.

## Diagnosis

The failure Julian describes is setpoint drift, not execution error, and the two need different regulators.

Ashby's law says a regulator needs as much variety as the disturbances it faces. A regulator that gets that variety from the manager at run-time, session after session, is a bottleneck dressed as a regulator: the moment the manager's attention drops, regulation stops, and nothing signals that it has. Julian's attention is the scarcest variety source in the system, and the current design spends it on repetition.

Why operational errors are cheap and top-level errors are not:

- An inner loop has a reference to compare against. A wrong edit fails `./verify`, a bad plan trips a gate. Redundancy and fast feedback absorb the error.
- The top *is* the reference. A drifted brief, a scope quietly widened, a gate weakened out of convenience: the inner loops track it faithfully. No component below can detect it, because to them it is the definition of correct.
- Drift compounds because every downstream decision is conditioned on it. By the time it is visible in output, many sessions of work sit on top.

The existing doctrine already handles the inner loops well (oracle discipline, `./verify`, gates never weakened). The gap is above them: nothing checks the reference against something outside the system, and the checks that exist there (wake-up, break-down, deciding which architecture rung, approving plans) are rituals Julian has to remember.

The Life OS stall is the same pattern in another domain: a scaffold designed completely first, then dependent on dedicated population sessions that require manual initiation. It stalled for the same reason the caution layer will if built the same way.

## Design principle

Change the kind of caution Julian supplies, not the amount: from run-time repetition to design-time ratchets plus exception handling.

Three roles remain his, and only these:

1. Setting setpoints: the brief, the scope, the acceptance criteria, the thresholds. Done once per project or phase, in writing, where the system can read them.
2. Handling exceptions: responding when the pain channel fires. Rare, and always about a specific breach.
3. Reviewing the regulator: a scheduled look at whether the gates and budgets themselves are still right. Monthly, not per session.

Everything else is either enforced by code that cannot be skipped, or measured by code and reported only on breach. Three tests for any proposed mechanism:

- Can it be skipped by forgetting? If yes, it is not enforcement. Move it into a hook or a precondition.
- Does it require a judgment call to evaluate? If yes, it cannot be checked by dumb code. Replace the judgment with a quantity and a threshold, and keep the judgment for the monthly review.
- Does it report when things are fine? If yes, it will be skimmed. Empty when healthy, loud when not.

This is the doctrine's own AI/deterministic boundary turned on the oversight layer: the AI (and Julian) interpret and propose; deterministic code decides whether the process may proceed.

## Move 1: enforcement by hooks

Every ritual that currently depends on Julian remembering becomes a precondition a hook checks, and the lazy path is always the safe path.

Claude Code hooks fire on a fixed lifecycle and several of them can block: `PreToolUse` blocks a tool call, `Stop` prevents the turn from ending, `TaskCompleted` prevents a task being marked done, `ConfigChange` blocks a settings change, `UserPromptSubmit` rejects a prompt. `SessionStart` and `SessionEnd` cannot block; they inject context and log. Hooks configured in settings also fire inside subagents, so a fleet inherits the gates. See [Hooks reference](https://code.claude.com/docs/en/hooks).

Mapping of current rituals to enforcement:

| Ritual today | Hook event | What the hook does | Evidence written |
| --- | --- | --- | --- |
| Wake-up at session start | `SessionStart` (startup, resume) + `PreToolUse` on Edit/Write | Injects state summary as context; first write is denied until a wake-up marker exists for this `session_id` | `wakeup` line in the hook log |
| Break-down at end of day | `SessionEnd` + `SessionStart` in any repo | `SessionEnd` cannot block, so it logs the session as open in the registry; the next `SessionStart` anywhere denies the first write until open sessions are closed or explicitly deferred | `open`/`closed`/`deferred` lines in the registry |
| Passing ≠ done | `TaskCompleted` | Runs `./verify fast`; blocks completion on red, or when no trace file was written for the task | `verify` line with exit code and duration |
| Plan approval needs green verify | `PreToolUse` on `git commit` / `git push` | Denies unless the log shows a green `./verify` for this repo within the last N minutes | same `verify` line |
| Gates never weakened | `ConfigChange` + `PreToolUse` on Edit of `./verify`, hook scripts, `thresholds` files | Blocks the edit unless a DECISIONS.md entry with a `GATE-CHANGE:` token was appended in this session | `gate-change` line, decision id |
| Architecture rung chosen, never defaulted | `PreToolUse` on the Agent tool | Denies spawning subagents unless `project.manifest.json` declares rung 2 or 3 | `rung` line |
| Scope stays inside the brief | `PreToolUse` on Edit/Write | Denies writes outside paths declared in the manifest; the reason tells the agent to add the path and a DECISIONS line first | `scope-expand` line |
| Containment for unattended runs | `PreToolUse` on Bash, plus permission deny rules | Denies destructive commands and anything outside the target repo; permission rules carry the hard denies, hooks carry the reasons | `deny` line |

Asymmetric friction is the design rule for every row: contracting is free, expanding costs a written rationale in DECISIONS.md, and the hook checks for the rationale rather than for Julian's approval. Approval is a judgment; the presence of a line with a token is a fact.

Implementation gotchas the agent must respect, all from the reference above:

- Only exit code 2 blocks. Exit 1 is treated as a non-blocking error and the action proceeds. Policy hooks exit 2.
- A `PreToolUse` command hook that times out does not block; the call falls through to the normal permission flow. Gate scripts must be fast and must never hang on network or on OneDrive placeholders.
- A mistyped script path leaves the gate silently disabled (exit 127, non-blocking). Every gate needs a self-test at `SessionStart` that fails loudly if any hook script is missing or not executable.
- The `if` filter on tool events is best-effort. Hard denies belong in permission rules; hooks add reasons and logging on top.
- `disableAllHooks` and `--settings` can switch hooks off from user or project settings. Only managed settings resist that. For a solo operator the mitigation is a `ConfigChange` hook that blocks the change and a `SessionStart` check that logs the hook count, so a disabled gate shows up in the log and on the dashboard rather than vanishing.
- Cloud sessions do not read `~/.claude/settings.json`. Gates that must hold on the VPS or in cloud sessions go in the project's `.claude/settings.json`, committed to the repo.
- `Stop` fires at the end of every turn, not at session end. Blocking it is for loops with a mechanical stop condition (the Ralph pattern), not for end-of-day rituals. Guard with `stop_hook_active` to avoid an infinite loop.

## Move 2: budgets, not judgments

Replace "be careful" with quantities dumb code can check, and give every quantity a threshold and a deterministic action on breach.

A budget without an intervention is monitoring, and monitoring is what Julian will skim. Current practice on runtime guardrails converges on the same shape: explicit versioned limits, and on breach a fixed action from a short menu: degrade to safe mode (read-only tools, no delegation, capped retries), require human approval, or terminate a run that is not making measurable progress. See [Oracle, Runtime budget guardrails for agentic AI](https://blogs.oracle.com/ai-and-datascience/runtime-budget-guardrails-agentic-ai). The three hard stops every loop write-up agrees on are a maximum iteration count, no-progress detection, and a spend cap.

The safety layer must be external and deterministic. Julian's harness-evolution loop lets the system propose changes to itself; the budgets that bound that loop must not be editable by it. Not another model, not another prompt.

Candidate budgets, first cut. Thresholds are starting points for the agent to tune against the log after two weeks of data:

| Quantity | Threshold (initial) | On breach | Class |
| --- | --- | --- | --- |
| Files touched since last green `./verify` | 8 files | Deny further Edit/Write until verify runs | Interrupt |
| Diff lines since last green `./verify` | 400 lines | Same | Interrupt |
| Minutes since last green `./verify` in an active session | 45 min | `TaskCompleted` blocks; Stop hook injects a reminder | Interrupt |
| Decisions in DECISIONS.md without a human-signed id since last signed one | 5 | Deny `git push`; algedonic notification to Julian | Interrupt |
| Subagents spawned per session vs. rung declared in manifest | rung 1: 0, rung 2: 6, rung 3: manifest value | Deny Agent tool call | Interrupt |
| Unattended run wall-clock without a snapshot | 20 min | Containment layer forces snapshot before next write | Interrupt |
| Iterations of a Stop-hook loop | 25 | Loop ends, run marked incomplete | Interrupt |
| Consecutive iterations with no change in verify result | 3 | Loop ends; no-progress flagged | Interrupt |
| Gate changes per month | 2 | Third one triggers the monthly regulator review early | Interrupt |
| Sessions open without break-down | 2 | First write in any repo denied until closed or deferred | Interrupt |
| Deferred break-downs in a row for one repo | any | Logged only; surfaces on dashboard | Accrue |
| Token spend per project per week | project manifest value | Notification at 80%; deny new subagents at 100% | Interrupt at 100% |
| Scope-expansion entries per project | any | Logged only; trend on dashboard | Accrue |
| Hook count at `SessionStart` vs expected | mismatch | Log line + notification | Interrupt |

Two classes only. Interrupt means a hook denies something or a notification reaches Julian's phone. Accrue means a line lands in the log and nothing else happens until the monthly review reads the trend. Anything that would need a third class is a judgment in disguise; keep it for the review.

All budgets live in one versioned `thresholds` file per project, plus a global default. The file is a gate: editing it goes through the `GATE-CHANGE:` token rule from Move 1.

## Move 3: setpoint audit

A slow outer loop, on its own clock, compares current trajectory to stated intent and emits a diff, because drift of the reference is invisible from inside the loops that track it.

The audit is a scheduled task (weekly to start) that runs against each active project with fresh context. Fresh context matters: an agent that has been building the thing shares its drift. Anthropic's own guidance on loops says the same for review: a checker with fresh context is less biased than the maker. See [Getting started with loops](https://claude.com/blog/getting-started-with-loops).

Inputs, all already produced by the doctrine:

- The original spin-up survey answers and `project.manifest.json` (the setpoint as first written)
- `ROADMAP.md` phases and gates (the setpoint as it stands now)
- `DECISIONS.md` since the last audit (how the setpoint moved, and whether each move was signed)
- The hook log for the period (what actually happened: scope expansions, gate changes, deferrals, breaches)
- The git log for the period (what was built)

Output is a diff, not a summary: three lists and nothing else.

1. Setpoint moved without a signed decision: places where the roadmap or manifest now says something the survey did not, with no DECISIONS line covering it.
2. Work outside the setpoint: commits or files that no roadmap item or decision accounts for.
3. Setpoint items with no work against them past their phase gate.

An empty diff produces no output at all. A non-empty one goes two places: a line in the hook log (accrue) and, when list 1 is non-empty, an algedonic notification to Julian (interrupt), since an unsigned setpoint move is the exact failure the packet exists to catch.

This is the interrogative work Julian says he is better at, arriving pre-chewed. He answers the diff, he does not produce it.

## Regulate the regulator

One deliberately manual touchpoint stays: a monthly review of the gates and budgets themselves, not of the work.

POSIWID cuts both ways. A system that removes Julian from enforcement also removes him from noticing when enforcement has gone wrong: a threshold that is now always breached and always deferred, a gate everyone routes around, a budget that blocks the wrong thing. The thing that slips is always the case nobody enumerated. So the review exists, but it is scheduled, scoped, and fed.

- Cadence: monthly, or early when the gate-change budget breaches.
- Scope: only the `thresholds` files, the hook set, the permission rules, and the audit's own inputs. Never the projects.
- Fed by the dashboard's accrue trends: deferral counts, scope-expansion counts, breaches per budget, and which budgets never fired (a budget that never fires is either right or dead; the review decides which).
- Output: `GATE-CHANGE:` decisions, signed. Each one is the only legitimate way a threshold moves.

The review is also where any hook the agent could not implement as deterministic code gets examined. A prompt-based or agent-based hook (both exist in Claude Code; agent hooks are experimental) is a judgment reintroduced by the back door. Allowed only where a quantity truly cannot be found, and listed by name in the review so the count of judgment-hooks is itself a tracked number.

## Life OS dashboard tab

The dashboard is a read-only pull surface for the slow loop, built after the enforcement layer, not before it, and it shows nothing that is fine.

Push vs pull. Enforcement (hooks, budgets, denials) never lives in a dashboard, because a dashboard only works if Julian remembers to look, which is the failure this packet is about. Breaches interrupt: a denied call, a phone notification, a first write refused. The dashboard is where the accrue class and the audit's history are read on a clock: before the weekly audit response and at the monthly regulator review.

What the tab shows, and only when non-empty:

- Open sessions without break-down, by repo, with age
- Per-repo time since last green `./verify`, only for repos over threshold
- Unsigned decisions count, only when over zero
- The last three audit diffs, in full
- Accrue trends: deferrals, scope expansions, breaches per budget, gate changes, over the last 90 days as a small chart per quantity
- Budgets that have not fired in 60 days, listed by name

What it never does: hold state, accept input, or act. It reads the append-only hook log and the session registry. If the dashboard is ever the source of truth for anything, the layering has failed.

Decoupling. The caution layer ships on hooks plus a log with zero UI. The tab is a later reader over that log. Life OS being stalled must not stall enforcement.

Inverted build for Life OS itself. The scaffold was designed complete in June and then depended on dedicated population sessions Julian had to initiate, and it stalled on exactly that. Resume it the other way round:

1. Put a page online now as a reader over whatever files exist, mostly empty. The hosting decision is forced by this step; pick the boring option, it is revisable.
2. Make the first content that flows in content Julian produces anyway without a session: the hook log, the open-session registry, the job tracker he already keeps.
3. Population of the remaining domains becomes a side effect of working, and each domain still empty is visible on the page as a gap rather than invisible in a folder.

That is reduce-never-invent applied to the process rather than to code.

Hosting note: the session registry was already planned to live in the private website repo so both machines see it. The dashboard reads the same repo. That makes the website repo the natural home for the tab, and the VPS decision is only about where the reader runs.

## Research notes

Current practice supports every move in this packet and adds a few constraints the design must absorb. Checked 2026-09-26.

**Claude Code hooks** ([reference](https://code.claude.com/docs/en/hooks), [best practices](https://code.claude.com/docs/en/best-practices)). Hooks run on a fixed lifecycle: per session (`SessionStart`, `SessionEnd`), per turn (`UserPromptSubmit`, `Stop`), per tool call (`PreToolUse`, `PostToolUse`), plus task, subagent, config, worktree and file-change events. Five handler types: command, HTTP, MCP tool, prompt, agent. Hooks merge across user, project, local, plugin, skill and subagent scopes and fire inside subagents. The blocking model is exit code 2 or a JSON decision; anything else is advisory. Two events matter most for this design and were not in the original conversation: `TaskCompleted` can block a task being marked done, which makes "passing ≠ done" enforceable at the task boundary, and `ConfigChange` can block a settings change, which is the nearest thing a solo operator has to a gate on the gates.

**Runtime budget guardrails** ([Oracle](https://blogs.oracle.com/ai-and-datascience/runtime-budget-guardrails-agentic-ai)). The consensus shape: limits are explicit and versioned; breach triggers a deterministic action from a short menu (degrade to safe mode, require approval, terminate); a limit without an action is only monitoring. Poorly tuned guardrails that fire at the first sign of pressure are their own failure, which is why this packet starts with generous thresholds and a two-week tuning window before the first regulator review.

**Loop engineering** ([Anthropic, Getting started with loops](https://claude.com/blog/getting-started-with-loops); [verification loops with skills](https://claude.com/blog/building-verification-loops-in-claude-code-with-skills)). Anthropic frames a loop as a re-fire rule, state between iterations, a verifier, and a budget, and recommends a reviewer with fresh context because the maker is biased toward its own patch. Completion must be mechanically verifiable ("exits 0"), and tasks that cannot be written that way are not suited to autonomous loops. This matches the doctrine's verifier-as-model principle and is the basis for running the setpoint audit in fresh context. The maker/checker split is also the argument against letting the harness-evolution loop touch its own budgets.

**Scheduled runs** ([loop engineering guide](https://blakecrosley.com/guides/loop-engineering)). Claude Code's scheduled tasks run without approval prompts, and the docs warn that a green run status does not mean the task in the prompt succeeded; the transcript has to be read. For this design that means the audit's output goes to the log and the notification channel, never only to the run status.

**Deterministic, external safety layer** ([AgentGuard](https://pypi.org/project/agentguard47/)). The strongest single point from the guardrail ecosystem: when agents write their own rules, the safety layer has to be external and deterministic, not another model or prompt. Directly relevant to the harness-evolution outer loop already briefed to the autonomous agent.

## Phased implementation

Containment and the log come first; the dashboard comes last, because nothing before it depends on it.

&#91;embedded content: implementation roadmap · 5 phases, 5 gates\]

Each phase ends at a gate that is itself a mechanical check, so the roadmap obeys the packet's own rule. A gate the agent cannot make mechanical is reported to Julian as an open question, not silently loosened.

Acceptance criteria per phase:

1. **Log.** One append-only JSONL hook log per project and one global session registry in the private website repo. Every session writes `wakeup`, `open`, and `closed` or `deferred` lines. Gate: five consecutive sessions across two repos with no missing lines.
2. **Gates.** The Move 1 table implemented as `PreToolUse`, `TaskCompleted`, `ConfigChange` hooks plus permission deny rules, in each project's committed `.claude/settings.json`. A `SessionStart` self-test that counts hooks and fails loudly. Gate: two weeks of log with no `hook-missing` line and at least one recorded deny per gate type, proving each fires.
3. **Budgets.** The Move 2 table as a versioned `thresholds` file per project with a global default; interrupt actions wired to hooks and phone notifications; accrue actions writing log lines only. Gate: the first monthly regulator review runs from the log and signs its threshold changes as `GATE-CHANGE:` decisions.
4. **Audit.** The Move 3 setpoint audit as a weekly scheduled task with fresh context per project, emitting the three-list diff to the log and notifying on an unsigned setpoint move. Gate: one non-empty diff produced and answered by Julian in DECISIONS.md.
5. **Dashboard.** The Life OS tab reading the log and registry, showing only non-empty items. Gate: with all projects healthy the tab renders empty; it holds no state and accepts no input.

Phases 0 through 2 are the containment-first work already on the autonomous roadmap, restated at the process layer. Phase 3 is new. Phase 4 unblocks Life OS by the inverted build in the dashboard section.

## Open questions

Decisions the agent should surface rather than make. Each is a setpoint, so it is Julian's.

- [ ] Notification channel for interrupts: phone push via Claude Code's Notification hook, a Slack or Discord webhook, or something already in Life OS? The algedonic channel is only as good as the thing that buzzes.
- [ ] Initial thresholds: accept the Move 2 table as a first cut for two weeks, or set them from the last month of git history before switching gates on?
- [ ] Deferral rules for break-down: is "deferred" a free action with a reason, or does it cost a DECISIONS line like any other expansion? The packet assumes free-with-reason, logged.
- [ ] Hosting for the registry and dashboard reader: the private website repo is the assumed home. Static page over a committed JSONL, or a small reader on the VPS? Boring option preferred; needs a pick.
- [ ] Cloud and unattended sessions: which projects will run there, so their gates are committed in project settings rather than user settings from day one?
- [ ] Whether the harness-evolution loop may propose threshold changes at all. The packet says it may propose but never apply; confirm or tighten.
- [ ] Which two repos run Phase 0 first. The registry only proves itself across more than one.

## Sources

- [Hooks reference, Claude Code docs](https://code.claude.com/docs/en/hooks)
- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)
- [Getting started with loops, Anthropic](https://claude.com/blog/getting-started-with-loops)
- [Building verification loops in Claude Code with skills, Anthropic](https://claude.com/blog/building-verification-loops-in-claude-code-with-skills)
- [Runtime budget guardrails for agentic AI, Oracle](https://blogs.oracle.com/ai-and-datascience/runtime-budget-guardrails-agentic-ai)
- [Loop engineering guide](https://blakecrosley.com/guides/loop-engineering)
- [AgentGuard, PyPI](https://pypi.org/project/agentguard47/)

Internal references the agent already holds: the fourteen Machine Horticulture principles, the Navigator's Handbook, the Gap Integration Schematic, and the containment-layer and harness-evolution briefs.
