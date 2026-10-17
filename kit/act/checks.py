"""checks — the contracts of the harness-owned actions, as pure functions.

Phase A0 (Decision 96; `briefs/2026-10-16-harness-owned-actions.proposal.md`).
Every outward action an agent takes (push, open a PR, close a superseded PR)
asks one of these functions first. Each takes FACTS, which the adapter in
`act.py` gathers from git and GitHub, and returns `(ok, reason)`. Nothing here
runs a command, reads a clock or calls a model, so every refusal is a
deterministic, testable verdict (the AI/deterministic boundary).

Each refusal names the incident that earned it. A check with no incident
behind it does not belong here: wrapping actions for their own sake is the
ceremony the doctrine says to delete.
"""


def verified(record, tree_now, clean, has_verify=True):
    """Is the tree about to leave this machine the one a GREEN verify judged?

    `record` is `.harness/last-verify.json` (or None), `tree_now` is
    `kit_tree_hash` of the working tree, `clean` is "git status is empty", so
    the working tree equals the commit being pushed. horde's lead pushed a red
    commit because a command PRINTED the verify result and nothing tested it
    (brief hypersaw-010). A record written before kit 2.9 has no fingerprint;
    it then has to name the commit itself.

    A repo with no `./verify` has no oracle to consult. That passes, with the
    reason saying so, because refusing would only push the agent back to raw
    `git push`; writing a record for a verify that never ran would bless bytes
    nothing judged, which is what the receipt exists to prevent."""
    if not has_verify:
        if not clean:
            return False, "the working tree has uncommitted changes, so it is not the commit being pushed"
        return True, "no ./verify in this repo (nothing to verify against)"
    if not record:
        return False, "no verify record here: run ./verify fast first"
    if record.get("exit") != 0:
        return False, "the last ./verify was RED"
    if not clean:
        return False, ("the working tree has changes that are not committed, so it is not "
                       "the commit being pushed. Commit or stash, then ./verify")
    want = record.get("tree") or ""
    if want:
        if want != tree_now:
            return False, "the tree changed after the last ./verify: run it again"
        return True, "verified tree"
    # Pre-2.9 record: no fingerprint, so the record must name this commit.
    if record.get("head_matches"):
        return True, "verified commit (record without a fingerprint)"
    return False, ("the verify record has no tree fingerprint and names another commit: "
                   "sync the kit (2.9+) or run ./verify on this commit")


def push(f):
    """f: branch, default, force, deletes, pr_states (states of PRs whose head
    is this branch), record, tree_now, clean."""
    if f.get("force"):
        return False, "force push refused: it rewrites history others may have"
    if f.get("deletes"):
        return False, "deleting a remote branch is not a push; use `act pr-close --delete-branch`"
    if f["branch"] == f["default"]:
        # Decision 96: every repo is PRs only, this one included.
        return False, f"push to the default branch `{f['default']}` refused: open a PR"
    states = set(f.get("pr_states") or [])
    if states and "OPEN" not in states:
        # The #47 incident: a commit pushed 12 minutes after its PR merged
        # never reached main (moved by hand to #48).
        return False, (f"this branch's PR is already {'/'.join(sorted(states))}; a push here "
                       f"reaches no one. Branch from the default branch and open a new PR")
    return verified(f.get("record"), f.get("tree_now"), f.get("clean"), f.get("has_verify", True))


def pr_open(f):
    """f: base, default, stack_base_state (state of the open PR whose head is
    `base`, when stacking), head_pushed (remote head == local HEAD),
    existing_open (URL of an open PR for this head, or None), body, record,
    tree_now, clean, stack (bool)."""
    if f.get("existing_open"):
        return False, f"a PR for this branch is already open: {f['existing_open']}"
    if f["base"] != f["default"]:
        if not f.get("stack"):
            return False, (f"base `{f['base']}` is not the default branch `{f['default']}`. "
                           f"A stacked PR merges into its base's branch, not `{f['default']}`; "
                           f"pass --stack to mean it")
        if f.get("stack_base_state") != "OPEN":
            # horde: a PR merged into its base's dead branch eight seconds
            # after the base merged.
            return False, (f"--stack: the base branch `{f['base']}` has no OPEN PR, so this "
                           f"would merge into a branch that is not going anywhere")
    if not f.get("head_pushed"):
        return False, "the branch is not pushed, or the remote has a different commit: `act push` first"
    body = (f.get("body") or "").strip()
    first = next((l for l in body.splitlines() if l.strip()), "")
    if "origin" not in first.lower():
        # Provenance tenet: an agent-authored text opens with where it came
        # from, so "who wrote this?" is answered at a glance.
        return False, "the PR body's first line must state its origin (who, when, which decision)"
    return verified(f.get("record"), f.get("tree_now"), f.get("clean"), f.get("has_verify", True))


def pr_close(f):
    """f: author, me, head, prefixes (branch prefixes this kit's batches use),
    superseded_by, state."""
    if f.get("state") != "OPEN":
        return False, f"the PR is {f.get('state')}, not open"
    if f.get("author") != f.get("me"):
        return False, "only a PR this account opened can be closed as superseded"
    if not any(f["head"].startswith(p) for p in f.get("prefixes") or []):
        return False, (f"branch `{f['head']}` is not one this kit's batches create "
                       f"({', '.join(f.get('prefixes') or [])})")
    if not (f.get("superseded_by") or "").startswith("https://"):
        return False, "--superseded-by must be the URL of the replacing PR"
    return True, "superseded"
