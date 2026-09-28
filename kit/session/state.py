#!/usr/bin/env python3
"""state — the shared read-and-render routine behind /wakeup, /breakdown, /reorient.

Per briefs/2026-08-17-session-boundary.md §3: all three commands read the same
state and differ only in what they may WRITE. So the reading is one
deterministic module with no model in it, and the commands are thin wrappers.
That split is the AI/deterministic boundary doctrine applied to a session
boundary: rendering state and surveying the human is judgement; gathering it
is not.

Reads, in the brief's priority order: SESSION.md, ROADMAP (current phase),
DECISIONS (tail), REFLECTIONS.md, the last ./verify result, git status and
recent commits, recent traces/.

Deliberately does NOT run `./verify`. It reads the RECORDED result and says
how old it is, because running the oracle is a side effect with a cost and the
caller decides whether to pay it. A recorded result from a different commit is
reported as stale rather than as green — the same
declared-vs-effective distinction that cost the fleet a week.

  state.py [repo] [--json]
"""
import argparse, datetime, json, os, re, subprocess, sys
import time

_MAX_TAIL = 6


def _git(repo, *args, default=""):
    try:
        r = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                           text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else default
    except (OSError, subprocess.TimeoutExpired):
        return default


def _head(path, n=40):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return [next(fh, "") for _ in range(n)]
    except OSError:
        return []


def _session_md(repo):
    """The only prior-session context the next session trusts (brief §2)."""
    p = os.path.join(repo, "SESSION.md")
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8", errors="ignore") as fh:
        return fh.read()


# What a ROADMAP heading uses to say "this phase is the current one", taken from
# the fleet's own roadmaps (2026-09-27 survey), not guessed. The plain word
# "active" is NOT a marker: the kit's own template heading "Invariants under
# active protection" sits in a dozen roadmaps above the real phase, and matched
# first. Likewise "current" alone ("not in current scope"). Case-sensitive
# ACTIVE only when shouted or bolded, because that is how repos that use it write it.
_PHASE_MARK = re.compile(
    r"(?i:in[- ]progress|\u2190\s*current|current (?:phase|focus|frontier)|\(current\b|\u25b6)"
    r"|\bACTIVE\b|\*\*active\*\*", )


_BULLET_PHASE = re.compile(
    r"(?i:\u2190\s*current|current phase|\bphase\b[^.\n]{0,40}?(?:in[- ]progress|\bactive\b))")
_DONE_BEFORE = re.compile(r"(?i:\b(?:done|closed|completed?|shipped)\b|was:)|\bMET\b|\u2705")


def _current_phase(repo):
    """The phase ROADMAP marks as current. ROADMAP outranks other docs on
    direction (doctrine), so this is the authority on 'what are we doing'.

    HEADINGS only, and only an explicit marker (`_PHASE_MARK`). The first
    version took any line starting `#`, `-`, `*` or `|` containing current /
    in progress / active — so a bolded paragraph of a CLOSED phase's gate prose
    ("**Gate: MET.** … active") won over the in-progress heading below it
    (resume-workshop brief, 2026-09-27), and the template heading "Invariants
    under active protection" won in Sluice, Maw and ten others. None when
    nothing is marked: an honest blank beats a confident wrong phase."""
    p = os.path.join(repo, "ROADMAP.md")
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8", errors="ignore") as fh:
        lines = fh.readlines()
    for line in lines:
        if re.match(r"^#{1,6} ", line) and _PHASE_MARK.search(line):
            return line.strip()[:200]
    # Second pass, only when no heading is marked: some roadmaps mark the phase
    # in a bullet ("- **D3 — The analyst.** **← current phase.**" in distillery,
    # "- **Phase:** 0b in progress." in refraction-bench). Stricter than the
    # heading pass, because bullets are where SUB-items live: "Status: in
    # progress" in a bullet was a queue item or an intake brief in Maw, Sluice
    # and Tonality-Live, not the phase. So a bullet counts only if it says
    # "← current" / "current phase", or names a Phase next to an in-progress
    # marker — and nothing marking it DONE comes before the marker ("DONE … Was:
    # in-progress" in Sluice is history). Plain checkboxes are tasks, excluded.
    for line in lines:
        if not re.match(r"^\s*[-*|] (?!\[[ xX]\])", line):
            continue
        m = _BULLET_PHASE.search(line)
        if m and not _DONE_BEFORE.search(line[:m.start()]):
            return line.strip()[:200]
    return None


