#!/usr/bin/env python3
"""config-guard — ConfigChange (O0.5): a settings change that switches hooks off
or drops a kit hook is logged, and in 'deny' mode blocked.

The nearest thing a solo operator has to a gate on the gates: `disableAllHooks`
or a deleted entry would otherwise turn every guard off in one edit, and nothing
would say so. ConfigChange can block (exit 2) except for policy settings
(hooks reference, verified 2026-09-26). Starts in 'observe' (Decision 84).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        import fleet_events as fe
        data = json.load(sys.stdin)
        src, path = data.get("source", ""), data.get("file_path") or ""
        if src not in ("user_settings", "project_settings", "local_settings"):
            return 0
        reasons = []
        try:
            with open(path, encoding="utf-8") as fh:
                s = json.load(fh)
            if s.get("disableAllHooks"):
                reasons.append("disableAllHooks is true")
        except Exception:
            s = None
        if src == "user_settings" and path:
            now = fe.expected_kit_hooks(path) or []
            last_p = os.path.join(fe.fleet_dir(), "kit-hook-count")
            try:
                with open(last_p) as fh:
                    last = int(fh.read().strip() or 0)
            except Exception:
                last = None
            if last is not None and len(now) < last:
                reasons.append(f"kit hooks dropped from {last} to {len(now)}")
            if not reasons:
                os.makedirs(fe.fleet_dir(), exist_ok=True)
                with open(last_p, "w") as fh:
                    fh.write(str(len(now)))
        fe.log("config-change", source=src, file=os.path.basename(path), flags=reasons)
        if reasons:
            m = fe.mode("config-guard")
            fe.log("would-deny" if m == "observe" else "deny", gate="config-guard",
                   source=src, reasons=reasons)
            if m == "deny":
                print("config-guard: " + "; ".join(reasons) + ". Lift: record a DECISIONS "
                      "line containing GATE-CHANGE: <why> in the standards repo first.",
                      file=sys.stderr)
                return 2
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
