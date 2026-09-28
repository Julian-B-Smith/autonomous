#!/usr/bin/env python3
"""hook-selftest — SessionStart (O0.5): every kit hook the user settings name
must exist and be runnable, or the session is told once and the log records it.

WHY: every kit hook is installed as `f=…; [ -x "$f" ] && … || true`, which is
right for an observer (never block a session) and means a moved or deleted
script vanishes without a trace — exit 127 is non-blocking and silent. The
Structural Caution packet named it; our own O0 install had the shape
(briefs/2026-09-26-structural-caution.response.md §1). Report-only: this can
never block, and SessionStart cannot block anyway.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        import fleet_events as fe
        hooks = fe.expected_kit_hooks(os.environ.get("KIT_SETTINGS_PATH"))
        if hooks is None:
            return 0
        missing = [(ev, p) for ev, p in hooks
                   if not os.path.isfile(p) or (p.endswith(".sh") and not os.access(p, os.X_OK))]
        fe.log("hook-count", count=len(hooks), missing=len(missing))
        for ev, p in missing:
            fe.log("hook-missing", hook_event=ev, script=p.replace(os.path.expanduser("~"), "~"))
        if missing:
            names = ", ".join(os.path.basename(p) for _, p in missing)
            print(f"hook self-test: {len(missing)} kit hook(s) configured but not runnable — {names}. "
                  "They are silently doing nothing; restore the file or remove the entry.")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
