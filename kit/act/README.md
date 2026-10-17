# kit/act/ — harness-owned outward actions

Phase A0 of Decision 96 (`briefs/2026-10-16-harness-owned-actions.proposal.md`).
The few actions that leave the working tree go through these commands, which
check what those actions keep needing and refuse with a reason. Reads,
builds, tests and local edits are not wrapped: that would be friction with no
safety in return.

    act push                                   push the current branch
    act pr-open --title T --body-file F [--base B --stack]
    act pr-close <number> --superseded-by URL [--delete-branch]
    act batch <plan.json> [--open] [--only a,b] [--classify-only]

Run as `python3 ~/Documents/Claude/autonomous/kit/act/act.py <verb> …` from
inside the repo the action is for. Exit 0 = done, 3 = refused (with the
reason), 1 = something broke. Every call is one line in the fleet event log.

| Command | Refuses | Earned by |
|---|---|---|
| `push` | the default branch; a branch whose PR is merged or closed; a red or missing verify record; a tree that is not the one verify recorded; uncommitted changes; force | a push to a merged PR's branch (#47); horde's push of a red commit |
| `pr-open` | a second PR for the branch; a non-default base without `--stack`; `--stack` onto a base with no open PR; an unpushed branch; a body without an origin line; an unverified tree | horde's stacked PR that merged into a dead branch |
| `pr-close` | a PR not opened by this account; a branch this kit's batches did not create; no link to the replacement | the 37 superseded PRs closed on 2026-10-12 |
| `batch` | per repo, anything a step does not recognise (it is named in the PR and left alone); a repo whose verify goes red only after the change | 49 PRs opened from a scratch-folder script |

**Layout.** `checks.py` holds the contracts as pure functions (facts in,
verdict out, no I/O, no model). `act.py` gathers the facts from git and
GitHub and acts only on `ok`. `steps.py` holds the changes a batch plan may
name. `batch.py` is the engine. `plans/` holds one JSON plan per batch, and is
the record of what each batch was. Run state (results, PR bodies, worktrees)
is machine-local under `~/.claude/fleet/act/<plan id>/`: it names private
repositories, and this repository is public.

**Not yet enforced.** Until Phase A2 the raw `git push` / `gh pr …` path still
works. A1 logs it; A2 denies it per command. Merges and repository settings
are already denied by rule in the harness template (2.10.0).

**Tests.** `test_act.py`: every refusal as a planted case; the commands end to
end against a local bare remote and a fake `gh`; one batch from plan to PR.
