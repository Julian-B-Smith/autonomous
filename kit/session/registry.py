#!/usr/bin/env python3
"""registry — which sessions are currently OPEN, across machines.

Per briefs/2026-08-17-session-boundary.md §4. Deliberately tiny:

  - ONE FILE PER SESSION, not one file of rows. Concurrent opens on two
    machines never touch the same path, so a merge is trivial and a conflict
    is impossible by construction.
  - Keyed by `session_id`, NOT by repo: two concurrent sessions in one repo
    (a fleet job and the human) are legible rather than a collision.
  - CONTAINS NO CONTENT — repo, session_id, machine, opened_at, plus (since
    O0, Decision 77) the FACTS a session was built against: its `~`-relative
    path, HEAD and branch at open, and hashes of the doctrine, kit and
    installed commands it loaded. Hashes and positions, never text, prompts,
    or identity: the oversight engine needs to know WHETHER a session drifted
    from the system, not what it was doing. It is the one sanctioned
    cross-repo write precisely because it carries nothing worth reading. dispatch and distillery read closed-session
    artifacts (SESSION.md, traces) and never this, so they cannot race a
    running build.
  - NEVER BLOCKS A SESSION (brief §5). No registry configured, unreachable,
    unwritable — every call degrades to a warning and a local marker. A
    bookkeeping store that can stop work is worse than no store.

Location is configured, not guessed: `KIT_SESSION_REGISTRY` env var, else
`~/.claude/session-registry` if it exists. The brief proposes a private repo
both machines already pull; that choice is the human's, and this module is
the one place it is named, so swapping to a hosted store later touches one
file (brief §4).

  registry.py open <repo> --session-id ID
  registry.py close --session-id ID [--state TEXT]
  registry.py sweep --older-than-hours 12 --reason TEXT
  registry.py list

Since O0 the SessionStart / SessionEnd hooks (`kit/hooks/session-open.py`,
`session-close.py`) call open and close; the commands no longer do. Closing
MOVES the record to `closed/` with how the tree was left, rather than deleting
it: "left dirty" is a finding the next session and the dashboard need, and a
deleted row cannot report it.
"""
import argparse, datetime, json, os, platform, socket, sys

_ENV = "KIT_SESSION_REGISTRY"
_FALLBACK = os.path.expanduser("~/.claude/session-registry")


def root():
    """Configured location, or None. None is a supported state, not an error."""
    p = os.environ.get(_ENV)
    if p:
        return os.path.expanduser(p)
    return _FALLBACK if os.path.isdir(_FALLBACK) else None


_MACHINE_ENV = "KIT_SESSION_MACHINE"


