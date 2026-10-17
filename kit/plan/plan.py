#!/usr/bin/env python3
"""plan — the plan map: one source, generated views, headless checks.

DRAFT of the opt-in kit module of Decision 97 (horde brief hypersaw-016),
first run on autonomous itself. The format is `kit.plan/0`, open for objection
in thread plan-map before the module ships to other repos.

    plan.py build <dir>      regenerate <dir>/PLAN.md and <dir>/plan-map.html
    plan.py check <dir>      the headless checks (exit 1 if any is red)

<dir> holds `parts.json` (the plan's structure) and `queue.json` (the decision
queue of Decision 90: what is waiting on the human). Both views are GENERATED
from them, never hand-copied: two hand-written copies drifted in horde
(lesson 4 of the brief). The repo's ROADMAP.md stays the single source of
truth for task state. This is a MAP of its records, not a second copy, so
every part cites the rows and decisions that govern it.

The checks need no browser and no model (Layer-0), and each has a must-fail
control in test_plan.py:
  1. every cited ROADMAP row, decision and file exists;
  2. the dependency graph is acyclic;
  3. ids, statuses and edges are well formed (closed vocabulary);
  4. the generated files match their source;
  5. a status other than `planned` cites at least one record, and a status
     that changed since HEAD changed its basis too (an agent's reading goes in
     as a proposal, never as a closure: brief lesson 2);
  6. every `code` path matches a tracked file;
  7. queue items name real parts and carry a recommendation.
Reported, never red (observe first, Decision 97): freshness (decisions and
ROADMAP commits since the plan was verified), the computed critical path to
each target with ties, and parts that are further along than a part they
cite as a prerequisite.
"""
import json, os, re, subprocess, sys

FORMAT = "kit.plan/0"
QUEUE_FORMAT = "kit.queue/0"
# One vocabulary for every repo. horde and loupe hand-drew maps with two
# different ones (built/ruled/post-1.0 vs built/ready/later) before this
# module existed; that is the drift a kit module is for.
STATUSES = ["closed", "built", "in progress", "ruled", "planned", "later", "parked", "superseded"]
DONE = {"closed", "superseded"}
ID = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
_HERE = os.path.dirname(os.path.abspath(__file__))


# --- loading -----------------------------------------------------------------
def load(d):
    with open(os.path.join(d, "parts.json"), encoding="utf-8") as fh:
        plan = json.load(fh)
    queue = {"format": QUEUE_FORMAT, "items": []}
    q = os.path.join(d, "queue.json")
    if os.path.isfile(q):
        with open(q, encoding="utf-8") as fh:
            queue = json.load(fh)
    return plan, queue


def repo_root(d):
    out = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True).stdout.strip()
    return out or os.path.abspath(os.path.join(d, ".."))


