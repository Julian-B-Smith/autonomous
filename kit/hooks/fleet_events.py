"""fleet_events — the append-only event log every oversight hook writes, and the
per-gate authority every gate reads (Phase O0.5, Decision 84).

ONE central log, `~/.claude/fleet/events.jsonl`, not one per repo: these hooks
are global and run in every repo, and a per-repo log file would dirty trees that
do not ignore it. The same directory holds the O1 snapshot (Decision 77), for
the same reason: a process launchd starts cannot read `~/Documents` (Decision
42), and nothing here should need it to.

Every function is total and never raises: a hook that throws is a hook that
breaks every session. Lines carry positions and verdicts, never content.
"""
import datetime, json, os

_HERE = os.path.dirname(os.path.abspath(__file__))


def fleet_dir():
    return os.path.expanduser(os.environ.get("KIT_FLEET_DIR", "~/.claude/fleet"))


def log(event, **fields):
    try:
        d = fleet_dir()
        os.makedirs(d, exist_ok=True)
        rec = {"at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "event": event, **fields}
        with open(os.path.join(d, "events.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    except Exception:
        pass


def mode(gate):
    """'observe' unless the versioned modes file says 'deny'. Anything
    unreadable is 'observe': a broken config must never start blocking work."""
    try:
        with open(os.path.join(_HERE, "gate_modes.json"), encoding="utf-8") as fh:
            m = json.load(fh).get(gate, "observe")
        return m if m in ("observe", "deny") else "observe"
    except Exception:
        return "observe"


def expected_kit_hooks(settings_path=None):
    """(event, script path) for every hook in user settings that points into
    this kit — the set the self-test and the config guard compare against."""
    p = settings_path or os.path.expanduser("~/.claude/settings.json")
    try:
        with open(p, encoding="utf-8") as fh:
            s = json.load(fh)
    except Exception:
        return None
    out = []
    for ev, groups in (s.get("hooks") or {}).items():
        for g in groups or []:
            for h in g.get("hooks") or []:
                cmd = h.get("command", "")
                i = cmd.find("autonomous/kit/hooks/")
                if i < 0:
                    continue
                rel = cmd[i:].split('"')[0].split()[0]
                out.append((ev, os.path.expanduser("~/Documents/Claude/" + rel)))
    return out
