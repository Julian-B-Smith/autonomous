"""batch — one worktree and one PR per roster repo, from a plan, through the
same contracts as `act push` / `act pr-open` / `act pr-close`.

The 2026-10-12 fleet batch (Decision 95) ran from a script written in a
scratch folder an hour before it opened 49 PRs and closed 37. This is that
script made permanent (Phase A0, Decision 96): a declarative plan in
`kit/act/plans/`, the steps in `steps.py`, dry by default, and every push, PR
and close decided by `checks.py`.

Per repo with a remote:
  1. a worktree off origin/<default> on the plan's branch;
  2. the plan's steps, each anchored (`steps.py`);
  3. proof: the kit gates sourced directly, the closing-gate shim executed and
     its wiring checked, and the repo's own `./verify fast`, compared with the
     same command on an untouched worktree if it is red;
  4. with --open: commit, `do_push`, `do_pr_open`, then close the repo's open
     PRs from the plan's `supersedes` branches with `do_pr_close`.

Run state (results, PR bodies, worktrees) is machine-local, under
`~/.claude/fleet/act/<plan id>/`, never in this public repo: it names private
repositories.
"""
import concurrent.futures as cf, json, os, shutil, subprocess, sys, tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, ".."))
sys.path.insert(0, os.path.join(_HERE, "..", "sweep"))
import act, steps  # noqa: E402
import currency  # noqa: E402

_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
REQUIRED = ("id", "branch", "steps", "title", "commit_message", "origin")


def load_plan(path):
    with open(path, encoding="utf-8") as fh:
        plan = json.load(fh)
    missing = [k for k in REQUIRED if not plan.get(k)]
    unknown = [s for s in plan.get("steps", []) if s not in steps.STEPS]
    if missing or unknown:
        raise ValueError(f"plan {path}: missing {missing}, unknown steps {unknown}")
    if "origin" not in plan["origin"].lower():
        raise ValueError("plan origin must open with an origin line (the PR contract requires it)")
    plan.setdefault("supersedes", [])
    return plan


def run_dir(plan):
    d = os.path.expanduser(os.environ.get("KIT_ACT_DIR", "~/.claude/fleet/act"))
    return os.path.join(d, plan["id"])


def git_env(rd):
    """An exclude file for this run only. The batch symlinks a repo's resident
    `node_modules`/`.venv` into the worktree so its verify can run, and git's
    `node_modules/` pattern does not match a SYMLINK, so every JS repo would
    read dirty and `checks.verified` would refuse the push. The user's own
    global excludes are kept: git reads one excludes file, and this one starts
    as a copy of theirs."""
    ex = os.path.join(rd, "excludes")
    base = ""
    for cand in (subprocess.run(["git", "config", "--global", "--get", "core.excludesFile"],
                                capture_output=True, text=True).stdout.strip(),
                 os.path.expanduser("~/.config/git/ignore")):
        if cand and os.path.isfile(os.path.expanduser(cand)):
            base = open(os.path.expanduser(cand), encoding="utf-8", errors="ignore").read()
            break
    with open(ex, "w", encoding="utf-8") as fh:
        fh.write(base.rstrip("\n") + "\n/node_modules\n/.venv\n/venv\n/.harness/\n")
    e = dict(os.environ)
    n = int(e.get("GIT_CONFIG_COUNT", "0") or 0)
    e.update({"GIT_CONFIG_COUNT": str(n + 1), f"GIT_CONFIG_KEY_{n}": "core.excludesFile",
              f"GIT_CONFIG_VALUE_{n}": ex})
    return e


def sh(cmd, cwd, env, timeout=900, inp=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           env=env, input=inp)
        return p.returncode, (p.stdout + p.stderr)[-1500:]
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def _link_deps(src, dst):
    for d in ("node_modules", ".venv", "venv"):
        s = os.path.join(src, d)
        if os.path.isdir(s) and not os.path.exists(os.path.join(dst, d)):
            os.symlink(s, os.path.join(dst, d))


def _verify(path, resident, env):
    if not os.access(os.path.join(path, "verify"), os.X_OK):
        return None, "no ./verify"
    _link_deps(resident, path)
    return sh(["./verify", "fast"], path, env)


