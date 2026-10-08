---
brief: structural-caution
from: autonomous (resident integrator)
to: julian
ball: julian
date: 2026-09-26
status: triaged; unified plan ratified (Decision 78); conflict (a) ruled — gates earn blocking per gate (Decision 84); (b), (c) ruled 2026-10-08 (Decision 87); all five conflicts ruled; §5 questions remain
answers: 2026-09-26-structural-caution.md
---

> **Origin.** autonomous standing integrator, 2026-09-26, triaging the human's
> Structural Caution recommendation packet the same evening it was dropped.
> Reconciled against: Decision 77 (session oversight, ratified today),
> Decision 66 (agents push branches and open PRs), the 2026-08-17
> session-boundary brief §5 ("a session never blocks on bookkeeping"),
> `briefs/2026-09-19-gardener-loop-and-fence.response.md` (the Fence),
> `handbook/` (principles 6, 8, 9, 12). Hook claims checked against the raw
> Claude Code hooks reference (code.claude.com/docs/en/hooks) on the same day.

# Triage: Structural Caution

**Headline.** The packet and Decision 77 are the same system seen from two
ends. Decision 77 asks "is each live session in sync with the system?"; the
packet adds the question nothing here asks yet — "is the system's own
reference drifting?" — and a sharper account of how enforcement fails. Most
of it adopts cleanly. Five rows conflict with rulings already on record, and
those are yours. Recommendation: fold the packet into Phase O as one plan,
not a second one running beside it.

## 1. Claims verified

Every hook claim the packet's design rests on, checked against the raw
reference:

| Claim | Reference says | Verdict |
|---|---|---|
| Only exit 2 blocks; exit 1 proceeds | "Exit 2 means a blocking error"; exit 1 is "a non-blocking error and proceeds" | confirmed |
| A missing script (exit 127) fails open | other non-zero codes are non-blocking; the action proceeds | confirmed |
| A timed-out PreToolUse hook does not block | "doesn't block the tool call … don't count on a stalled hook to act as a gate" | confirmed |
| SessionStart / SessionEnd cannot block | exit-2 table: "Can block? No" for both | confirmed |
| `TaskCompleted` can block | "Prevents the task from being marked as completed" | confirmed — **but** it fires only when a task is closed through the task list or by an agent-team teammate, so it enforces "passing ≠ done" for task-list work only, not for ordinary sessions |
| `ConfigChange` can block a settings change | "Blocks the configuration change from taking effect (except `policy_settings`)" | confirmed |
| Hooks fire inside subagents | "also run inside subagents" | confirmed |
| `disableAllHooks` exists; only managed settings resist it | confirmed | confirmed |
| `stop_hook_active` guards Stop loops | present on Stop and SubagentStop input | confirmed — **plus** a default cap of 8 consecutive continuations, after which Claude Code ends the turn anyway. The packet's 25-iteration loop budget needs `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` raised, or it is really 8 |
| The `if` filter is best-effort; hard denies belong in permission rules | stated verbatim | confirmed |

**A finding in our own install, from the packet's gotcha list.** The two
O0 hooks installed today follow the fleet's existing pattern,
`[ -x "$f" ] && python3 "$f" || true`. For an observer that is correct
(fail open), but it means a moved or renamed hook disappears with no trace —
the packet's "mistyped path leaves the gate silently disabled", and this
repo's own L0002 one level up. The SessionStart self-test the packet
proposes is the fix; it is in the unified plan below as the first new step.

## 2. Adopt — compatible with everything on record

