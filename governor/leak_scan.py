#!/usr/bin/env python3
"""leak_scan — deterministic fleet privacy audit (the watchdog's first check).

Greps every roster repo's TRACKED files (git grep at HEAD — respects
.gitignore) for references that leak the local environment, and flags the one
thing a per-repo check can't see: a PRIVATE repo's name appearing in a PUBLIC
repo. Deterministic (no model calls); propose-only (reports, never edits).

Severity:
  HIGH  absolute home paths (/Users/<user>/...) or the literal local username
        in tracked files — bakes machine identity into the repo.
  HIGH  a private repo's name found in a public repo's tracked files
        (cross-repo exposure; needs --visibility / gh).
  INFO  home-relative structural refs (~/Documents/..., Documents/Claude/...) —
        intended in replication docs; reported low so real leaks stand out.

Usage:
  leak_scan.py --registry ../registry.json [--visibility] [--json]
Exit 0 always (report tool); a CI GATE variant would exit nonzero on HIGH.
"""

import argparse
import json
import os
import re
import subprocess
import sys

# reuse the sweep primitive for roster enumeration + visibility
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "kit", "sweep"))
import sweep  # noqa: E402

# USERNAME is the Windows spelling; USER is POSIX. Both, or a Windows run
# falls back to the homedir basename and can miss the username entirely.
USER = (
    os.environ.get("USER")
    or os.environ.get("USERNAME")
    or os.path.basename(os.path.expanduser("~"))
)


def username_pattern(user):
    """POSIX-ERE pattern for the bare local username, anchored on both sides.

    Unanchored, the pattern is the username as a substring, and a detector
    keyed on the CURRENT machine's identity is a different detector on every
    machine: the Windows box's username is a substring of "transport" and
    "support", so the same 54 trees that read clean on the Mac read 20 HIGH
    there — every one a false positive, and a channel that cries wolf is a
    channel nobody reads. `git grep -E` has no `` (L0002), so the boundary
    is spelled out: start-or-non-word before, non-word-or-end after.
    """
    return r"(^|[^A-Za-z0-9_])" + re.escape(user) + r"([^A-Za-z0-9_]|$)"

HIGH_PATTERNS = [
    # POSIX ERE only — `git grep -E` does NOT support \s / \d (a \s here
    # silently matched nothing, so absolute-path detection was dead: the
    # 2026-07-13 first run caught leaks by username alone. Keep it ERE-safe.)
    (r"/(Users|home)/[^/]+/", "absolute home path"),
    # Windows identity path. `\\+` matches raw `C:\Users\` AND escaped
    # `C:\\Users\\` (how it lands in JSON/configs); a one-backslash pattern
    # misses the escaped form silently.
    (r"[A-Za-z]:\\+Users\\+[^\\]", "windows absolute home path"),
    (username_pattern(USER), "local username"),
]
INFO_PATTERNS = [
    (r"~/Documents", "home-relative structural ref"),
    (r"Documents/Claude", "structural ref"),
]


# `/Users/<user>/…`, `/home/$USER/…`, `/Users/%s/`, `/Users/{name}/…`,
# `/Users/@…` in prose/code are docs ABOUT the pattern, not leaks. Filter them
# or the scanner cries wolf — a noisy scanner is an ignored scanner.
# MUST match the bash leak_gate's placeholder class `[<$@{%]` in every ./verify
# (two detectors — bash gate, python scanner — that must stay consistent; when
# one changes, change both. The gate once had %/@ that this lacked, so the
# monitor false-flagged repos the gate passed.)
_PLACEHOLDER = re.compile(r"/(Users|home)/[<${@%]|[A-Za-z]:\\+Users\\+[<${@%]")


def _is_placeholder(line):
    return bool(_PLACEHOLDER.search(line))


def _excludes(path):
    """Pathspec excludes: the scanner itself, the allowlist file, and every
    entry in the repo's .leakcheck-allow (security docs that legitimately hold
    the patterns). Same allowlist the ./verify leak_gate honors."""
    ex = [":(exclude)*leak_scan.py", ":(exclude).leakcheck-allow"]
    allow = os.path.join(path, ".leakcheck-allow")
    if os.path.isfile(allow):
        for line in open(allow, encoding="utf-8", errors="ignore"):
            line = line.split("#", 1)[0].strip()
            if line:
                ex.append(":(exclude)" + line)
    return ex


def _git_grep(path, pattern, excludes):
    """Lines in tracked files matching pattern (POSIX ERE). [] if none."""
    try:
        out = subprocess.run(
            ["git", "-C", path, "grep", "-nIE", pattern, "--", "."] + excludes,
            capture_output=True, text=True,
        )
        return out.stdout.splitlines() if out.returncode == 0 else []
    except FileNotFoundError:
        return []


def scan_repo(path, private_names=None, public=None):
    findings = []
    if not os.path.isdir(os.path.join(path, ".git")):
        return findings
    excludes = _excludes(path)
    for pat, label in HIGH_PATTERNS:
        for line in _git_grep(path, pat, excludes):
            if label == "absolute home path" and _is_placeholder(line):
                continue  # docs about the pattern, not a leak
            findings.append(("HIGH", label, line))
    for pat, label in INFO_PATTERNS:
        for line in _git_grep(path, pat, excludes):
            findings.append(("INFO", label, line))
    # cross-repo: private names inside a PUBLIC repo
    if public and private_names:
        for name in private_names:
            base = name.split("/")[-1]
            if len(base) < 4:      # skip short names -> false positives
                continue
            for line in _git_grep(path, r"\b" + re.escape(base) + r"\b", excludes):
                findings.append(("HIGH", f"private-name '{base}' in public repo", line))
    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(prog="leak_scan")
    ap.add_argument("--registry", required=True)
    ap.add_argument("--visibility", action="store_true",
                    help="use gh to fetch public/private (enables cross-repo name check)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    registry = json.load(open(args.registry))
    projects = sweep.resolve(registry)

    vis = {}
    private_names = []
    if args.visibility:
        for p in projects:
            v = sweep.repo_visibility(sweep.derive_status(p["path"]).get("remote"))
            vis[p["name"]] = v
            if v and v != "PUBLIC":
                private_names.append(p["name"])

    report = []
    for p in projects:
        is_public = vis.get(p["name"]) == "PUBLIC"
        findings = scan_repo(p["path"], private_names=private_names, public=is_public)
        if findings:
            report.append({"name": p["name"], "visibility": vis.get(p["name"]),
                           "findings": findings})

    if args.json:
        json.dump(report, sys.stdout, indent=2); sys.stdout.write("\n")
        return 0

    high = sum(1 for r in report for f in r["findings"] if f[0] == "HIGH")
    info = sum(1 for r in report for f in r["findings"] if f[0] == "INFO")
    print(f"leak_scan: {len(report)} repos with findings — {high} HIGH, {info} INFO\n")
    for r in report:
        hi = [f for f in r["findings"] if f[0] == "HIGH"]
        if not hi and not args.json:
            continue  # in summary view, surface repos with HIGH first
        vtag = f" [{r['visibility']}]" if r.get("visibility") else ""
        print(f"── {r['name']}{vtag}")
        for sev, label, line in hi[:8]:
            print(f"   HIGH  {label}: {line[:100]}")
        if len(hi) > 8:
            print(f"   … +{len(hi)-8} more HIGH")
    if not high:
        print("No HIGH-severity leaks in tracked files. ✓ "
              "(INFO-level structural refs are intended replication docs.)")
    print("\nNote: scans HEAD (tracked files). Git HISTORY may still hold "
          "purged blobs — a deeper history scan is a separate, one-time check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