def body_for(plan, r):
    v = {"green": "passed", "n/a": "does not exist here",
         "red before and after": "was **already red on the default branch**, and is red by "
                                 "the same amount on this branch"}[r["verify"]]
    lines = "\n".join(f"- {l}" for l in r["lines"] if l)
    extra = ("\n\n" + plan["about"].strip()) if plan.get("about") else ""
    return f"""{plan['origin'].strip()}

## What changed

{lines}{extra}

## Evidence

- On this branch, `kit_integrity` and `leak_gate` pass.
- Where this repo has a closing gate, the shim runs and exits 0, and it is wired to the Stop hook.
- This repo's own `./verify fast` {v}.
- Pushed and opened through `act` (autonomous Decision 96): the branch's tree is the one the green verify recorded.

## Action

{plan.get('action', 'Merge.').strip()}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
"""


def one(plan, name, path, rd, env, do_open, classify_only):
    r = {"name": name}
    rc, out = sh(["git", "remote"], path, env)
    if rc or not out.strip():
        return {**r, "result": "skip: no remote"}
    sh(["git", "fetch", "-q", "--prune", "origin"], path, env, timeout=180)
    base = act.default_branch(path)
    if not base:
        return {**r, "result": "fail: default branch unreadable"}
    if sh(["git", "rev-parse", "-q", "--verify", f"origin/{base}"], path, env)[0]:
        return {**r, "result": f"fail: no origin/{base}"}
    br = plan["branch"]
    if not classify_only and sh(["git", "ls-remote", "--exit-code", "--heads", "origin", br],
                                path, env, timeout=60)[0] == 0:
        return {**r, "result": "skip: branch already on remote"}
    wt = os.path.join(rd, "wt", name)
    bwt = wt + "__base"
    for w in (wt, bwt):
        sh(["git", "worktree", "remove", "--force", w], path, env); shutil.rmtree(w, ignore_errors=True)
    sh(["git", "worktree", "prune"], path, env)
    if not classify_only:
        sh(["git", "branch", "-D", br], path, env)
    add = ["git", "worktree", "add", "-q"] + (["--detach", wt] if classify_only else ["-b", br, wt])
    rc, out = sh(add + [f"origin/{base}"], path, env)
    if rc:
        return {**r, "result": "fail: worktree", "detail": out}
    try:
        return _in_worktree(plan, r, path, wt, bwt, base, env, rd, do_open, classify_only)
    finally:
        # The branch stays in the resident's repo (a refused push can be
        # retried from it); only the worktree goes.
        sh(["git", "worktree", "remove", "--force", wt], path, env)