def _machine():
    """A label for this machine — overridable, because the default is not safe
    to commit.

    `platform.node()` returned "Julians-MacBook-Air" on the first live run: the
    default macOS hostname embeds the owner's NAME. That is fine in a local
    registry and is a personal-identity leak the moment this store is promoted
    to the shared private repo the brief proposes. Doctrine forbids committing
    machine identity, and a hostname is exactly that.

    So the label is configurable and the promotion step sets it — `mac`, `win`
    — rather than discovering the tension after the first push. Which machine
    holds a session open is load-bearing information; whose machine it is, is
    not.
    """
    override = os.environ.get(_MACHINE_ENV)
    if override:
        return override[:32]
    return platform.node().split(".")[0] or "unknown"


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def open_session(repo, session_id, at=None, facts=None):
    """Open, or REFRESH, this session's record. A resumed or compacted session
    fires SessionStart again with the same id: it keeps its original
    `opened_at` (it is the same session) but its facts are re-read, because a
    resumed session re-loads the doctrine and may be running newer rules."""
    r = root()
    row = {"repo": os.path.basename(os.path.abspath(repo)),
           "session_id": session_id,
           "machine": _machine(),
           "opened_at": at or _now()}
    if not r:
        return {"ok": False, "reason": "no registry configured", "row": row}
    p = os.path.join(r, f"{session_id}.json")
    try:
        with open(p, encoding="utf-8") as fh:
            prev = json.load(fh)
        row["opened_at"] = prev.get("opened_at", row["opened_at"])
        row["refreshed_at"] = _now()
    except (OSError, ValueError):
        pass
    row.update(facts or {})
    try:
        os.makedirs(r, exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(row, fh, indent=2)
        return {"ok": True, "row": row, "path": r}
    except OSError as e:
        return {"ok": False, "reason": f"registry unwritable: {e}", "row": row}


def close_session(session_id, state=None):
    """Move the record to `closed/` with `closed_at` and `close_state`. A
    manual close with no state says so rather than claiming the tree was
    clean — an unrecorded state is not a clean one."""
    r = root()
    if not r:
        return {"ok": False, "reason": "no registry configured"}
    p = os.path.join(r, f"{session_id}.json")
    if not os.path.isfile(p):
        return {"ok": True, "reason": "no row (already closed, or never opened)"}
    try:
        with open(p, encoding="utf-8") as fh:
            row = json.load(fh)
    except (OSError, ValueError):
        row = {"session_id": session_id}
    row["closed_at"] = _now()
    row["close_state"] = state or {"summary": "closed by command; tree state not recorded"}
    try:
        os.makedirs(os.path.join(r, "closed"), exist_ok=True)
        with open(os.path.join(r, "closed", f"{session_id}.json"), "w", encoding="utf-8") as fh:
            json.dump(row, fh, indent=2)
        os.remove(p)
        return {"ok": True, "row": row}
    except OSError as e:
        return {"ok": False, "reason": f"could not close row: {e}"}


def sweep_stale(older_than_hours, reason, now=None):
    """Close every open record older than the line, stating why. For rows no
    end hook will ever close: crashes, force-quits, and every row opened
    before the hooks existed. Returns the swept session ids."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    swept = []
    for row in list_open():
        try:
            t = datetime.datetime.strptime(row.get("opened_at", ""), "%Y-%m-%dT%H:%M:%SZ") \
                .replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            continue
        ref = row.get("refreshed_at")
        if ref:
            try:
                t = max(t, datetime.datetime.strptime(ref, "%Y-%m-%dT%H:%M:%SZ")
                        .replace(tzinfo=datetime.timezone.utc))
            except ValueError:
                pass
        if (now - t).total_seconds() / 3600 > older_than_hours:
            if close_session(row["session_id"], {"summary": f"unclean — {reason}"})["ok"]:
                swept.append(row["session_id"])
    return swept


def list_open():
    r = root()
    if not r or not os.path.isdir(r):
        return []
    out = []
    for f in sorted(os.listdir(r)):
        if not f.endswith(".json"):
            continue
        try:
            with open(os.path.join(r, f), encoding="utf-8") as fh:
                out.append(json.load(fh))
        except (OSError, ValueError):
            continue
    return out


def stale_rows_for(repo, session_id=None):
    """Rows for THIS repo that are not this session — an unclean shutdown
    (brief §5). Never silently overwritten: the caller offers /reorient, then
    an abbreviated close, because a row nobody closed means a session nobody
    finished, and that is information."""
    name = os.path.basename(os.path.abspath(repo))
    return [r for r in list_open()
            if r.get("repo") == name and r.get("session_id") != session_id]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("open"); o.add_argument("repo"); o.add_argument("--session-id", required=True)
    c = sub.add_parser("close"); c.add_argument("--session-id", required=True)
    c.add_argument("--state", default=None)
    w = sub.add_parser("sweep"); w.add_argument("--older-than-hours", type=float, required=True)
    w.add_argument("--reason", required=True)
    sub.add_parser("list")
    a = ap.parse_args()
    if a.cmd == "open":
        r = open_session(a.repo, a.session_id)
        print(json.dumps(r, indent=2))
        return 0                                  # never blocks, even on failure
    if a.cmd == "close":
        st = {"summary": a.state} if a.state else None
        print(json.dumps(close_session(a.session_id, st), indent=2))
        return 0
    if a.cmd == "sweep":
        swept = sweep_stale(a.older_than_hours, a.reason)
        print(f"swept {len(swept)} stale record(s)" + ("".join(f"\n  {s}" for s in swept)))
        return 0
    rows = list_open()
    if not rows:
        print("registry: no open sessions"
              + ("" if root() else f"  (none configured — set ${_ENV})"))
        return 0
    for r in rows:
        print(f"  {r.get('repo',''):28} {r.get('session_id','')[:12]:14} "
              f"{r.get('machine',''):12} opened {r.get('opened_at','')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
