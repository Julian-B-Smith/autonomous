#!/usr/bin/env python3
"""ball_scan — who owes whom, and since when.

The INTEGRATIONS protocol gives every exchange a `ball:` field so exactly one
side owns the next move. It assigns responsibility; NOTHING escalates it. Three
exchanges in one week were found only because a human happened to mention them:
distillery-002 sat 13 days past `respond-by` with named content blocked behind
it, and two mailbox writes sat untracked for ~12 days each. The field worked;
the absence of a sweep over it did not.

Deterministic, no model calls, read-only — same class as leak_scan.

THE UNIT IS THE EXCHANGE ID, NOT THE FILE. A thread's opening `brief.md` keeps
`ball: provider, status: filed` forever; the answer lands in a *sibling* file.
Per-file evaluation therefore reports every answered thread as permanently
overdue, which is worse than no check at all — a scanner that always cries wolf
is a scanner nobody reads. Files are grouped by their `id:` frontmatter and the
thread's state is taken from its most recent member.
"""

import datetime
import glob
import os
import re

# A thread in one of these states owes nobody anything.
TERMINAL = {"closed", "ratified", "shipped", "withdrawn", "declined", "superseded"}

# Most-recent-wins, in order of decisiveness. `ratified` outranks `responded`
# outranks `filed` because a thread can be re-filed (`refreshed`) after an answer.
_DATE_FIELDS = ("ratified", "responded", "refreshed", "filed")

_FM = re.compile(r"\A---\s*\n(.*?)\n---", re.S)

# Files that MOVE a ball rather than open a question. Naming is the
# fleet's real convention and is stable; ordering by date/mtime is not
# (day-resolution dates, and editing a file changes its mtime).
_ROLE_ANSWERER = re.compile(r"^(response|ratif|notice|ack)", re.I)


def _field(fm, name):
    m = re.search(rf"^{name}:\s*(.+?)\s*$", fm, re.M)
    return m.group(1).strip() if m else None


def _state(status):
    """The STATE a status line declares: its first word, lowercased, with any
    glued punctuation dropped. A status may explain itself — `closed — all
    three answers taken`, `shipped—see PR #12` — and only the leading word is
    the state; the rest is prose for the reader.

    First word, deliberately — not `startswith` and not a substring test: a
    status like `open — not closed until you confirm` contains a terminal word
    and must stay open. Exact whole-line matching, the previous rule, left 11
    closed files across three repos reading open for weeks (HYPERSAW notice
    terminal-status-exact-match, 2026-09-20), and the session brief printed
    them at every open — the cry-wolf failure this module exists to avoid."""
    m = re.match(r"[a-z][a-z_-]*", (status or "").strip().lower())
    return m.group(0) if m else ""


