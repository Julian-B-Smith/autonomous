#!/usr/bin/env python3
"""gate-change — PreToolUse on Edit|Write|MultiEdit (O0.5): editing a gate file
needs a DECISIONS line containing `GATE-CHANGE:` added in this working tree.

"Gates are never weakened to pass" was review judgment; this makes it a fact a
hook can check. The lift is something the agent can produce itself — write the
rationale — so a block never waits on the human; the human reads the
rationales in bulk at the monthly regulator review (Decision 84; the packet's
asymmetric-friction rule: contracting is free, expanding costs a written why).

Gate files: `./verify`, anything under `.kit/`, `.claude/hooks/`, the
`.claude/settings*.json` files, `thresholds*`, and in the standards repo its
sources (`kit/hooks/`, `kit/vendor/`, `harness/`). Starts in 'observe': logs
would-deny, never blocks, until a signed GATE-CHANGE flips it.
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_GATE = re.compile(r"(^verify$|(^|/)\.kit/|(^|/)\.claude/hooks/|(^|/)\.claude/settings[^/]*\.json$"
                   r"|(^|/)thresholds[^/]*$|^kit/hooks/|^kit/vendor/|^harness/)")


def _token_in_tree(top):
    try:
        diff = subprocess.run(["git", "-C", top, "diff", "HEAD", "--", "DECISIONS.md"],
                              capture_output=True, text=True, timeout=3).stdout
        if any(l.startswith("+") and "GATE-CHANGE:" in l for l in diff.splitlines()):
            return True
        new = subprocess.run(["git", "-C", top, "ls-files", "--others", "--exclude-standard",
                              "DECISIONS.md"], capture_output=True, text=True, timeout=3).stdout
        if new.strip():
            return "GATE-CHANGE:" in open(os.path.join(top, "DECISIONS.md"), encoding="utf-8").read()
    except Exception:
        pass
    return False


def main():
    try:
        import fleet_events as fe
        data = json.load(sys.stdin)
        path = (data.get("tool_input") or {}).get("file_path") or ""
        cwd = data.get("cwd") or os.getcwd()
        top = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=3).stdout.strip()
        if not path or not top:
            return 0
        # realpath both sides: macOS reaches temp and some home paths through
        # symlinks (/var -> /private/var), and a mismatched spelling made the
        # file look outside the repo, so the gate silently skipped it.
        rel = os.path.relpath(os.path.realpath(os.path.join(cwd, path)), os.path.realpath(top))
        if rel.startswith("..") or not _GATE.search(rel.replace(os.sep, "/")):
            return 0
        if _token_in_tree(top):
            fe.log("gate-change-ok", repo=os.path.basename(top), file=rel)
            return 0
        m = fe.mode("gate-change")
        fe.log("would-deny" if m == "observe" else "deny", gate="gate-change",
               repo=os.path.basename(top), file=rel)
        if m == "deny":
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse", "permissionDecision": "deny",
                "permissionDecisionReason":
                    f"{rel} is a gate file. Lift: append a DECISIONS.md line containing "
                    "'GATE-CHANGE: <why this gate changes>' first, then retry."}}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
