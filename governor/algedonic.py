#!/usr/bin/env python3
"""algedonic — the pain channel. Remote-visible fleet pain only, no model calls.

VSM's algedonic signal is a threshold alarm that leaps the hierarchy: it does
not wait for a scheduled report, it does not pass through S3's judgement, it
goes straight to S5 (the human). Amendment D (Decision 47) earns this with one
incident: a machine-identity leak sat in a PUBLIC repo for 19 days, visible to
anyone with a browser, while every local sweep pointed one directory too high.
Remote-visible pain that only local tooling can notice is pain that goes
unnoticed the moment the human isn't at the keyboard.

SCOPE, stated so it is not over-trusted: this checks ONLY what GitHub can see.
  - default-branch CI RED on any roster repo with a workflow
  - machine-identity leak in the tracked tree of any PUBLIC roster repo
Local-only pain (an untracked leak, an unpushed regression, a dead local
monitor) is explicitly out of scope; that still waits for a session hook or
the FDA-cron trade the human declined. A check that claims fleet coverage it
does not have is worse than one that states its edge.

WHY NO MODEL: doctrine keeps AI out of the path of metrics and validation. A
pain signal that depends on a model's judgement can be talked out of firing,
or fire on a hallucination. This is `git grep` and `gh api`; it cannot be
argued with and it cannot invent.

WHY NOT DEPEND ON THE LOCAL REGISTRY'S PATHS: this runs on a GitHub runner
with no roster on disk. It derives the roster from the org's repo list and
clones public repos shallowly, so it sees exactly what a stranger sees — which
is the threat model.

Exit 0 = quiet. Exit 2 = pain (the workflow turns that into a notification).
Exit 1 = the check itself failed and MUST be treated as unknown, never quiet.
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ORG = os.environ.get("ALGEDONIC_ORG", "Julian-B-Smith")

# Kept byte-identical in spirit to the leak_gate / leak_scan patterns: POSIX
# ERE, both identity shapes, `\\+` for the escaped Windows form.
# Third alternative: the dash-encoded home path (kit 2.7.0, hypersaw-004).
_LEAK = r'/(Users|home)/[^/]+/|[A-Za-z]:\\+Users\\+[^\\]|(^|[/[:space:](=])-(Users|home)-[^-/[:space:]]+-'
_PLACEHOLDER = r'/(Users|home)/[<$@{%]|[A-Za-z]:\\+Users\\+[<$@{%]|-(Users|home)-[<$@{%]'


def _gh(*args):
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        # One slow call must not kill the run with a traceback: every PAIN line
        # already gathered (leaks included) would never be printed.
        raise RuntimeError(f"gh {' '.join(args[:3])}… timed out")
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}… failed: {r.stderr.strip()[:200]}")
    return r.stdout


def list_repos():
    """[(name, visibility, default_branch)] for every repo in the org."""
    out = _gh("repo", "list", ORG, "--limit", "200",
              "--json", "name,visibility,defaultBranchRef,isArchived,isEmpty")
    rows = []
    for r in json.loads(out):
        # Archived and EMPTY repos have nothing to be in pain about. Two empty
        # public repos (the-governor, grust) reported as "clone/scan failed" on
        # the first run — noise dressed as uncertainty, which is the exact thing
        # that gets a pain channel muted.
        if r.get("isArchived") or r.get("isEmpty"):
            continue
        rows.append((r["name"], r["visibility"].upper(),
                     (r.get("defaultBranchRef") or {}).get("name") or "main"))
    return rows


def default_branch_red(name, branch):
    """True if the latest completed run on the default branch concluded failure.
    'No runs' and 'in progress' are NOT red — only a concluded failure is pain."""
    try:
        out = _gh("run", "list", "-R", f"{ORG}/{name}", "--branch", branch,
                  "--limit", "1", "--json", "conclusion,status")
    except RuntimeError:
        return None
    runs = json.loads(out)
    if not runs:
        return False
    r = runs[0]
    return r.get("status") == "completed" and r.get("conclusion") == "failure"


def public_leak(name, branch):
    """Leak lines in a fresh shallow clone of a PUBLIC repo's default branch."""
    tmp = tempfile.mkdtemp(prefix="algedonic-")
    try:
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", branch,
                        f"https://github.com/{ORG}/{name}.git", tmp],
                       check=True, capture_output=True, timeout=120)
        excludes = [":(exclude)*leak_scan.py", ":(exclude).leakcheck-allow"]
        allow = os.path.join(tmp, ".leakcheck-allow")
        if os.path.isfile(allow):
            for line in open(allow, encoding="utf-8", errors="ignore"):
                line = line.split("#", 1)[0].strip()
                if line:
                    excludes.append(f":(exclude){line}")
        r = subprocess.run(["git", "-C", tmp, "grep", "-nIE", _LEAK, "--", ".", *excludes],
                           capture_output=True, text=True)
        hits = [l for l in r.stdout.splitlines()
                if l and not re.search(_PLACEHOLDER, l)]
        return hits
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- landing check (horde brief hypersaw-010) ---------------------------------
# GitHub shows a PR as MERGED whichever branch it merged into. A stacked PR
# whose base merged first lands on the base's dead branch: the work looks
# shipped and is not on the default branch. horde hit it twice in one week (a
# PR merged eight seconds after its base, before GitHub retargeted it). Only
# the remote can show this, and nobody sees it once the PR page says "merged".
LANDING_DAYS = 14


