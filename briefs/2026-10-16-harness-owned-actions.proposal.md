---
proposal: harness-owned-actions
from: autonomous (resident integrator)
to: julian
ball: julian
date: 2026-10-16
status: proposed — awaiting ratification by poll
answers: the human's question of 2026-10-16, from reading on harness design —
  "agents aren't allowed to call tools themselves; build the tool call contract
  into the harness and make the calls through it." Is that something we should
  implement?
---

> **Origin.** autonomous standing integrator, 2026-10-16, at the human's
> request ("Write the proposal first", by poll). Grounded in: Decisions 66
> (agents push branches and open PRs; merges are the human's), 84 (gates earn
> blocking one by one), 89–95 (the closing gate, the receipt, the 2.9.1 batch),
> horde briefs hypersaw-009 and -010, and this fortnight's incident record.

# Harness-owned actions: outward calls go through tested commands

## The one-paragraph version

Taken literally, Claude Code already works this way: the model never runs
anything itself; it asks, and the harness executes, with permission rules and
hooks in between. What the principle is really about is **ambient
authority**. Any session here can run `git push`, `gh pr create`,
`gh pr close`, `gh pr merge` or a script it wrote a minute ago, and nothing
owned by the harness says what must be true before it does. This proposal
gives the handful of actions that change things OUTSIDE the agent's working
tree a kit-owned, tested command each, with the checks those actions keep
needing, logs every raw use for a week, and then lets each command earn the
right to be the only way, one at a time. Reads, builds, tests and local edits
stay free.

## Why: the record

Every row is from 2026-10-05 to 2026-10-12. None needed a smarter model. Each
needed a check that lived in nobody's code.

| What happened | The check a command would have made |
|---|---|
| The integrator pushed a commit to #47's branch 12 minutes after #47 merged; it never reached `main` (moved by hand to #48) | the head branch's PR is still open |
| horde's lead pushed a red commit: a command printed the verify result and nothing tested it | the verify record is green AND its tree fingerprint matches the tree being pushed |
| A stacked PR merged into its dead base branch eight seconds after the base merged (horde) | a PR's base is the default branch unless the call says `--stack`, and a stack is recorded for the landing check |
| Two `gh pr comment` loops posted nothing (zsh does not split words) and looked successful | one tested implementation instead of a shell loop written fresh each time |
| A brief reused a closed thread's id (hypersaw-003) | the id is unique across that sender's threads |
| **49 PRs opened and 37 closed by a script written in a scratch folder an hour earlier**, reviewed by no one | the batch is versioned code with tests, and a dry run whose output is the plan |
| "Merges are the human's" is prose. The harness template's 11 deny rules do not include `gh pr merge`, and no hook checks it | a deny rule. The cheapest row in this table |

## Scope: which actions, and which not

**In scope:** actions whose effect leaves the working tree and is
seen by others or is hard to undo.

| Action | Today | Proposed command |
|---|---|---|
| Push a branch | raw `git push` | `act push` |
| Open a PR | raw `gh pr create` | `act pr-open` |
| Close a PR as superseded | raw `gh pr close` | `act pr-close --superseded-by <url>` |
| Fleet batch (sync, retrofit steps, PR per repo) | `sync270.py`, `sync291.py` in a scratch folder | `act batch <plan>` |
| File a brief, notice or response in another repo's mailbox | hand-written Markdown | `act file` |
| Merge a PR | raw `gh pr merge` (not denied) | **no command: denied outright.** It is the human's |
| Visibility, repo settings, deletion | raw `gh repo edit/delete` | **no command: denied outright** |

**Out of scope, deliberately:** reads, searches, builds, tests, edits inside
the repo, and Claude Code's own tools (Artifact, MCP servers), which already
pass through its permission prompts. Wrapping these adds friction and no
safety, and the doctrine says to delete constraints that do not earn their
place. No model sits in any command's path: each check is deterministic code
(AI/deterministic boundary).

## The contracts

Each command refuses with a reason, and logs the call to the fleet event log
(positions and verdicts, never content), so the log shows every outward
action in one place.

