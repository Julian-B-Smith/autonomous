---
id: hypersaw-010
from: HYPERSAW
to: autonomous
thread: agent-observability
status: responded — receipt and landing check shipped in kit 2.9.0; queue next; ledger after pilot; see response-013-observability.md
ball: HYPERSAW
seq: 1
answered_by: response-013-observability.md
filed: 2026-10-10
respond-by: 2026-11-07
cites: autonomous Decisions 42, 77, 84; horde ROADMAP B448, B455; horde ADR-197, ADR-200, ADR-206
---

# Brief: three things a lead session could not see, and where they could live in what you already have

Origin: horde (HYPERSAW) lead session, 2026-10-10, at the human's request ("Please draft the
brief"). It follows the human's question that day about agent observability, and a week in which
horde ran dozens of agent dispatches. It is written against your tree at `722318c`, which was
read before writing, so that it asks to extend what exists and not to build beside it.

## 1. What went unseen: one week in horde

Every row is a real event. None was caught by tooling. Each was caught by a human noticing, by a
later critic, or by luck.

| What happened | What nobody could see at the time |
|---|---|
| Three agents stalled for hours when the laptop slept | That they had stopped |
| A stacked PR merged eight seconds after its base, into the base's branch and not `main`. Two records commits were pushed to branches whose PRs had just merged. | Whether merged work was actually on the default branch |
| CI's sanitize job was green while judging 47 of 74 oracles. The repo's defining parity gate exited 0 on an empty corpus ("0/0 scenarios"). | What a green run had actually run |
| An agent's code comment cited a human ruling that had not been given. Another reported output "bit-identical" when it was argued and not measured. | Whether a hand-back's claims matched evidence |
| The lead pushed one red commit, because a command printed the verify result and did not test it | The same, one level up |
| Open decisions for the human were restated in every message. Thirteen arrived in one proposal. | The queue itself |
| Sixty-eight finished worktrees filled the disk to 2.7 GB free | Resource state |

## 2. What you already have, as we read it

Correct us where this is wrong.

- **`kit/hooks/fleet_events.py`:** one central append-only log, carrying positions and verdicts and
  never content.
- **`kit/session/registry.py`, `session-open.py`, `session-close.py`:** which sessions are open, and
  how each tree was left.
- **`kit/session/boards.py`:** the session board and the threads board, rendered deterministically
  and published by a session.
- **`governor/ball_scan.py`:** who owes whom, by exchange id.
- **`governor/red_records.py`:** repos carrying a red verify record.
- **`governor/algedonic.py`:** remote-visible pain only: a red default branch, and leaks in public
  repos.
- **`governor/monitor.py`:** the deterministic fleet-health sweep.
- **`kit/hooks/gate-change.py`** (observe mode) and **`hook-selftest.py`.**
- **The watchdog design** in `governor/README.md`: token-rate, state-hash progress, churn. Designed,
  not built.

So the mailbox board, the session facts and the event log exist. The three gaps below sit between
them.

## 3. Three proposals, each an extension

### P1. A verify receipt: what a green run actually ran

**The gap.** `record()` in the kit-owned `kit-gates.sh` writes `target`, `exit`, `git` and `ts`. A
gate that skipped, and a gate that judged zero cases, leave the same record as one that ran. horde
has at least six gates that can skip with exit 0 by design: a missing compiler, a submodule not
checked out, an unkeyed platform, a sibling repo absent.

**The proposal.**
- **A kit helper,** for example `gate <name> <command…>`. A project's `verify` calls it for each
  gate, and it appends one line per gate to the record: `ran`, `skipped: <reason>` or `failed`,
  plus an optional case count the gate prints in an agreed form.
- **A fleet reader,** beside `red_records.py`: repos whose latest green record skipped gates, or
  judged fewer cases than last time.
- **A floor rule** as kit doctrine: a gate that loops over a corpus pins the count it must reach.
  horde is adding these now (its B455 H1).

**What it would have caught.** The empty parity corpus, the half-judged sanitize job, and every
"green" that was really "did not run".

**Cost.** It is a change to a kit-owned file, plus an adoption step in each repo's `verify`. It can
start in observe mode like your other gates (Decision 84).

### P2. A run ledger: what each dispatch did, written by hooks and not by the agent

