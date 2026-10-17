"""steps — the changes a batch plan may name, each ANCHORED, never a guess.

A step takes the worktree path and returns a Step: a `kind` (what it found
and did), the paths it changed, one line for the PR body, and `hold` with a
reason if the repo must not get a PR at all. A step that meets something it
does not recognise changes nothing and says so in the PR: a drifted file is
the resident's to judge (the 2.3.0 rule, kept by every batch since).

Ported from the 2026-10-12 batch script (Decision 95) and extended with the
deny rules of Decision 96.
"""
import hashlib, json, os, shutil, subprocess, sys
from collections import namedtuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_KIT = os.path.join(_HERE, "..")
_ROOT = os.path.join(_KIT, "..")
sys.path.insert(0, _KIT)
import kit_sync  # noqa: E402

Step = namedtuple("Step", "kind paths line hold")
GATE_REL, SET_REL = ".claude/hooks/stop-gate.sh", ".claude/settings.json"
SHIM_SRC = os.path.join(_ROOT, "harness", ".claude", "hooks", "stop-gate.sh")
# sha256 of every project-owned stop gate the template ever shipped. Only a
# byte-identical copy is replaced; anything else is a local variant.
OLD_GATES = {"dd8389032677eca5362db38f724f1fe03be3c0f1dcc2eac226f7da7ce53173b7"}
ENTRY = {"matcher": "", "hooks": [{"type": "command",
         "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-gate.sh"}]}
# Decision 96: merges and repository settings are the human's, by rule and not
# by habit. Kept identical to harness/.claude/settings.json (a test pins it).
DENY = ["Bash(gh pr merge*)", "Bash(gh repo edit*)", "Bash(gh repo delete*)",
        "Bash(gh repo rename*)", "Bash(gh repo archive*)"]


def _ignored(wt, rel):
    return subprocess.run(["git", "check-ignore", "-q", rel], cwd=wt).returncode == 0


def _load_settings(wt):
    p = os.path.join(wt, SET_REL)
    if not os.path.isfile(p):
        return {}, None
    try:
        s = json.load(open(p, encoding="utf-8"))
        if not isinstance(s, dict):
            raise ValueError("not an object")
        return s, None
    except Exception:
        return None, ".claude/settings.json does not parse"


def _save_settings(wt, s):
    os.makedirs(os.path.dirname(os.path.join(wt, SET_REL)), exist_ok=True)
    with open(os.path.join(wt, SET_REL), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(s, indent=2) + "\n")


def kit_sync_step(wt):
    st, _ = kit_sync.check(wt)
    if st.startswith("absent"):
        return Step("never-vendored", [], "", "never vendored (.kit/ absent on the default branch)")
    if st.startswith("current"):
        return Step("current", [], "**Kit files:** already current.", None)
    kit_sync.install(wt)
    return Step("synced", [".kit"],
                f"**Kit files:** `.kit/` synced to {kit_sync.kit_version()} by `kit_sync.py`.", None)


def closing_gate_step(wt):
    gate = os.path.join(wt, GATE_REL)
    if os.path.isfile(gate):
        body = open(gate, "rb").read()
        if b".kit/stop-gate.sh" in body:
            return Step("already-shim", [], "**Closing gate:** already the kit's shim; unchanged.", None)
        if hashlib.sha256(body).hexdigest() not in OLD_GATES:
            return Step("drifted", [], (
                "**Closing gate: NOT changed.** `.claude/hooks/stop-gate.sh` is a local variant, "
                "so it was left alone. This repo reads behind on 2.9.0 until its resident replaces "
                "it with the kit's shim (`harness/.claude/hooks/stop-gate.sh` in autonomous), "
                "keeping whatever the variant was for."), None)
        shutil.copy(SHIM_SRC, gate); os.chmod(gate, 0o755)
        return Step("swapped", [GATE_REL], (
            "**Closing gate:** `.claude/hooks/stop-gate.sh` was byte-identical to the old "
            "template, so it is replaced by the kit's shim, which runs `.kit/stop-gate.sh`."), None)
    if not os.access(os.path.join(wt, "verify"), os.X_OK):
        return Step("no-verify", [], "**Closing gate:** not applicable (no `./verify`).", None)
    if _ignored(wt, SET_REL):
        return Step("ignored", [], (
            "**Closing gate: NOT added.** `.claude/settings.json` is gitignored here, so a "
            "committed gate is not possible. The repo reads behind on 2.9.0 until its resident "
            "decides how to carry it."), None)
    s, err = _load_settings(wt)
    if s is None or not isinstance(s.get("hooks", {}), dict):
        return Step("bad-settings", [], f"**Closing gate: NOT added.** {err or 'settings hooks is not an object'}; left alone.", None)
    hooks = s.setdefault("hooks", {})
    for ev in ("Stop", "SubagentStop"):
        lst = hooks.setdefault(ev, [])
        if not any("stop-gate.sh" in (h.get("command") or "") for g in lst for h in (g.get("hooks") or [])):
            lst.append(json.loads(json.dumps(ENTRY)))
    os.makedirs(os.path.dirname(gate), exist_ok=True)
    shutil.copy(SHIM_SRC, gate); os.chmod(gate, 0o755)
    _save_settings(wt, s)
    return Step("added", [GATE_REL, SET_REL], (
        "**Closing gate, new here:** this repo has a `./verify` and had no closing gate. Adds the "
        "kit's shim at `.claude/hooks/stop-gate.sh` and two entries (`Stop`, `SubagentStop`) in "
        "`.claude/settings.json`. A session here is now blocked once from ending while the last "
        "`./verify` is red."), None)


def deny_rules_step(wt):
    """Add the merge and repo-settings denies. Only where the repo already
    carries a committed `.claude/settings.json`: creating a settings file in a
    repo that has none is a bigger change than a deny list, and is the
    resident's (the closing-gate step creates one only under Decision 92)."""
    if not os.path.isfile(os.path.join(wt, SET_REL)):
        return Step("no-settings", [], "**Deny rules:** not added (no `.claude/settings.json` here).", None)
    if _ignored(wt, SET_REL):
        return Step("ignored", [], "**Deny rules: NOT added.** `.claude/settings.json` is gitignored here.", None)
    s, err = _load_settings(wt)
    if s is None:
        return Step("bad-settings", [], f"**Deny rules: NOT added.** {err}; left alone.", None)
    perms = s.setdefault("permissions", {})
    if not isinstance(perms, dict) or not isinstance(perms.setdefault("deny", []), list):
        return Step("bad-settings", [], "**Deny rules: NOT added.** `permissions.deny` is not a list; left alone.", None)
    missing = [d for d in DENY if d not in perms["deny"]]
    if not missing:
        return Step("present", [], "**Deny rules:** already present.", None)
    perms["deny"].extend(missing)
    _save_settings(wt, s)
    return Step("added", [SET_REL], (
        "**Deny rules:** agents may no longer run `gh pr merge` or `gh repo edit/delete/rename/"
        "archive` here (autonomous Decision 96: merges and repository settings are the human's)."), None)


STEPS = {"kit_sync": kit_sync_step, "closing_gate": closing_gate_step, "deny_rules": deny_rules_step}