def _in_worktree(plan, r, path, wt, bwt, base, env, rd, do_open, classify_only):
    r["kinds"], r["lines"], paths = {}, [], []
    for name in plan["steps"]:
        s = steps.STEPS[name](wt)
        r["kinds"][name] = s.kind
        if s.hold:
            return {**r, "result": f"skip: {s.hold}"}
        r["lines"].append(s.line)
        paths += s.paths
    if classify_only:
        return {**r, "result": "classified"}
    if not sh(["git", "status", "--porcelain"], wt, env)[1].strip():
        return {**r, "result": f"skip: already current on origin/{base}"}
    if os.path.isfile(os.path.join(wt, ".kit", "kit-gates.sh")):
        rc, out = sh(["bash", "-c", ". .kit/kit-gates.sh && kit_integrity && leak_gate"], wt, env)
        if rc:
            return {**r, "result": "HOLD: kit gates red after the change", "detail": out}
    if r["kinds"].get("closing_gate") in ("swapped", "added", "already-shim"):
        e = dict(env, CLAUDE_PROJECT_DIR=wt, KIT_FLEET_DIR=os.path.join(rd, "nofleet"))
        rc, out = sh(["bash", steps.GATE_REL], wt, e, inp="{}")
        if rc:
            return {**r, "result": "HOLD: shim did not exit 0 on a fresh tree", "detail": out}
        if currency._closing_gate(wt) is not True:
            return {**r, "result": "HOLD: closing gate not wired after the change"}
    vrc, vout = _verify(wt, path, env)
    if vrc not in (None, 0):
        sh(["git", "worktree", "add", "-q", "--detach", bwt, f"origin/{base}"], path, env)
        brc, _ = _verify(bwt, path, env)
        sh(["git", "worktree", "remove", "--force", bwt], path, env)
        if brc == 0:
            return {**r, "result": "HOLD: verify red only after the change", "detail": vout}
    r["verify"] = "n/a" if vrc is None else ("green" if vrc == 0 else "red before and after")
    sh(["git", "add", "--"] + sorted(set(paths)), wt, env)
    if not do_open:
        return {**r, "result": "ready (dry)"}
    msg = os.path.join(rd, "commit-message.txt")
    with open(msg, "w", encoding="utf-8") as fh:
        fh.write(plan["commit_message"].rstrip("\n") + "\n")
    rc, out = sh(["git", "commit", "-q", "-F", msg], wt, env)
    if rc:
        return {**r, "result": "fail: commit", "detail": out}
    stray = sh(["git", "status", "--porcelain"], wt, env)[1].strip()
    if stray:
        # verify left files the repo does not ignore; the push contract would
        # refuse, and committing them would be a guess.
        return {**r, "result": "HOLD: verify left untracked files", "detail": stray[:400]}
    old = os.environ.copy()
    os.environ.update({k: v for k, v in env.items() if k.startswith("GIT_CONFIG")})
    try:
        if act.do_push(wt):
            return {**r, "result": "fail: push (refused by contract or by the repo's pre-push hook)"}
        bodyf = os.path.join(rd, r["name"].replace("/", "__") + ".pr.md")
        with open(bodyf, "w", encoding="utf-8") as fh:
            fh.write(body_for(plan, r))
        code, url = act.do_pr_open(wt, plan["title"], bodyf)
        if code:
            return {**r, "result": "fail: pr refused or failed"}
        r["pr"], r["closed"] = url, []
        for head in plan["supersedes"]:
            rc, nums = sh(["gh", "pr", "list", "--head", head, "--state", "open", "--json", "number",
                           "--jq", ".[].number"], wt, env, timeout=60)
            for n in nums.split():
                if n.isdigit():
                    r["closed"].append(n if act.do_pr_close(wt, n, url, delete_branch=True) == 0
                                       else f"{n} (close refused or failed)")
    finally:
        os.environ.clear(); os.environ.update(old)
    return {**r, "result": "PR"}


def main(a):
    plan = load_plan(a.plan)
    sys.path.insert(0, os.path.join(_ROOT, "kit", "sweep"))
    import sweep
    rd = run_dir(plan)
    os.makedirs(os.path.join(rd, "wt"), exist_ok=True)
    env = git_env(rd)
    reg = json.load(open(os.environ.get("KIT_ACT_REGISTRY", os.path.join(_ROOT, "registry.json"))))
    skip = set(a.skip.split(",")) - {""}
    todo = [(p["name"], p["path"]) for p in sweep.resolve(reg)
            if os.path.realpath(p["path"]) != os.path.realpath(_ROOT) and p["name"] not in skip
            and (not a.only or p["name"] in a.only.split(","))]
    res = []
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(one, plan, n, p, rd, env, a.open, a.classify_only) for n, p in todo]
        for f in cf.as_completed(futs):
            x = f.result(); res.append(x)
            print(json.dumps({k: v for k, v in x.items() if k != "lines"})[:400], flush=True)
    mode = "classify" if a.classify_only else ("open" if a.open else "dry")
    with open(os.path.join(rd, f"results-{mode}.json"), "w", encoding="utf-8") as fh:
        json.dump(sorted(res, key=lambda x: x["name"]), fh, indent=1)
    counts = {}
    for x in res:
        counts[x["result"].split(":")[0]] = counts.get(x["result"].split(":")[0], 0) + 1
    print(f"act batch {plan['id']} [{mode}]: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
          + f"  (results: {os.path.join(rd, f'results-{mode}.json')})")
    held = [x for x in res if x["result"].startswith(("HOLD", "fail"))]
    return 2 if held else 0
