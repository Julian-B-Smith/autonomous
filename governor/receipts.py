#!/usr/bin/env python3
"""receipts — which repos' latest GREEN verify did less than it looks.

`red_records.py` answers "who is red". This answers the opposite failure,
which is the dangerous one because nothing announces it: a green record whose
gates skipped or judged nothing, or whose tree changed while verify ran
(horde brief hypersaw-010 P1: a parity gate exiting 0 on "0/0 scenarios", and
a sanitize job green on 47 of 74 oracles, each found by a human noticing).

Reads `.harness/last-verify.json`, which the kit's `record` writes with a
receipt from kit 2.9.0. The session brief calls `findings` for its own repo. A gate appears only if the repo's `./verify`
wraps it in `gate <name> …`, so an empty receipt means "not adopted", and is
counted and never read as "all gates ran".

REPORT ONLY, never writes (writes stay home), deterministic, no model calls.

Usage:  receipts.py [--registry ../registry.json]
"""
import argparse, json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..")
sys.path.insert(0, os.path.join(_ROOT, "kit", "sweep"))
import sweep  # noqa: E402


def _load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def findings(last):
    """Lines for one repo's latest record. Pure. Only a GREEN record is judged:
    a red one is `red_records.py`'s business and its receipt is cut short.

    Deliberately NOT here: "judged fewer cases than the run before". It was
    built and removed the same day (review, 2026-10-10): a drop showed for
    exactly one run and then became the new normal, and a `full` after a `fast`
    never compared. The floor (`gate --min-cases`) is the mechanism for that:
    it is pinned in the repo and it fails the run."""
    if not last or last.get("exit") != 0:
        return []
    out = []
    for g in last.get("gates") or []:
        if not isinstance(g, dict):
            continue
        if g.get("result") == "skipped":
            out.append(f"{g.get('name')}: skipped ({g.get('reason') or 'no reason given'})")
        elif g.get("cases") == 0:
            out.append(f"{g.get('name')}: ran and judged 0 cases")
    start, end = last.get("tree_start"), last.get("tree")
    if start and end and start != end:
        out.append("the tree changed WHILE verify ran: the record covers bytes no gate "
                   "judged (expected if verify regenerates files; otherwise re-run)")
    return out


def scan(registry):
    rows, adopted, total = [], 0, 0
    for p in sweep.resolve(registry):
        last = _load(os.path.join(p["path"], ".harness", "last-verify.json"))
        if last is None:
            continue
        total += 1
        adopted += bool(last.get("gates"))
        f = findings(last)
        if f:
            rows.append({"repo": p["name"], "target": last.get("target"), "findings": f})
    return sorted(rows, key=lambda r: r["repo"]), adopted, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default=os.path.join(_ROOT, "registry.json"))
    a = ap.parse_args()
    with open(a.registry, encoding="utf-8") as fh:
        rows, adopted, total = scan(json.load(fh))
    print(f"receipts: {adopted} of {total} repos with a verify record wrap their gates "
          f"(an unwrapped gate is invisible here)")
    for r in rows:
        print(f"  {r['repo']} [{r['target']}]")
        for f in r["findings"]:
            print(f"      {f}")
    if not rows:
        print("  no green record skipped a gate, judged nothing, or changed under verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
