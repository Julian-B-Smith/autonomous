#!/usr/bin/env python3
"""session-open — SessionStart hook (O0, Decision 77): open or refresh this
session's registry record, with no command to remember.

Keyed by Claude Code's own `session_id`, so a resumed or compacted session
refreshes its record instead of opening a second one. Prints exactly one line
into the session's context — its own record id — so `/wakeup` and `/breakdown`
can tell their own row from a stale one; prints nothing when no registry is
configured.

FAIL-OPEN: every path exits 0. A bookkeeping hook that can stop a session is
worse than no bookkeeping (registry.py, brief §5).
"""
import os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "..", "session"))


def main():
    try:
        import session_facts as sf
        import registry
        data = sf.read_hook_input()
        sid = data.get("session_id")
        if not sid or not registry.root():
            return 0
        top = sf.repo_top(data.get("cwd") or os.getcwd())
        facts = sf.open_facts(top)
        facts["start_source"] = data.get("source", "")
        r = registry.open_session(top, sid, facts=facts)
        if r.get("ok"):
            print(f"session record: {sid} (opened {r['row']['opened_at']}; "
                  "closed automatically by the SessionEnd hook)")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
