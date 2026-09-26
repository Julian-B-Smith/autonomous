"""session_facts — what a session hook records about the session. Shared by
session-open.py and session-close.py so the two can never disagree on how a
fact is computed.

Every function is bounded (git with a timeout) and total (returns a value, never
raises): these run inside SessionStart/SessionEnd hooks, and a hook that raises
or hangs is a hook that slows or breaks every session in every repo. Values are
positions and hashes, never content — the registry's rule (registry.py).
"""
import glob, hashlib, json, os, subprocess, sys

AUT = os.path.expanduser(os.environ.get("AUTONOMOUS_HOME", "~/Documents/Claude/autonomous"))
HOME = os.path.expanduser("~")


def read_hook_input():
    """The JSON Claude Code writes to a hook's stdin, or {} — never raises."""
    try:
        return json.load(sys.stdin) or {}
    except Exception:
        return {}


def _git(cwd, *args):
    try:
        p = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=3)
        return p.stdout.strip() if p.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def repo_top(cwd):
    return _git(cwd, "rev-parse", "--show-toplevel") or cwd


def tilde(path):
    """`~`-relative, so no record carries a machine-absolute path (doctrine:
    never commit machine identity — the registry may one day be a shared repo)."""
    path = os.path.abspath(path)
    return "~" + path[len(HOME):] if path == HOME or path.startswith(HOME + os.sep) else path


def _sha(data):
    return hashlib.sha256(data).hexdigest()[:12]


def _file_sha(path):
    try:
        with open(path, "rb") as fh:
            return _sha(fh.read())
    except OSError:
        return ""


def open_facts(top):
    """The system a session was built against. The oversight engine compares
    these with the system as it is NOW to say what drifted."""
    cmds = sorted(glob.glob(os.path.join(HOME, ".claude", "commands", "*.md")))
    blob = b"".join(open(c, "rb").read() for c in cmds if os.path.isfile(c))
    try:
        with open(os.path.join(AUT, "kit", "VERSION"), encoding="utf-8") as fh:
            kit = fh.read().strip()
    except OSError:
        kit = ""
    return {"path": tilde(top),
            "head_at_open": _git(top, "rev-parse", "--short", "HEAD"),
            "branch_at_open": _git(top, "branch", "--show-current"),
            "doctrine_sha": _file_sha(os.path.join(AUT, "doctrine", "DOCTRINE.md")),
            "kit_version": kit,
            "commands_sha": _sha(blob) if cmds else ""}


def close_state(top, reason=""):
    """How the tree was left, recorded without judgment. `summary` is the one
    line a human reads; the counts are what the engine checks."""
    porcelain = _git(top, "status", "--porcelain")
    dirty = len([l for l in porcelain.splitlines() if l.strip()])
    branch = _git(top, "branch", "--show-current")
    upstream = _git(top, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    unpushed = None
    if upstream:
        n = _git(top, "rev-list", "--count", "@{u}..HEAD")
        unpushed = int(n) if n.isdigit() else None
    bits = []
    if dirty:
        bits.append(f"dirty: {dirty} file(s)")
    if unpushed:
        bits.append(f"unpushed: {unpushed} commit(s)")
    if branch and not upstream:
        bits.append(f"branch {branch} has no upstream")
    return {"summary": "; ".join(bits) or "clean",
            "dirty": dirty, "unpushed": unpushed, "branch": branch,
            "upstream": bool(upstream), "head": _git(top, "rev-parse", "--short", "HEAD"),
            "end_reason": reason}