def _parse(path):
    """Frontmatter of one exchange file, or None if it isn't one."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            head = fh.read(4096)
    except OSError:
        return None
    m = _FM.match(head)
    if not m:
        return None
    fm = m.group(1)
    if not _field(fm, "id"):
        return None                      # not an exchange; some other fronted doc
    dates = [d for d in (_field(fm, f) for f in _DATE_FIELDS) if d]
    return {
        "path": path,
        "id": _field(fm, "id"),
        "ball": (_field(fm, "ball") or "").lower(),
        "status": (_field(fm, "status") or "").lower(),
        "state": _state(_field(fm, "status")),   # the first word; see _state
        "respond_by": _field(fm, "respond-by"),
        # Sort key: the newest date the file claims. Files with no date at all
        # sort oldest, so a dated answer always outranks an undated opener.
        "date": max(dates) if dates else "",
        # Same-day tiebreak. Exchange dates have DAY resolution, and a live
        # channel turns around inside a day: FOUNDATIONS filed a new proposal
        # (ball: provider) hours after our response (ball: consumer), all
        # stamped 2026-08-09. Ordering on the date alone fell through to
        # alphabetical filename, which put `response.md` last and reported the
        # ball as theirs while it was actually ours.
        # CAVEAT: a fresh `git clone` stamps every file with checkout time, so
        # this degrades to filename order there. Day-resolution dates are the
        # real limitation; a monotonic `seq:` field in the protocol would fix
        # it properly. Filed as a known gap rather than papered over.
        "mtime": os.path.getmtime(path) if os.path.exists(path) else 0.0,
    }


def _ball_is_ours(ball, repo_name):
    """True when the ball sits on the repo that OWNS this mailbox.

    Tolerant on purpose: the protocol says `provider`/`consumer`, but real
    exchanges also name the repo directly (Audiology's template writes
    `ball: audiology`). Unrecognized values are treated as NOT ours and
    reported verbatim — under-claiming is safe, silently absorbing another
    project's obligation is not.
    """
    token = _ball_token(ball)
    if not token or token in ("none", "-"):
        return False
    return token == "provider" or token == repo_name.lower().split("/")[-1]


def _ball_token(ball):
    """The bare holder token, stripped of any prose qualifier.

    Real exchanges annotate the field — `ball: consumer (ratify B23 locally and
    proceed)`, `ball: none (F2 opens on FOUNDATIONS' schedule)`. Whole-string
    comparison made every annotated ball unrecognized, which for `provider (…)`
    means an obligation ON US reported as not ours: a FALSE NEGATIVE, the
    direction that loses work, in the check whose entire job is not losing work.
    Found 2026-08-09 while answering "is there a HYPERSAW brief?" — the annotated
    forms live in FOUNDATIONS' and Tonality's mailboxes, not in autonomous's, so
    no fixture here would have caught it.
    """
    if not ball:
        return ""
    return re.split(r"[\s(,;:—-]", ball.strip(), 1)[0].strip().lower()


def scan_repo(path, repo_name, today=None):
    """Open exchange threads in one repo's mailbox.

    Returns a list of dicts: id, dir, ball, ours, status, respond_by,
    days_overdue (None when not past due), untracked (mailbox file not in git).
    """
    today = today or datetime.date.today()
    files = []
    for f in glob.glob(os.path.join(path, "integrations", "*", "*.md")):
        p = _parse(f)
        if p:
            files.append(p)

    threads = {}
    for f in files:
        threads.setdefault(f["id"], []).append(f)

    out = []
    for tid, members in sorted(threads.items()):
        # Closure is MONOTONIC and beats date-ordering: if any member declares a
        # terminal status the thread is done. Trusting "latest file wins" here
        # reported antiphon-001 as 12 days overdue when its ratification.md said
        # `status: closed` — the ratification carried the same `responded:` date
        # as the response it closed, so the tiebreak picked the wrong file.
        # Exchange dates are hand-written and will collide; closure is a fact.
        if any(m["state"] in TERMINAL for m in members):
            continue
        # Only files that ASSERT a ball determine who holds it. `ball: none`
        # marks a file that deliberately moves nothing — an informational note,
        # an FYI. Treating those as "latest wins" let FOUNDATIONS' informational
        # note, filed 34 seconds after their actual proposal, mask a live
        # `ball: provider` ask. A thread is not a linear conversation; concurrent
        # members are normal, so the ball comes from the newest file that claims
        # one, not from the newest file.
        claimants = [m for m in members
                     if _ball_token(m["ball"]) not in ("", "none", "-")]
        if not claimants:
            continue                       # open, but nobody is holding anything
        latest = max(claimants, key=lambda m: (m["date"], m["mtime"], m["path"]))
        # The live commitment is the LATEST respond-by in the thread: a refile
        # or a counter-brief resets the clock, and honouring a superseded date
        # would report an obligation nobody currently holds.
        deadlines = [m["respond_by"] for m in members if m["respond_by"]]
        respond_by = max(deadlines) if deadlines else None
        ours = _ball_is_ours(latest["ball"], repo_name)

        # Overdue is computed ONLY when the ball is ours. A `respond-by` binds
        # whoever holds the ball; once we answer and the ball moves, that date is
        # satisfied, not breached. Without this guard every answered thread
        # reported as overdue forever — the exact false-positive flood that
        # trains a reader to skip the section.
        overdue = None
        if ours and respond_by:
            try:
                d = (today - datetime.date.fromisoformat(respond_by)).days
                overdue = d if d > 0 else None
            except ValueError:
                overdue = None            # malformed date is not an obligation
        out.append({
            "id": tid,
            "dir": os.path.basename(os.path.dirname(latest["path"])),
            "ball": latest["ball"] or "(unset)",
            "ours": ours,
            "status": latest["status"] or "(unset)",
            "respond_by": respond_by,
            "days_overdue": overdue,
        })
    return out


def untracked_mailbox_files(path):
    """Mailbox files present on disk but not in git.

    A brief filed under the mailbox exception is written by a VISITOR and
    committed by a RESIDENT — so it is untracked by design for a moment, and
    invisible to anyone reading the repo through git for as long as the
    resident doesn't notice. Two sat ~12 days each. This is the check that
    would have caught them.
    """
    import subprocess
    try:
        out = subprocess.run(
            ["git", "-C", path, "ls-files", "--others", "--exclude-standard",
             "--", "integrations/"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [l for l in out.splitlines() if l.strip()]

def responses_awaiting(repo_name, roster_paths, today=None):
    """Exchanges in OTHER repos' mailboxes addressed to THIS repo, where the
    ball is now on us.

    Closes the delivery gap found 2026-08-17 (Decision 53): a response lands in
    the PROVIDER's repo, and `scan_repo` only ever reads a repo's own mailbox —
    so from the consumer's side an answered brief and an ignored one are
    identical. distillery filed against a stale premise for five days because
    of exactly this.

    This is a READ across territories, which writes-stay-home permits (it
    forbids WRITES). Nothing here mutates another repo; it reports what another
    repo has already said to us.
    """
    today = today or datetime.date.today()
    me = repo_name.lower().split("/")[-1]
    out = []
    for path in roster_paths:
        base = os.path.basename(path.rstrip("/")).lower()
        if base == me:
            continue                      # our own mailbox is scan_repo's job
        box = os.path.join(path, "integrations")
        if not os.path.isdir(box):
            continue
        for d in os.listdir(box):
            if d.lower() != me:
                continue                  # only channels addressed to US
            for th in scan_repo(path, me, today):
                # scan_repo evaluated ownership from the OTHER repo's point of
                # view; re-evaluate from ours. Their `ball: consumer` is our
                # ball when we are the consumer in that channel.
                if th["dir"].lower() != me:
                    continue
                token = _ball_token(th["ball"])
                ours = token in ("consumer", me)
                if ours:
                    out.append({**th, "in_repo": os.path.basename(path), "ours": True})
    return out


def _rel(f, root):
    """Repo-relative path with forward slashes on every platform. Consumers
    compare and print these (`integrations/peer/brief.md`); a backslash form
    from a Windows run is a different string for the same file, and the
    session brief, the Threads Board, and two tests all read it as one."""
    return os.path.relpath(f, root).replace(os.sep, "/")

def frontmatter_lies(path):
    """Threads whose opening file still claims the ball while an answer exists.

    hypersaw-001 round 2: the manual sweep that fixed this caught 21 of 23 —
    and one of the two misses was HYPERSAW's own brief, on the very thread
    that reported the bug. A sweep fixes instances; a gate fixes the class.
    Prose is the reminder, the gate is the enforcement.

    The rule: if any file in a thread names an `answered_by` target that
    EXISTS, no file in that thread may still read `ball: provider`. Asserts the
    effective state (does the answer exist on disk?) rather than the declared
    one (does someone say it was answered?).
    """
    out = []
    threads = {}
    for f in glob.glob(os.path.join(path, "integrations", "*", "*.md")):
        p = _parse(f)
        if p:
            threads.setdefault(p["id"], []).append((f, p))

    for tid, members in sorted(threads.items()):
        answered = False
        for f, m in members:
            try:
                with open(f, encoding="utf-8", errors="ignore") as fh:
                    head = fh.read(4096)
            except OSError:
                continue
            am = re.search(r"^answered_by:\s*(\S+)\s*$", head, re.M)
            if am and os.path.isfile(os.path.join(os.path.dirname(f), am.group(1))):
                answered = True
            # A sibling that RESPONDS is equally proof the thread moved.
            if m["state"] in ("responded", "ratified", "closed"):
                answered = True
        if not answered:
            continue
        # A thread can legitimately BOUNCE: HYPERSAW's ratification-001 claims
        # `ball: provider` after our response-001, and it is RIGHT to — a new
        # ask, not stale state.
        #
        # Ordering by (date, mtime) cannot separate the two here: exchange dates
        # are day-resolution and every file in that thread is 2026-08-18, so the
        # tiebreak falls to mtime — and merely EDITING an opener's frontmatter
        # makes it the newest file, which flipped this check's verdict mid-fix.
        # So this uses no ordering at all. It uses the fleet's actual, stable
        # filename convention: openers state a question, answerers move the ball.
        # An OPENER still claiming provider in a thread that has an ANSWERER is
        # stale; an ANSWERER claiming provider is a hand-back and is current.
        for f, m in members:
            if _ball_token(m["ball"]) != "provider":
                continue
            if _ROLE_ANSWERER.match(os.path.basename(f)):
                continue                   # a hand-back, not stale state
            if any(_ROLE_ANSWERER.match(os.path.basename(g)) for g, _ in members):
                out.append({"id": tid, "file": _rel(f, path),
                            "says": m["ball"], "status": m["status"]})
    return out


def cites_missing(path):
    """Threads that have moved past `filed` with no `cites:` key on the OPENING
    file — the resident-affirmed-at-intake rule (INTEGRATIONS §The ball,
    ratified 2026-09-02). Proves the field was filled, never that it was filled
    correctly: `cites: none` passes, and that is the stated limit of the gate.

    Only the opening brief/report is checked — `cites:` is an intake act, and
    responses/notices are answers to a thread that was already triaged. Only
    threads whose opening file is NOT still `filed` are checked, so a brief
    nobody has touched yet is not a failure: intake has not happened.
    """
    bad = []
    for f in glob.glob(os.path.join(path, "integrations", "*", "*.md")):
        p = _parse(f)
        if not p:
            continue
        base = os.path.basename(f)
        if _ROLE_ANSWERER.match(base):
            continue                                # answers are not intake
        if (p["state"] or "filed") == "filed":
            continue                                # not triaged yet — no duty yet
        with open(f, encoding="utf-8", errors="ignore") as fh:
            head = fh.read(4000)
        if not re.search(r"^cites:\s*\S", head, re.M):
            bad.append({"file": _rel(f, path), "id": p["id"],
                        "status": p["status"]})
    return bad

