#!/usr/bin/env python3
"""session-close — SessionEnd hook (O0, Decision 77): close this session's
record with how the tree was left. Never commits, never pushes, never judges:
nobody is present at exit to review anything, so the hook only RECORDS —
dirty files, unpushed commits, a branch with no upstream — for the next
session and the dashboard to act on.

A crash or force-quit never fires this hook; those records are closed later by
`registry.py sweep`, marked unclean. That gap is stated, not hidden.

FAIL-OPEN: every path exits 0, silently.
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
        registry.close_session(sid, sf.close_state(top, data.get("reason", "")))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