| Packet element | Where it lands | Why it fits |
|---|---|---|
| **Three tests for any mechanism** (skippable by forgetting? needs judgment? reports when fine?) | a design rule in `DESIGN.md` §4 and the handbook | the doctrine's AI/deterministic boundary turned on the oversight layer, as the packet says; "empty when healthy" is the cry-wolf lesson of Decisions 71 and 76 stated as a rule |
| **Hook self-test at SessionStart** (count expected hooks, check each is executable, log `hook-missing`) | new O0.5 | closes the silent-disable gap found above |
| **ConfigChange guard** on `user_settings` / `project_settings` (log every change; block `disableAllHooks`) | O0.5 | the nearest thing a solo operator has to a gate on the gates; confirmed to block |
| **`GATE-CHANGE:` token rule** — editing `./verify`, hook scripts, or a thresholds file requires a DECISIONS line with the token appended in this session | O0.5, report-first then deny (see §3a) | makes "gates never weakened" and "gate definitions outside the implementer's territory" checkable facts instead of review judgments |
| **Two classes only: interrupt and accrue** | O1 findings schema | maps onto Decision 77's severities: inform/warn accrue (plus a one-time in-session line), alarm interrupts |
| **Versioned `thresholds` file** per project plus a global default, itself a gate | O1 | budgets become data the engine reads and the monthly review edits, never code |
| **Setpoint audit** (Move 3): weekly, fresh context, three-list diff, silent when empty, interrupt on an unsigned setpoint move | new O3 | fills the gap Decision 77 does not cover. Advisory by construction: a model produces the diff, you answer it. Related to HYPERSAW's per-repo auditor (`/wakeup` Step 4b), which audits code debt, not setpoints |
| **Regulate the regulator** — monthly review of thresholds, hooks, permission rules only; tracked count of judgment-hooks; "budgets that never fired" list | O3 | handbook principle 9 made scheduled and fed |
| **Dashboard last, read-only, never the source of truth, empty when healthy** | O4 (Decision 77's O3) | consistent with Decision 77; adds the emptiness rule and the source-of-truth rule |
| **Life OS inverted build** — put a mostly empty reader online first; populate from what is produced anyway | the O4 brief to life-os-app / life-os-web | reduce-never-invent applied to process, as the packet says |
| **Cloud sessions need gates in project settings** | noted for the Fence and for any gate that must hold in the monthly landscape-audit routine | cloud sessions do not read `~/.claude/settings.json` |

## 3. Conflicts — rulings on record that the packet contradicts

Each of these is yours. The recommendation is stated, not applied.

**a. Blocking at launch vs report-only (Decision 77, ratified today).** Most
budget rows are interrupts that deny tool calls. Decision 77's authority
answer was report-only until a week of output has been seen. *Reconciliation
proposed:* each gate ships report-only, writing a `would-deny` line; once it
has fired correctly on a plant and logged a week with no false positive, it
flips to deny by a signed `GATE-CHANGE:` decision. That is the packet's own
Phase 2 gate ("at least one recorded deny per gate type") and its two-week
tuning window, applied per gate instead of all at once.

**b. Bookkeeping denies** — "first write denied until a wake-up marker exists"
and "first write in any repo denied while other sessions are open".
Since O0 both conditions are produced automatically: the start hook writes the
record before the first prompt, and the end hook closes it on every normal
exit, so the only open sessions left are crashes. Denying writes across the
whole fleet because a session crashed elsewhere contradicts your own
2026-08-17 brief ("a session never blocks on bookkeeping"). *Recommended:*
drop both denies; stale sessions accrue on the dashboard and inform the next
session in that repo.

**c. Unsigned decisions → deny `git push`.** Pushing a branch and opening a PR
is how work reaches your review (Decision 66); denying the push hides work
rather than stopping it. Separately, DECISIONS.md has no signature convention
to count: entries say "human ruling via poll" in prose. *Recommended:* add a
machine-readable `ruled-by:` marker to each decision's first line; unsigned
count past the threshold interrupts you by notification, and nothing is
denied.

**d. Scope by manifest paths** — deny writes outside declared paths. No
manifest declares paths today except composites' territories, so switched on
it would deny in almost every repo on day one. *Recommended:* report-only
until a retrofit step adds `scope.paths` to manifests; then eligible for the
flip in (a).

**e. Subagents denied at rung 1.** Correct by the doctrine's definition of
rung 1 (single-threaded). It would also deny the read-only Explore scout,
which rung-1 sessions use routinely. Folded into (a): report-only first, and
the week of data shows whether read-only scouts should count.

## 4. One plan, not two — Phase O revised

| Phase | From | Builds | Gate |
|---|---|---|---|
| **O0** — hands-off boundaries | D77 = packet Phase 1 (registry half) | *done today*: records opened and closed by hooks, stale rows swept, neutral machine label set | a week of self-closing records |
| **O0.5** — gates on the gates | packet Move 1, new | SessionStart hook self-test; ConfigChange guard; `GATE-CHANGE:` rule (report-first); per-repo append-only JSONL event log (packet Phase 1, log half) | each guard fires on a plant; a deliberately removed hook produces `hook-missing` |
| **O1** — engine, budgets, snapshot | D77 O1 + packet Move 2 | the eleven sync checks plus the budget table as findings; thresholds file; interrupt/accrue classes; snapshot | every check and budget fires on its plant, silent on a clean fleet |
| **O2** — delivery and staged interrupts | D77 O2 + §3a | in-session one-time lines; notifications on interrupts; per-gate flip to deny after its week | a week in which every delivered line was worth delivering, judged by you |
| **O3** — setpoint audit and regulator review | packet Move 3 + review, new | weekly fresh-context three-list diff; monthly review of thresholds and hooks, fed by accrue trends | one non-empty diff answered in DECISIONS; first review signs its changes |
| **O4** — dashboards | D77 O3 + packet dashboard section | standalone app here and the LifeOS fleet page, both empty when healthy, both read-only | with the fleet healthy, both render empty |
| **O5** — HALT | D77 O4 | human-armed per repo | deferred until O2's noise is measured |

The Fence (gardener brief, Workstream A) stays its own repo; its policy file
and this plan's thresholds file should share one format when both exist.

## 5. The packet's open questions, still yours

These follow the four rulings above and are best taken in a second poll:

1. **Notification channel** for interrupts. Today's only live one is GitHub's
   notification for the weekly algedonic workflow. Claude Code's
   `Notification` hook fires when Claude needs your input, not on arbitrary
   events, so a phone push needs a service. Candidates: an existing LifeOS
   channel, a Slack or Discord webhook, or a push service.
2. **Initial thresholds**: the packet's table for two weeks, or derived from
   the last month of git history first.
3. **Deferral** of a close: free with a reason (the packet's assumption), or
   a DECISIONS line. Less pressing now that closing is automatic.
4. **Registry and dashboard home**: stay under `~/.claude/` (current, local
   to each machine) or move to the private website repo (both machines see
   it; the neutral machine label is now set, which that move requires).
5. **Cloud and unattended projects** whose gates must be committed in project
   settings from day one.
6. **Harness-evolution loop and thresholds**: propose but never apply
   (the packet's position, and the gardener response's) — confirm.
7. **First repos** — moot for the registry (O0 runs everywhere); still
   useful for O0.5's per-repo event log. Suggested: this repo and one busy
   consumer (HYPERSAW).

## 6. Housekeeping done during triage

- O0 hooks installed in `~/.claude/settings.json` (backup beside it),
  dry-run end to end against a scratch registry.
- Seven stale records from before the hooks swept as `unclean`.
- `KIT_SESSION_MACHINE=Mac` set in the global settings environment: the two
  sessions opened today had recorded the hostname, which contains your name.
  The registry is local today, but §5 item 4 would make it a committed file.
- The packet moved to `briefs/2026-09-26-structural-caution.md`. Its
  "implementation roadmap" embed did not survive export; the phase list and
  acceptance criteria in the text are complete, so nothing is lost. Its
  phases are numbered 1–5 while one sentence refers to "Phases 0 through 2";
  the unified plan above supersedes both numberings.