def unlanded(prs, default, status_of, now, days=LANDING_DAYS):
    """{base branch: [PR numbers]} merged within `days` and not on `default`.

    Pure: `prs` is `gh pr list --json number,baseRefName,headRefOid,mergeCommit,
    mergedAt` output; `status_of(oid)` is GitHub's compare status of a commit
    against the default branch, where `behind`/`identical` mean "an ancestor".
    A PR merged INTO the default branch is landed by definition and costs no
    call. Otherwise it is landed if its HEAD commit reached the default branch
    (a later merge or catch-up carried it), or failing that its merge commit.
    The head is asked first because it is the one a catch-up carries: the first
    live run flagged four repaired PRs when only the merge commit was asked.
    Limit, stated: work re-applied as NEW commits (a squash, a cherry-pick) is
    on the default branch and still reported; the line says check, not lost."""
    out = {}
    for pr in prs:
        try:
            merged = datetime.datetime.strptime(pr["mergedAt"], "%Y-%m-%dT%H:%M:%SZ")
        except (KeyError, TypeError, ValueError):
            continue
        if (now - merged).days > days or pr.get("baseRefName") == default:
            continue
        oids = [pr.get("headRefOid"), (pr.get("mergeCommit") or {}).get("oid")]
        if not any(o and status_of(o) in ("behind", "identical") for o in oids):
            out.setdefault(pr.get("baseRefName"), []).append(pr["number"])
    return {base: sorted(nums) for base, nums in out.items()}


def unlanded_merges(name, branch):
    """{base branch: [PR numbers]} for one repo, or None if it cannot be asked.

    The search is filtered SERVER-side to the window and to PRs whose base is
    not the default branch. Listing the latest 50 merges and filtering here
    covered two days of a busy repo (horde merged 200+ in 14 days), and a
    weekly run then never looked at the other five. A compare call that fails
    makes the whole repo UNKNOWN: "could not ask" is not "not landed"."""
    since = (datetime.datetime.now(datetime.timezone.utc)
             - datetime.timedelta(days=LANDING_DAYS)).strftime("%Y-%m-%d")
    try:
        prs = json.loads(_gh("pr", "list", "-R", f"{ORG}/{name}", "--state", "merged",
                             "--search", f"merged:>={since} -base:{branch}", "--limit", "1000",
                             "--json", "number,baseRefName,headRefOid,mergeCommit,mergedAt"))

        def status_of(oid):
            return _gh("api", f"repos/{ORG}/{name}/compare/{branch}...{oid}",
                       "--jq", ".status").strip()
        return unlanded(prs, branch, status_of,
                        datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
    except (RuntimeError, ValueError):
        return None


def main():
    try:
        repos = list_repos()
    except Exception as exc:  # noqa: BLE001 — surface, never swallow
        print(f"ALGEDONIC-UNKNOWN: could not list repos ({exc})")
        return 1

    pain, unknown = [], []
    for name, vis, branch in repos:
        red = default_branch_red(name, branch)
        if red is None:
            unknown.append(f"{name}: CI state unqueryable")
        elif red:
            pain.append(f"CI RED on {name}@{branch}")
        stray = unlanded_merges(name, branch)
        if stray is None:
            unknown.append(f"{name}: merged PRs unqueryable")
        # One line per base branch, not per PR: a repo whose GitHub default
        # branch is not the branch its work merges into (Maw: default `spinup`,
        # 43 PRs into `main`) is ONE fact, and 43 lines would mute the channel.
        for base, nums in sorted((stray or {}).items()):
            shown = " ".join(f"#{n}" for n in nums[:6]) + (" …" if len(nums) > 6 else "")
            pain.append(f"MERGED BUT NOT ON {branch}: {name}, {len(nums)} PR(s) into '{base}' "
                        f"({shown}) — check the work reached {branch}, or that {branch} "
                        f"is the right default branch")
        if vis == "PUBLIC":
            hits = public_leak(name, branch)
            if hits is None:
                unknown.append(f"{name}: public clone/scan failed")
            elif hits:
                pain.append(f"PUBLIC LEAK in {name}: {len(hits)} line(s), e.g. "
                            + hits[0][:120])

    for u in unknown:
        print(f"UNKNOWN  {u}")
    for p in pain:
        print(f"PAIN     {p}")
    if pain:
        print(f"\nalgedonic: {len(pain)} pain signal(s) across {len(repos)} repos")
        return 2
    print(f"algedonic: quiet across {len(repos)} repos"
          + (f" ({len(unknown)} unverifiable)" if unknown else ""))
    # Unverifiable-but-no-pain is reported, not escalated: the point of the
    # channel is high-signal. But it must never be reported as *clean*.
    return 0


if __name__ == "__main__":
    sys.exit(main())