# A heading that carries an entry ID: "### D-043 — …", "## ADR-12", "## Decision
# 7", "### 118 — …", "## D1: …". The ID must be followed by punctuation-or-space,
# so a date heading ("## 2026-08-01 …") is not read as entry 2026.
_ID_HEADING = re.compile(r"^#{1,6}\s+(?:Decision\s+|ADR-?|DEC-?|D-?)?(\d+)(?=[.):]?\s|\s*[\u2014\u2013-]\s)")
_NUMBERED_LINE = re.compile(r"^(\d+)[.)]\s")


def _decisions_tail(repo, n=3):
    """The NEWEST decisions — by number where they are numbered, by file order
    where they are not.

    File order is not recency: this repo appends before a marker, so the last
    lines in the file are decisions 16-18 while the repo is at 66. Showing
    those to someone catching up is worse than showing nothing, because it
    looks like an answer. Where entries are numbered, the highest numbers are
    the newest — which is also why the next number is max+1, never last+1.

    WHICH lines are entries depends on the file's own style, decided once per
    file. If any heading carries an ID, headings are the entries and numbered
    lines are list items inside them — a body's "1.–4." outranked every real
    `### D-043` heading until 2026-09-27 (resume-workshop brief; the same shape
    in Sluice, Maw, HYPERSAW, FOUNDATIONS, Residuum, spectrogen). Otherwise
    top-level numbered lines are the entries, which is this repo's own style
    (`79. **…**` under a plain title), so that case must keep working."""
    p = os.path.join(repo, "DECISIONS.md")
    if not os.path.isfile(p):
        return []
    with open(p, encoding="utf-8", errors="ignore") as fh:
        lines = [l.rstrip("\n") for l in fh]
    by_heading = [(int(m.group(1)), l.strip()) for l in lines for m in [_ID_HEADING.match(l)] if m]
    if by_heading:
        return [h for _, h in sorted(by_heading, key=lambda t: t[0])[-n:]]
    by_line = [(int(m.group(1)), l.strip()) for l in lines for m in [_NUMBERED_LINE.match(l)] if m]
    if by_line:
        return [h for _, h in sorted(by_line, key=lambda t: t[0])[-n:]]
    heads = [l.strip() for l in lines if re.match(r"^#{1,3} ", l)]
    return heads[-n:]


def _reflections(repo):
    """Open questions and half-thoughts held between sessions (brief §2).
    Entries carry `raised_on:`; anything old is flagged for graduate-or-drop
    rather than allowed to accumulate (brief §5)."""
    p = os.path.join(repo, "REFLECTIONS.md")
    if not os.path.isfile(p):
        return {"exists": False, "entries": [], "stale": []}
    text = open(p, encoding="utf-8", errors="ignore").read()
    entries = re.findall(r"^- \[(\d{4}-\d{2}-\d{2})\]\s*(.+)$", text, re.M)
    today = datetime.date.today()
    stale = []
    for raised, body in entries:
        try:
            age = (today - datetime.date.fromisoformat(raised)).days
        except ValueError:
            continue
        if age >= 14:
            stale.append({"raised_on": raised, "age_days": age, "text": body[:160]})
    return {"exists": True,
            "entries": [{"raised_on": d, "text": t[:160]} for d, t in entries],
            "stale": stale}


def _verify_state(repo):
    """The RECORDED verify result, with its own staleness. `.harness/` is
    written by ./verify; a result recorded at a different commit says nothing
    about this one, and reporting it as green would be exactly the
    declared-vs-effective error the kit exists to prevent."""
    p = os.path.join(repo, ".harness", "last-verify.json")
    head = _git(repo, "rev-parse", "--short", "HEAD")
    if not os.path.isfile(p):
        return {"recorded": False, "stale": None, "note": "no recorded run"}
    try:
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return {"recorded": False, "stale": None, "note": "unreadable record"}
    stale = bool(head) and d.get("git") not in (head, None)
    return {"recorded": True, "exit": d.get("exit"), "at": d.get("ts"),
            "git": d.get("git"), "stale": stale,
            "note": ("recorded at a DIFFERENT commit — says nothing about HEAD"
                     if stale else "matches HEAD")}


def _traces(repo, n=3):
    d = os.path.join(repo, "traces")
    if not os.path.isdir(d):
        return []
    files = sorted((f for f in os.listdir(d) if f.endswith(".md")), reverse=True)
    return files[:n]