def _read(root, rel):
    try:
        with open(os.path.join(root, rel), encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


def row_exists(roadmap, ref):
    """A ROADMAP row is cited by its bold label: `K0` matches `**K0 —`,
    `Phase R` matches `**Phase R —`, `A. S4 freshness` matches that bold
    run, and a heading is cited by its text (`Parallel track — Kit v2`). The
    lookahead stops `A` matching `**A0`."""
    if re.search(r"^#+ " + re.escape(ref) + r"\b", roadmap, re.M):
        return True
    return re.search(r"\*\*(?:Phase )?" + re.escape(ref) + r"(?=[\s.—:(*,])", roadmap) is not None


def decision_numbers(decisions):
    return {int(m) for m in re.findall(r"^(\d+)\. \*\*", decisions, re.M)}


def tracked(root):
    # --others --exclude-standard: a file about to be committed counts. Without
    # it a new part's code path reads missing until the commit lands, and the
    # check goes red on the change that adds the part.
    out = subprocess.run(["git", "-C", root, "ls-files", "--cached", "--others", "--exclude-standard"],
                         capture_output=True, text=True).stdout
    return out.splitlines()


def edges(plan):
    """(from, to, cited) for every dependency: `to` needs `from`."""
    out = []
    for p in plan["parts"]:
        out += [(n, p["id"], True) for n in p.get("needs", [])]
        out += [(n, p["id"], False) for n in p.get("needs_inferred", [])]
    return out


# --- the checks ----------------------------------------------------------------
def check(d, head_plan=None):
    """[(check number, ok, message)]. `head_plan` is the plan as committed at
    HEAD (for check 5); None reads it from git."""
    plan, queue = load(d)
    root = repo_root(d)
    roadmap, decisions = _read(root, "ROADMAP.md"), _read(root, "DECISIONS.md")
    have = decision_numbers(decisions)
    files = tracked(root)
    parts = plan.get("parts", [])
    ids = [p.get("id") for p in parts]
    known = set(ids)
    res = []

    # 1. cited records exist
    bad = []
    for p in parts:
        for r in p.get("rows", []):
            if not row_exists(roadmap, r):
                bad.append(f"{p['id']}: row '{r}' is not in ROADMAP.md")
        for a in p.get("adrs", []):
            if a not in have:
                bad.append(f"{p['id']}: Decision {a} is not in DECISIONS.md")
        for b in p.get("basis", []):
            bad += [f"{p['id']}: basis {e}" for e in _basis_errors(b, roadmap, have, files)]
    res.append((1, not bad, "; ".join(bad) or f"{sum(len(p.get('rows', [])) for p in parts)} rows, "
                f"{sum(len(p.get('adrs', [])) for p in parts)} decisions and every basis exist"))

    # 3. well formed (run before 2: a cycle check over unknown ids means little)
    bad = []
    if plan.get("format") != FORMAT:
        bad.append(f"format is {plan.get('format')!r}, want {FORMAT!r}")
    dup = sorted({i for i in ids if ids.count(i) > 1})
    bad += [f"duplicate id {i}" for i in dup]
    for p in parts:
        if not ID.match(str(p.get("id", ""))):
            bad.append(f"bad id {p.get('id')!r}")
        if p.get("status") not in STATUSES:
            bad.append(f"{p.get('id')}: status {p.get('status')!r} is not in the vocabulary")
        for n in p.get("needs", []) + p.get("needs_inferred", []):
            if n not in known:
                bad.append(f"{p['id']}: needs unknown part {n!r}")
        if not p.get("title") or not p.get("what"):
            bad.append(f"{p.get('id')}: a part needs a title and a one-line `what`")
    for t in plan.get("targets", []):
        if t not in known:
            bad.append(f"target {t!r} is not a part")
    used = {p.get("track") for p in parts}
    bad += [f"track {t!r} is declared but no part uses it" for t in plan.get("tracks", []) if t not in used]
    res.append((3, not bad, "; ".join(bad) or f"{len(parts)} parts, every id, status and edge well formed"))

    # 2. acyclic
    cyc = find_cycle(plan) if not bad else None
    res.append((2, cyc is None, f"cycle: {' -> '.join(cyc)}" if cyc else "the dependency graph is acyclic"))

    # 4. generated files match their source
    bad = []
    for name, want in (("PLAN.md", render_md(plan, queue, d)), ("plan-map.html", render_html(plan, queue, d))):
        if _read(d, name) != want:
            bad.append(f"{name} differs from what parts.json generates: run `plan.py build {d}`")
    res.append((4, not bad, "; ".join(bad) or "PLAN.md and plan-map.html match their source"))

    # 5. status changes are cited
    bad = []
    for p in parts:
        if p.get("status") != "planned" and not p.get("basis"):
            bad.append(f"{p['id']}: status '{p.get('status')}' cites no record")
    prev = head_plan if head_plan is not None else _head_plan(d, root)
    if prev:
        before = {p.get("id"): p for p in prev.get("parts", [])}
        for p in parts:
            o = before.get(p["id"])
            if o and o.get("status") != p.get("status") and o.get("basis") == p.get("basis"):
                bad.append(f"{p['id']}: status moved '{o.get('status')}' -> '{p.get('status')}' "
                           f"with no new record in its basis")
    res.append((5, not bad, "; ".join(bad) or "every status cites a record; no uncited status change"))

    # 6. code paths
    bad = []
    for p in parts:
        for c in p.get("code", []):
            if not _code_files(c, files):
                bad.append(f"{p['id']}: code '{c}' matches no tracked file")
    res.append((6, not bad, "; ".join(bad) or f"{sum(len(p.get('code', [])) for p in parts)} code paths, each tracked"))

    # 7. queue
    bad = []
    if queue.get("format") != QUEUE_FORMAT:
        bad.append(f"queue format is {queue.get('format')!r}, want {QUEUE_FORMAT!r}")
    qids = [q.get("id") for q in queue.get("items", [])]
    bad += [f"duplicate queue id {i}" for i in sorted({i for i in qids if qids.count(i) > 1})]
    for q in queue.get("items", []):
        for k in ("id", "question", "raised", "recommendation", "lands_in"):
            if not q.get(k):
                bad.append(f"queue {q.get('id')}: missing {k}")
        for b in q.get("blocks", []):
            if b not in known:
                bad.append(f"queue {q.get('id')}: blocks unknown part {b!r}")
    res.append((7, not bad, "; ".join(bad) or f"{len(queue.get('items', []))} decisions waiting, each well formed"))
    return sorted(res)


def _basis_errors(b, roadmap, have, files):
    if re.fullmatch(r"D\d+", b):
        return [] if int(b[1:]) in have else [f"{b} is not in DECISIONS.md"]
    if b.startswith("R:"):
        return [] if row_exists(roadmap, b[2:]) else [f"{b}: row not in ROADMAP.md"]
    if b.startswith("file:"):
        return [] if _code_files(b[5:], files) else [f"{b}: no tracked file"]
    return [f"{b!r}: a basis is D<n>, R:<row> or file:<path>"]


def _code_files(c, files):
    c = c.rstrip("/")
    return [f for f in files if f == c or f.startswith(c + "/")]


def _head_plan(d, root):
    rel = os.path.relpath(os.path.join(d, "parts.json"), root)
    out = subprocess.run(["git", "-C", root, "show", f"HEAD:{rel}"], capture_output=True, text=True)
    try:
        return json.loads(out.stdout) if out.returncode == 0 else None
    except ValueError:
        return None


def find_cycle(plan):
    g = {}
    for a, b, _ in edges(plan):
        g.setdefault(a, []).append(b)
    state, stack = {}, []

    def dfs(n):
        state[n] = 1; stack.append(n)
        for m in sorted(g.get(n, [])):
            if state.get(m) == 1:
                return stack[stack.index(m):] + [m]
            if not state.get(m):
                c = dfs(m)
                if c:
                    return c
        state[n] = 2; stack.pop()
        return None
    for n in sorted(g):
        if not state.get(n):
            c = dfs(n)
            if c:
                return c
    return None


# --- reported, never red -----------------------------------------------------------
def critical_paths(plan):
    """{target: (length, [chains])}: the longest chains of UNFINISHED parts that
    end at each target, every tie listed. Computed, not drawn (brief lesson 6:
    a hand-highlighted path was a judgment the check could only verify).
    Only CITED edges count: through an inferred one, the plan's own guess
    would decide what is critical (it did, on the first run)."""
    by = {p["id"]: p for p in plan["parts"]}
    # Unknown ids are check 3's to report; here they are skipped, so a broken
    # plan still renders and the check can say what is wrong.
    needs = {p["id"]: [n for n in p.get("needs", []) if n in by] for p in plan["parts"]}
    memo = {}

    def longest(n):
        if n in memo:
            return memo[n]
        if by[n].get("status") in DONE:
            memo[n] = (0, [[]])
            return memo[n]
        best, chains = 0, [[]]
        for m in sorted(needs[n]):
            ln, ch = longest(m)
            if ln > best:
                best, chains = ln, [c[:] for c in ch]
            elif ln == best and ln > 0:
                chains += [c[:] for c in ch]
        memo[n] = (best + 1, [c + [n] for c in chains])
        return memo[n]
    return {t: longest(t) for t in plan.get("targets", []) if t in by}


def ahead_of_prerequisites(plan):
    """Parts recorded further along than a part they cite as a prerequisite:
    the record contradicts itself, and the plan says so rather than choosing."""
    rank = {s: i for i, s in enumerate(["closed", "built", "in progress", "ruled", "planned", "later", "parked"])}
    by = {p["id"]: p for p in plan["parts"]}
    out = []
    for p in plan["parts"]:
        for n in p.get("needs", []):
            q = by.get(n)
            if q and p["status"] in ("closed", "built") and rank.get(q["status"], 9) > rank["built"]:
                out.append(f"`{p['id']}` is {p['status']}, but it cites `{n}` ({q['status']}) as a prerequisite")
    return out


def freshness(plan, root):
    v = plan.get("verified", {})
    have = decision_numbers(_read(root, "DECISIONS.md"))
    newer = sorted(n for n in have if n > int(v.get("decisions_max", 0)))
    out = subprocess.run(["git", "-C", root, "rev-list", "--count", f"{v.get('roadmap_commit', 'HEAD')}..HEAD",
                          "--", "ROADMAP.md"], capture_output=True, text=True)
    commits = int(out.stdout.strip()) if out.returncode == 0 and out.stdout.strip().isdigit() else None
    return {"decisions_since": newer, "roadmap_commits_since": commits}


# --- generation ----------------------------------------------------------------
def _data(plan, queue, d):
    return {"plan": plan, "queue": queue, "statuses": STATUSES,
            "critical": {t: {"length": ln, "chains": ch} for t, (ln, ch) in critical_paths(plan).items()},
            "ahead": ahead_of_prerequisites(plan)}


def render_md(plan, queue, d):
    parts = plan["parts"]
    v = plan.get("verified", {})
    unblocks = {}
    for a, b, _ in edges(plan):
        unblocks.setdefault(a, []).append(b)
    count = {s: sum(1 for p in parts if p["status"] == s) for s in STATUSES}
    L = [f"# {plan.get('title', 'Plan of record')}", "",
         "<!-- GENERATED by kit/plan/plan.py from parts.json and queue.json. Do not edit:",
         "     edit the source and run `python3 kit/plan/plan.py build plan`. -->", "",
         plan.get("about", "").strip(), "",
         f"**Last verified: {v.get('date')}**, against ROADMAP.md at `{v.get('roadmap_commit')}` and "
         f"DECISIONS.md through Decision {v.get('decisions_max')}. ROADMAP.md outranks this file.", "",
         "The picture: [`plan-map.html`](plan-map.html).", "",
         "## Status", "",
         " · ".join(f"{count[s]} {s}" for s in STATUSES if count[s]), "",
         "| Status | Means |", "|---|---|"]
    meaning = plan.get("status_meaning", {})
    L += [f"| {s} | {meaning.get(s, '')} |" for s in STATUSES]
    L += ["", "## Parts", "",
          "| Part | Status | Rows | Decisions | Needs | What |", "|---|---|---|---|---|---|"]
    for p in parts:
        needs = ", ".join([f"`{n}`" for n in p.get("needs", [])] + [f"`{n}`?" for n in p.get("needs_inferred", [])])
        L.append(f"| `{p['id']}` {p['title']} | {p['status']} | {', '.join(p.get('rows', [])) or '—'} | "
                 f"{', '.join(str(a) for a in p.get('adrs', [])) or '—'} | {needs or '—'} | {p['what']} |")
    L += ["", "`x`? marks a dependency the records do not state: the plan's inference, drawn dashed on the map.", ""]
    L += ["## Critical path", ""]
    for t, (ln, chains) in critical_paths(plan).items():
        L.append(f"To `{t}`: {ln} unfinished part{'s' if ln != 1 else ''}"
                 + (f", {len(chains)} tied chains:" if len(chains) > 1 else ":"))
        L += [f"- {' → '.join(f'`{c}`' for c in ch)}" for ch in chains]
        L.append("")
    L += ["## Waiting on the human", ""]
    items = sorted(queue.get("items", []), key=lambda q: (str(q.get("raised", "")), str(q.get("id", ""))))
    if not items:
        L.append("Nothing.")
    for q in items:
        L.append(f"- **`{q.get('id')}`** (raised {q.get('raised')}; blocks "
                 f"{', '.join(f'`{b}`' for b in q.get('blocks', [])) or 'nothing named'}): {q.get('question')} "
                 f"*Recommendation:* {q.get('recommendation')} *Lands in:* {q.get('lands_in')}.")
    L += ["", "## Inconsistencies found", ""]
    inc = list(plan.get("inconsistencies", [])) + [f"{a} (computed)" for a in ahead_of_prerequisites(plan)]
    L += [f"- {i}" for i in inc] or ["None."]
    L.append("")
    return "\n".join(L)


def render_html(plan, queue, d):
    with open(os.path.join(_HERE, "map_template.html"), encoding="utf-8") as fh:
        tpl = fh.read()
    blob = json.dumps(_data(plan, queue, d), sort_keys=True, ensure_ascii=False).replace("</", "<\\/")
    return tpl.replace("__PLAN_TITLE__", plan.get("title", "Plan map")).replace("/*__PLAN_DATA__*/null", blob)


def build(d):
    plan, queue = load(d)
    for name, body in (("PLAN.md", render_md(plan, queue, d)), ("plan-map.html", render_html(plan, queue, d))):
        with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
            fh.write(body)
    print(f"plan: wrote {d}/PLAN.md and {d}/plan-map.html")


def main(argv):
    if len(argv) != 3 or argv[1] not in ("build", "check"):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    d = argv[2]
    if argv[1] == "build":
        build(d)
        return 0
    res = check(d)
    plan, _ = load(d)
    for n, ok, msg in res:
        print(f"  {'ok  ' if ok else 'RED '} {n}. {msg}")
    f = freshness(plan, repo_root(d))
    print(f"  info  freshness: {len(f['decisions_since'])} decision(s) and "
          f"{f['roadmap_commits_since']} ROADMAP commit(s) since the plan was verified "
          f"{('(' + ', '.join(f'D{n}' for n in f['decisions_since']) + ')') if f['decisions_since'] else ''}")
    for t, (ln, ch) in critical_paths(plan).items():
        print(f"  info  critical path to {t}: {ln} parts, {len(ch)} chain(s)")
    for a in ahead_of_prerequisites(plan):
        print(f"  info  {a}")
    red = [n for n, ok, _ in res if not ok]
    print(f"plan check: {'RED ' + str(red) if red else 'green'}")
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
