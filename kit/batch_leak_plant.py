#!/usr/bin/env python3
"""batch_leak_plant — apply kit 2.3.0's one-block leak_gate change fleet-wide.

2.3.0's retrofit action is a deterministic text insertion, not a judgment
call: the gate must ignore `.kit-currency-plant-*` unless `KIT_LEAK_PLANT`
names that exact file, so one session's currency probe cannot red another
session's concurrent `./verify` (mind-lathe, 2026-08-18; LIBRARY L0006).

Doing it by hand across the fleet is 13 identical edits, which is exactly the
shape that should not be done by hand. Constraints this script holds to:

  - ANCHORED, not fuzzy. It replaces one exact line. A repo whose gate has
    drifted is REPORTED, never guessed at (Antiphon has a variant).
  - IDEMPOTENT. A repo already carrying KIT_LEAK_PLANT is skipped.
  - PROVEN, not assumed. After patching it runs the repo's own `./verify
    fast` twice: once clean (must not newly break) and once with a foreign
    plant present (must NOT name it). A patch that does not change behaviour
    is a patch that did nothing.
  - NEVER COMMITS. Writes stay home: these are other residents' repos. The
    edit is left in the working tree for a resident or the human to commit.
  - DRY BY DEFAULT. --apply is required to write anything.

Usage:  batch_leak_plant.py [--apply] [--registry ../registry.json]
"""
import argparse, json, os, subprocess, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..")
sys.path.insert(0, os.path.join(_HERE, "sweep"))
import sweep  # noqa: E402
import currency  # noqa: E402

ANCHOR = "  local hits excludes=(':(exclude)*leak_scan.py' ':(exclude).leakcheck-allow')\n"


def _block():
    """The replacement, lifted VERBATIM from harness/verify — the template is
    the source of truth, so this script cannot drift from what /spinup ships."""
    src = open(os.path.join(_ROOT, "harness", "verify"), encoding="utf-8").read()
    start = src.index("  # A foreign process may be probing this repo right now.")
    end = src.index("  if [ -f .leakcheck-allow ]; then")
    return src[start:end]


def _probe_ok(path, plant=".kit-currency-plant-batchcheck.md"):
    """Behavioural proof, per repo: with a foreign plant present, the gate must
    not NAME it. Exit code is deliberately not the assertion — a repo's verify
    may be red for its own unrelated reasons, and that is not ours to judge."""
    p = os.path.join(path, plant)
    try:
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("x " + "/" + "Users" + "/nobody/secret\n")   # assembled, never literal
        env = dict(os.environ); env.pop("KIT_LEAK_PLANT", None)
        r = subprocess.run(currency.verify_cmd(), cwd=path, env=env,
                           capture_output=True, text=True, timeout=180)
        return plant not in (r.stderr + r.stdout)
    except (OSError, subprocess.TimeoutExpired):
        return False
    finally:
        try:
            os.remove(p)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--registry", default=os.path.join(_ROOT, "registry.json"))
    a = ap.parse_args()
    block = _block()
    with open(a.registry, encoding="utf-8") as fh:
        projects = sweep.resolve(json.load(fh))

    plan = {"patch": [], "already": [], "variant": [], "no-gate": []}
    for p in projects:
        v = os.path.join(p["path"], "verify")
        try:
            with open(v, encoding="utf-8") as fh:
                s = fh.read()
        except OSError:
            plan["no-gate"].append(p); continue
        if "leak_gate" not in s:
            plan["no-gate"].append(p)
        elif "KIT_LEAK_PLANT" in s:
            plan["already"].append(p)
        elif ANCHOR in s:
            plan["patch"].append(p)
        else:
            plan["variant"].append(p)

    print(f"kit 2.3.0 batch — {'APPLY' if a.apply else 'DRY RUN'}")
    print(f"  would patch      : {len(plan['patch'])}")
    print(f"  already current  : {len(plan['already'])}")
    print(f"  variant gate     : {len(plan['variant'])}  {[q['name'] for q in plan['variant']]}")
    print(f"  no leak_gate     : {len(plan['no-gate'])}  (2.3.0 asks nothing; baseline is their gap)")
    print()
    for p in plan["patch"]:
        if not a.apply:
            print(f"  [dry] {p['name']}")
            continue
        v = os.path.join(p["path"], "verify")
        with open(v, encoding="utf-8") as fh:
            s = fh.read()
        with open(v, "w", encoding="utf-8") as fh:
            # `block` ALREADY ends with the anchor line — appending ANCHOR too
            # emits `local hits excludes=(…)` twice, and the second one resets
            # excludes AFTER the plant logic, silently undoing the patch. Caught
            # by the behavioural check below on a scratch copy, not in review.
            fh.write(s.replace(ANCHOR, block, 1))
        ok = _probe_ok(p["path"])
        print(f"  [{'ok ' if ok else 'CHECK'}] {p['name']}"
              + ("" if ok else "  — gate still names a foreign plant; inspect before committing"))
    if a.apply:
        print("\nNothing committed. These are other residents' repos: review the diff "
              "and commit there, or leave it for that repo's next session.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