- **`act push`.** Refuses:
  - a branch whose PR is merged or closed;
  - a force push;
  - the default branch, unless the repo's manifest allows direct pushes there
    (autonomous does today; see question 2);
  - a tree that is not the one a green verify recorded (`kit_tree_hash`
    against the record, which 2.9 already writes).
- **`act pr-open`.** Requires:
  - a base that is the default branch, or `--stack <base>`, which is recorded
    so the landing check knows to expect it;
  - the head pushed and matching the verified tree;
  - a body whose first line is an origin line, as the provenance tenet
    requires.
- **`act pr-close --superseded-by`.** Only:
  - PRs this account opened;
  - from branch names this kit uses;
  - with the link in the closing comment.
- **`act batch <plan>`.** The 2026-10-12 script made permanent:
  - a declarative plan naming the change steps;
  - dry by default, and the dry run's output is the plan the human approves;
  - one worktree per repo;
  - the kit gates and the repo's own verify, before and after the change;
  - `act pr-open` for each PR, and supersede the repo's earlier batch PR;
  - resumable after a failure, with a run record kept.
- **`act file`.** Checks:
  - the frontmatter against `kit/contracts/status.md`;
  - id uniqueness;
  - an origin line.

  It writes the file uncommitted into the provider's
  `integrations/<sender>/`, which is the one sanctioned write outside home.

The commands live in `kit/act/` and run from the standards repo's checkout,
like `kit_sync.py`. They are not vendored: CI never pushes or opens PRs, so
nothing in CI needs them.

## Enforcement ladder

1. **A0 — the commands exist and are used by choice.** The batch command
   first, because it carried the largest single risk. Merge and settings
   become deny rules in the harness template at the same time.
2. **A1 — observe.** A PreToolUse hook on Bash logs `would-deny` for every
   raw `git push`, `gh pr create|close|merge|edit`, `gh repo edit|delete` and
   `gh api` write that did not come through `act`. The log is per verb.
   Mode is read from `kit/hooks/gate_modes.json` (Decision 84).
3. **A2 — deny, per command.** After a clean week, each command's raw route
   is denied by its own signed GATE-CHANGE, the way the closing gate earns
   blocking.
4. **A3 — credential isolation, only if the log shows it is needed.**

**A limit at A2, stated so the rule does not oversell itself.** A hook
matching command text is best effort: `bash -c "gh pr create"` or a script
slips past it. A2 raises the floor; it is not a wall. The wall is A3: the
agent's shell holds no GitHub credential, and only the `act` process does. On
one Mac with one user account that means a second OS user or a small local
service holding the token. That is real cost, and it is deferred until the A1
log shows raw outward calls still happening.

## Phases and gates

| Phase | Builds | Gate |
|---|---|---|
| **A0** | `act batch` (a port of `sync291.py` with tests); `act push`, `act pr-open`, `act pr-close`; deny rules for merge and repo settings in the template | each refusal fires on a planted case; a dry run of `act batch` over the fleet classifies every unchanged repo the same as the 2026-10-12 run did |
| **A1** | the observe hook; `act file` | a week of `would-deny` events, read per verb |
| **A2** | per-verb deny flips | each by a signed GATE-CHANGE after its clean week |
| **A3** | credential isolation | only if A1 shows raw outward calls continuing, and only by the human's call |

Order: after the decision queue, as the human said, unless reordered at
ratification.

## Questions for the human (to be asked as a poll at ratification)

1. **Where the observe hook installs.** Globally, so every session on this Mac
   is covered (a settings change only you can approve), or per repo through
   the next kit batch.
2. **autonomous's own direct pushes to `main`.** The charter allows them. Keep
   that as a manifest-declared exception, or route this repo through PRs like
   every other.
3. **Merge as a hard deny now.** It is the cheapest row and could ship ahead
   of everything else, in the next kit batch.
4. **Order.** After the decision queue as planned, or A0 first. The batch
   command would then exist before the next fleet batch.