def _audit(repo):
    """Routine-audit staleness (hypersaw-003, kit 2.6.3). A repo declares an
    auditor either as `.claude/agents/auditor.md` or as a manifest field
    `auditor: {agent, cadence_days}`; reports live in `docs/audits/`. Age is
    by the newest report's mtime — a date in the filename would be nicer to
    read but is a convention no gate enforces, and mtime is what git checkout
    sets on every clone. None when the repo has no auditor: the line is then
    omitted, not "none", because absence of an auditor is not staleness."""
    manifest = os.path.join(repo, "project.manifest.json")
    cadence = 7
    declared = os.path.exists(os.path.join(repo, ".claude", "agents", "auditor.md"))
    try:
        with open(manifest, encoding="utf-8") as f:
            a = json.load(f).get("auditor")
        if a:
            declared = True
            cadence = int(a.get("cadence_days", cadence))
    except (OSError, ValueError, AttributeError):
        pass
    if not declared:
        return None
    d = os.path.join(repo, "docs", "audits")
    reports = sorted((os.path.getmtime(os.path.join(d, n)), n) for n in os.listdir(d)
                     if n.endswith(".md")) if os.path.isdir(d) else []
    if not reports:
        return {"cadence_days": cadence, "last": None, "age_days": None, "stale": True}
    mtime, name = reports[-1]
    age = int((time.time() - mtime) // 86400)
    return {"cadence_days": cadence, "last": f"docs/audits/{name}", "age_days": age,
            "stale": age >= cadence}


def gather(repo):
    return {
        "repo": os.path.basename(os.path.abspath(repo)),
        "branch": _git(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "head": _git(repo, "rev-parse", "--short", "HEAD"),
        "dirty": [l for l in _git(repo, "status", "--porcelain").splitlines() if l],
        "unpushed": _git(repo, "rev-list", "--count", "@{u}..HEAD", default="0"),
        "recent_commits": _git(repo, "log", "--oneline", "-5").splitlines(),
        "session_md": _session_md(repo),
        "phase": _current_phase(repo),
        "decisions_tail": _decisions_tail(repo),
        "reflections": _reflections(repo),
        "verify": _verify_state(repo),
        "traces": _traces(repo),
        "audit": _audit(repo),
    }


def render(s):
    """Text for a human or an agent to read at a session boundary. Facts only —
    what to DO with them is the command's judgement, not this module's."""
    L = [f"# {s['repo']} — session state",
         f"branch {s['branch']} @ {s['head'] or '(no commits)'}"
         f"{'  · ' + str(len(s['dirty'])) + ' uncommitted' if s['dirty'] else '  · clean tree'}"
         f"{'  · ' + s['unpushed'] + ' unpushed' if s['unpushed'] not in ('0', '') else ''}"]
    v = s["verify"]
    if not v["recorded"]:
        L.append(f"verify: {v['note']} — run ./verify fast to know")
    else:
        L.append(f"verify: exit {v['exit']} at {v.get('at')} ({v['note']})")
    if s["phase"]:
        L.append(f"phase:  {s['phase']}")
    else:
        L.append("phase:  none marked — mark the current phase's ROADMAP heading "
                 "\"IN PROGRESS\" or \"← current\" and this line will show it")
    if s["session_md"]:
        first = next((l for l in s["session_md"].splitlines() if l.strip()
                      and not l.startswith("#")), "")
        L.append(f"last close: {first[:150]}")
    else:
        L.append("last close: no SESSION.md — this repo has not closed a session yet")
    r = s["reflections"]
    if r["exists"]:
        L.append(f"reflections: {len(r['entries'])} open"
                 + (f", {len(r['stale'])} unaddressed 14+ days (graduate or drop)"
                    if r["stale"] else ""))
    a = s.get("audit")
    if a:
        if a["last"] is None:
            L.append(f"last audit: none — auditor declared, no report in docs/audits/ (cadence {a['cadence_days']}d)")
        else:
            L.append(f"last audit: {a['age_days']} days ago ({a['last']})"
                     + (f" — STALE at cadence {a['cadence_days']}d: /wakeup dispatches the auditor" if a["stale"] else ""))
    if s["decisions_tail"]:
        L.append("decisions (newest): " + " | ".join(d[:60] for d in s["decisions_tail"]))
    if s["traces"]:
        L.append("recent traces: " + ", ".join(s["traces"]))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    s = gather(a.repo)
    print(json.dumps(s, indent=2) if a.json else render(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
