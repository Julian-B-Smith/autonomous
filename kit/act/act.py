#!/usr/bin/env python3
"""act — harness-owned outward actions (Phase A0, Decision 96).

    act push                                   push the current branch
    act pr-open --title T --body-file F [--base B --stack]
    act pr-close <number> --superseded-by URL [--delete-branch]
    act batch <plan.json> [--open] [--only a,b] [--classify-only]

Run from inside the repo the action is for. Each command gathers FACTS from
git and GitHub, asks the pure contract in `checks.py`, and acts only on
`ok`. A refusal prints its reason and exits 3, so a caller can tell "refused"
from "broke" (exit 1). Every call, refused or not, is one line in the fleet
event log (`kit/hooks/fleet_events.py`): verb, verdict, repo; never content.

Why these exist: the raw `git push` / `gh pr …` path carried six incidents in
one week (the proposal's table), each a check that lived in nobody's code.
Until A2 the raw path is still open; these are the path that cannot skip a
check, not yet the only path.
"""
import argparse, json, os, subprocess, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "..", "hooks"))
import checks  # noqa: E402

REFUSED, BROKE = 3, 1
# Branch prefixes `act batch` creates. `act pr-close` closes only these.
BATCH_PREFIXES = ("kit-",)


def run(args, cwd=None, timeout=120, inp=None):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, input=inp)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 124, "", str(exc)


def log(verb, ok, repo, **extra):
    try:
        import fleet_events as fe
        fe.log("act", verb=verb, verdict="ok" if ok else "refused", repo=repo, **extra)
    except Exception:
        pass                      # the log must never break the action