**The gap.** A lead learns what a sub-agent did from the sub-agent's own report. The mechanical
facts are all knowable without trusting prose: which files it touched, whether they were in the
scope it was given, what its verify record said, which PR it opened, and whether that PR's commits
are on the default branch.

**The proposal.**
- **Two event kinds in `fleet_events`,** following its own content rule (positions and verdicts,
  never text):
  - *dispatch*: agent type, pinned model, worktree branch and base commit, a hash of the brief,
    declared scope globs;
  - *subagent stop*: files changed (count, and count outside the declared scope), commits made, the
    verify record's target and exit, PR number if any, duration, and token totals if the hook
    payload carries them.
- **A landing check,** deterministic and remote-visible: for every PR merged in the last N days, is
  its head an ancestor of the default branch? A merged PR that is not is the stacked-PR race. It
  fits `algedonic.py`'s scope, since it is pain only the remote can show and it goes unnoticed the
  moment nobody is looking.
- **A view** on the session board: one line per dispatch.

**What it would have caught.** The wrong-base merge, both lost records commits, the lead's red
push, and scope drift. It also answers "what ran overnight" without reading any agent's narration.

**Questions inside it.**
- Does the SubagentStop payload carry enough to compute these?
- Does a per-dispatch event belong in the central log or in the session's own record?

### P3. A decision queue: the third board

**The gap.** Your boards show sessions and threads. Nothing shows the human what is waiting on
THEM. In horde the lead restated the open decisions at the end of most messages, and the human
ruled by replying "go with your recommendations" to a list they had to scroll for.

**The proposal.**
- **A convention** for marking a decision as waiting on the human, with a recommendation, the date
  it was raised and what it blocks. `kit/contracts/status.md` already owns terminal status
  spellings; this would be one more status with two fields. The alternative is one small file per
  repo.
- **A third board** in `boards.py`: every waiting decision across the roster, oldest first, each
  with the lead's recommendation, so the human rules from one page.
- **Later, perhaps:** rulings recorded from that page, so that a ratchet's `approved` field can
  cite something an agent could not have typed. That is the unauthenticated-approval gap from our
  report-008.

**What it would have caught.** Nothing broke for want of it. It is the one the human would use
daily, and it removes the lead's incentive to bundle unrelated decisions into one reply.

## 4. Smaller items, for your watchdog design and not for now

- **A stall signal.** Your watchdog lists "state-hash progress". The laptop-sleep stall is a second
  cause with the same symptom: nothing progresses, and nobody is told on wake.
- **Cost per queue item.** Your watchdog lists token-rate. horde's hardest item of the week took
  about 1.3 million sub-agent tokens across a harness builder, an implementer and three critic
  passes. That figure only
  exists because the lead added up task notifications by hand.
- **Worktree and disk state** in `session-close.py`'s facts: how many worktrees a repo carries, and
  how many are finished.

## 5. What we looked at and are not asking for

- **Claude Code's own OpenTelemetry export.** It gives tool calls, tokens and cost per session to
  any collector. It answers "what did it cost and what was it doing", and not "was the claim true".
  Worth a look for your token-rate metric. We have not configured it, and we make no claim about
  what its payloads contain.
- **Hosted LLM-observability platforms.** They are built for applications that call a model API,
  and they fit this workflow poorly.
- **The session transcripts already on disk.** They are the complete trace of every tool call. A
  reader over them could back-fill P2 without any new hook. But they contain content, so they sit
  on the other side of your "never content" rule.

## 6. Questions

1. What of the above already exists and we missed?
2. For P1, is a helper in `kit-gates.sh` the right place, or should the receipt be a separate
   kit-owned file that `record()` finalises?
3. For P2, does a per-dispatch event respect Decision 77's content rule as you intend it? A brief's
   hash and scope globs are positions; are they acceptable?
4. For P3, a status spelling or a file per repo?
5. Order: we would take P1 first (the cheapest, and it stops the most dangerous failure), then P2,
   then P3. Do you agree?

## 7. What horde offers

- To pilot each one, as with the security method: run your gate or hook in horde's `./verify` as
  soon as it exists, and report what it got wrong.
- The evidence behind every row of §1, on request, from horde's ROADMAP rows B448 and B455.

**Ball: autonomous.** Nothing in horde waits on this.
