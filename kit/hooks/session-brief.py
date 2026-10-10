#!/usr/bin/env python3
"""session-brief — SessionStart hook. Tells THIS repo's session what THIS repo
owes, and nothing else.

WHY SCOPED (2026-08-17, Decision 54): the previous version read the fleet-wide
STATUS.md and reported its counts into every session on the machine, because
the hook is installed globally. Agents in several unrelated projects all warned
the human about one uncommitted brief sitting in autonomous's mailbox — a repo
none of them had standing to touch. That is a requisite-variety failure: an
attenuator must deliver a signal its recipient can ACT on, and fleet state
delivered to a leaf project is pure noise that trains the reader to skip the
channel.

Rule, and it is the same rule the protocol states for humans and agents alike:
**a repo acts only on exchanges in its own mailbox, plus responses addressed to
it elsewhere.** Everything else is somebody else's territory.

Fleet-wide roll-up appears ONLY in the standards repo, which is the one place
it is actionable.

Fail-open: an observer, not a gate.
"""
import datetime
import json
import os
import subprocess
import sys

HOME = os.path.expanduser("~")
AUT = os.environ.get("AUTONOMOUS_HOME", os.path.join(HOME, "Documents/Claude/autonomous"))
sys.path.insert(0, os.path.join(AUT, "governor"))
sys.path.insert(0, os.path.join(AUT, "kit", "sweep"))


def out(msg):
    if msg:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SessionStart", "additionalContext": msg}}))
    sys.exit(0)


def main():
    try:
        root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        out(None)
    if not root:
        out(None)                      # not in a repo: nothing scoped to say
    name = os.path.basename(root)

    try:
        import ball_scan
    except Exception:
        out(None)

    today = datetime.date.today()
    bits = []

    # 0. Retrofit notices (autonomous only — the mailbox is ours; runs BEFORE
    #    the ball scan so a notice judged here is not also reported as owed). A repo that
    #     finished /retrofit filed a notice asking to be verified NOW; verify
    #     it here by re-reading its tree, and say what the verdict was. The
    #     notice's claim is never repeated as fact — only the verdict is.
    if os.path.realpath(root) == os.path.realpath(AUT):
        try:
            sys.path.insert(0, os.path.join(AUT, "governor"))
            import retrofit_verify
            with open(os.path.join(AUT, "registry.json"), encoding="utf-8") as fh:
                judged = retrofit_verify.verify_all(json.load(fh))
            for r in judged:
                bits.append(f"retrofit {r['sender']}→{r['claimed']}: {r['verdict'].upper()}"
                            + ("" if r["verdict"] == "verified" else f" ({r['note']})"))
        except Exception:
            pass

    # 1. What THIS repo owes (its own mailbox).
    try:
        mine = ball_scan.scan_repo(root, name, today)
    except Exception:
        mine = []
    overdue = [t for t in mine if t["days_overdue"]]
    held = [t for t in mine if t["ours"] and not t["days_overdue"]]
    if overdue:
        bits.append("OVERDUE: " + "; ".join(
            f"{t['id']} ({t['days_overdue']}d past {t['respond_by']})" for t in overdue))
    if held:
        bits.append("ball on us: " + ", ".join(t["id"] for t in held))

    # 1b. What this repo's last GREEN verify did not do (kit 2.9.0). A skipped
    #     gate or an empty corpus leaves the same green record as a full run,
    #     and a reader nobody invokes makes nothing visible (review, 2026-10-10),
    #     so the brief says it. Silent when every wrapped gate ran.
    try:
        sys.path.insert(0, os.path.join(AUT, "governor"))
        import receipts
        with open(os.path.join(root, ".harness", "last-verify.json"), encoding="utf-8") as fh:
            short = receipts.findings(json.load(fh))
        if short:
            bits.append("last green verify: " + "; ".join(short[:4])
                        + (f" (+{len(short) - 4} more)" if len(short) > 4 else ""))
    except Exception:
        pass

    # 2. Mailbox writes a visitor left here that a RESIDENT must commit.
    try:
        unc = ball_scan.untracked_mailbox_files(root)
    except Exception:
        unc = []
    if unc:
        bits.append(f"{len(unc)} uncommitted mailbox write(s) here: "
                    + ", ".join(os.path.basename(f) for f in unc))

    # 3. Responses to OUR briefs, sitting in other repos' trees. The delivery
    #    gap (Decision 53): without this a repo cannot tell an answered brief
    #    from an ignored one. Roster read is best-effort — never block on it.
    try:
        import sweep
        with open(os.path.join(AUT, "registry.json"), encoding="utf-8") as fh:
            reg = json.load(fh)
        paths = [p["path"] for p in sweep.resolve(reg)]
        awaiting = ball_scan.responses_awaiting(name, paths, today)
        if awaiting:
            bits.append("answered elsewhere, unread by us: " + ", ".join(
                f"{a['id']} in {a['in_repo']}" for a in awaiting))
    except Exception:
        pass

    # 4. Installed slash commands vs the kit. Commands are USER-level
    #    (~/.claude/commands/), copied from kit/commands/ by hand (INSTALL-GLOBAL
    #    §3), so a kit change leaves the installed copy stale until someone
    #    re-copies — the same silent-currency gap K0 closed for repos, one level
    #    up. Reported in EVERY session because it is machine-wide, not
    #    repo-scoped, and it is the human's install to fix.
    try:
        import filecmp
        kit_cmds = os.path.join(AUT, "kit", "commands")
        inst = os.path.join(HOME, ".claude", "commands")
        stale, missing = [], []
        for f in sorted(os.listdir(kit_cmds)):
            if not f.endswith(".md"):
                continue
            k, i = os.path.join(kit_cmds, f), os.path.join(inst, f)
            if not os.path.isfile(i):
                missing.append(f[:-3])
            elif not filecmp.cmp(k, i, shallow=False):
                stale.append(f[:-3])
        if stale or missing:
            parts = []
            if stale:
                parts.append("stale: /" + ", /".join(stale))
            if missing:
                parts.append("not installed: /" + ", /".join(missing))
            bits.append("commands " + "; ".join(parts)
                        + " — cp ~/Documents/Claude/autonomous/kit/commands/*.md ~/.claude/commands/")
    except Exception:
        pass

    # 4. Fleet roll-up: ONLY in the standards repo.
    if os.path.realpath(root) == os.path.realpath(AUT):
        st = os.path.join(AUT, "governor", "STATUS.md")
        if os.path.isfile(st):
            age_h = int((datetime.datetime.now().timestamp()
                         - os.path.getmtime(st)) // 3600)
            try:
                with open(st, encoding="utf-8") as fh:
                    text = fh.read()
            except OSError:
                text = ""
            fleet = []
            n_over = text.count("d overdue**")
            if n_over:
                fleet.append(f"{n_over} overdue fleet-wide")
            for tag in ("S4-UNMERGED", "S4-STALE", "OPEN-PR"):
                if f"`{tag}`" in text:
                    fleet.append(tag)
            if age_h > 48:
                fleet.append(f"sweep cache {age_h}h old")
            if fleet:
                bits.append("fleet: " + ", ".join(fleet))

    if not bits:
        out(None)
    out(f"[{name}] " + " · ".join(bits)
        + " — scoped to this repo; other repos' obligations are theirs.")


if __name__ == "__main__":
    main()