def top(cwd="."):
    rc, out, _ = run(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
    if rc:
        sys.exit(_die("not inside a git repository"))
    return out


def repo_name(t):
    try:
        import fleet_events as fe
        return fe.repo_name(t)
    except Exception:
        return os.path.basename(t)


def _die(msg, code=BROKE):
    print(f"act: {msg}", file=sys.stderr)
    return code


def default_branch(t):
    """origin/HEAD first (no network), then GitHub, then main/master. A wrong
    answer here would let a push to the default branch through, so a repo whose
    default cannot be read is refused rather than guessed."""
    rc, out, _ = run(["git", "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD"], cwd=t)
    if rc == 0 and out.startswith("origin/"):
        return out.split("/", 1)[1]
    rc, out, _ = run(["gh", "repo", "view", "--json", "defaultBranchRef",
                      "--jq", ".defaultBranchRef.name"], cwd=t, timeout=60)
    if rc == 0 and out:
        return out
    return None


def current_branch(t):
    rc, out, _ = run(["git", "symbolic-ref", "-q", "--short", "HEAD"], cwd=t)
    return out if rc == 0 else None


def verify_facts(t):
    """record, tree_now, clean — what `checks.verified` needs."""
    rec = None
    try:
        with open(os.path.join(t, ".harness", "last-verify.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
    except (OSError, ValueError):
        rec = None
    if isinstance(rec, dict):
        _, head, _ = run(["git", "rev-parse", "HEAD"], cwd=t)
        g = str(rec.get("git") or "")
        rec["head_matches"] = bool(g) and head.startswith(g)
    else:
        rec = None
    tree = ""
    if os.path.isfile(os.path.join(t, ".kit", "kit-gates.sh")):
        rc, out, _ = run(["bash", "-c", ". .kit/kit-gates.sh >/dev/null 2>&1; "
                          "type kit_tree_hash >/dev/null 2>&1 && kit_tree_hash"], cwd=t)
        tree = out if rc == 0 else ""
    _, st, _ = run(["git", "status", "--porcelain"], cwd=t)
    return {"record": rec, "tree_now": tree, "clean": st == "",
            "has_verify": os.access(os.path.join(t, "verify"), os.X_OK)}


def pr_states(t, head):
    rc, out, _ = run(["gh", "pr", "list", "--head", head, "--state", "all",
                      "--json", "state", "--jq", ".[].state"], cwd=t, timeout=60)
    if rc:
        return None
    return out.split()


def do_push(t):
    """Push `t`'s current branch if the contract allows. Returns an exit code."""
    br, default = current_branch(t), default_branch(t)
    if not br:
        return _die("HEAD is detached; check out a branch")
    if not default:
        return _die("cannot read this repo's default branch; refusing rather than guessing")
    states = pr_states(t, br)
    if states is None:
        return _die("could not ask GitHub for this branch's PRs; refusing rather than guessing")
    ok, why = checks.push({"branch": br, "default": default, "force": False, "deletes": False,
                           "pr_states": states, **verify_facts(t)})
    log("push", ok, repo_name(t))
    if not ok:
        return _die(f"push refused: {why}", REFUSED)
    rc, out, err = run(["git", "push", "-u", "origin", br], cwd=t, timeout=1800)
    if rc:
        return _die(f"git push failed (the repo's own pre-push hook may have refused):\n{err[-1500:]}")
    print(f"act: pushed {br} ({why})")
    return 0


def do_pr_open(t, title, body_file, base=None, stack=False):
    """Open a PR from `t`'s current branch if the contract allows. Prints the
    URL on success and returns (exit code, url)."""
    br, default = current_branch(t), default_branch(t)
    if not br or not default:
        return _die("need a checked-out branch and a readable default branch"), None
    base = base or default
    try:
        body = open(body_file, encoding="utf-8").read()
    except OSError as exc:
        return _die(f"cannot read --body-file: {exc}"), None
    rc, remote, _ = run(["git", "ls-remote", "origin", f"refs/heads/{br}"], cwd=t, timeout=60)
    _, head, _ = run(["git", "rev-parse", "HEAD"], cwd=t)
    rc2, existing, _ = run(["gh", "pr", "list", "--head", br, "--state", "open",
                            "--json", "url", "--jq", ".[0].url"], cwd=t, timeout=60)
    stack_state = None
    if base != default:
        _, s, _ = run(["gh", "pr", "list", "--head", base, "--state", "open",
                       "--json", "state", "--jq", ".[0].state"], cwd=t, timeout=60)
        stack_state = s or None
    ok, why = checks.pr_open({"base": base, "default": default, "stack": stack,
                              "stack_base_state": stack_state,
                              "head_pushed": rc == 0 and remote.split()[:1] == [head],
                              "existing_open": existing or None, "body": body,
                              **verify_facts(t)})
    log("pr-open", ok, repo_name(t), stacked=base != default)
    if not ok:
        return _die(f"PR refused: {why}", REFUSED), None
    rc, out, err = run(["gh", "pr", "create", "--base", base, "--head", br, "--title", title,
                        "--body-file", body_file], cwd=t, timeout=120)
    if rc:
        return _die(f"gh pr create failed:\n{err[-800:]}"), None
    url = out.splitlines()[-1] if out else ""
    print(url)
    return 0, url


def do_pr_close(t, number, superseded_by, delete_branch=False):
    rc, out, err = run(["gh", "pr", "view", str(number), "--json", "author,headRefName,state"],
                       cwd=t, timeout=60)
    if rc:
        return _die(f"cannot read PR {number}: {err[-300:]}")
    pr = json.loads(out)
    _, me, _ = run(["gh", "api", "user", "--jq", ".login"], cwd=t, timeout=60)
    ok, why = checks.pr_close({"author": (pr.get("author") or {}).get("login"), "me": me,
                               "head": pr.get("headRefName") or "", "prefixes": BATCH_PREFIXES,
                               "superseded_by": superseded_by, "state": pr.get("state")})
    log("pr-close", ok, repo_name(t))
    if not ok:
        return _die(f"close refused: {why}", REFUSED)
    cmd = ["gh", "pr", "close", str(number), "--comment",
           f"Superseded by {superseded_by}. Closed through `act pr-close` (autonomous Decision 96)."]
    if delete_branch:
        cmd.append("--delete-branch")
    rc, out, err = run(cmd, cwd=t, timeout=60)
    if rc:
        return _die(f"gh pr close failed:\n{err[-500:]}")
    print(f"act: closed #{number} as superseded by {superseded_by}")
    return 0


def cmd_push(a):
    return do_push(top())


def cmd_pr_open(a):
    return do_pr_open(top(), a.title, a.body_file, a.base, a.stack)[0]


def cmd_pr_close(a):
    return do_pr_close(top(), a.number, a.superseded_by, a.delete_branch)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="act")
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("push")
    p = sub.add_parser("pr-open")
    p.add_argument("--title", required=True)
    p.add_argument("--body-file", required=True)
    p.add_argument("--base")
    p.add_argument("--stack", action="store_true")
    p = sub.add_parser("pr-close")
    p.add_argument("number")
    p.add_argument("--superseded-by", required=True)
    p.add_argument("--delete-branch", action="store_true")
    p = sub.add_parser("batch")
    p.add_argument("plan")
    p.add_argument("--open", action="store_true")
    p.add_argument("--only")
    p.add_argument("--skip", default="")
    p.add_argument("--classify-only", action="store_true")
    p.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    if a.verb == "batch":
        import batch
        return batch.main(a)
    return {"push": cmd_push, "pr-open": cmd_pr_open, "pr-close": cmd_pr_close}[a.verb](a)


if __name__ == "__main__":
    sys.exit(main())
