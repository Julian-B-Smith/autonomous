#!/usr/bin/env python3
"""currency — the deterministic half of `/retrofit`: where is this repo
against the kit, and exactly which entries does it need?

Phase K1 (Decision 51). `/retrofit` used to re-derive a repo's harness state
every run and then re-scaffold. Now it MIGRATES: read the repo's declared
`kit_version`, diff it against `kit/CHANGELOG.md`, and emit the ordered list
of entries the repo is behind — each with a presence check the retrofit can
act on. AI does the parts that need judgement (inferring survey answers,
mapping a foreign kit's substance into standard slots); THIS does the parts
that must never depend on judgement (what version, what delta, what present).

Absence is never current: a repo with no `kit_version` is `pre-2.0.0` and
gets every entry. Idempotence is the gate — a repo AT the kit version gets an
empty delta, so re-running the retrofit is a no-op by construction.

Usage:
  currency.py <repo> [--kit <autonomous>] [--json]
Exit 0 always for a readable repo (report tool). Exit 2 = repo unreadable.
"""

import argparse
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_VERSION_RE = re.compile(r"^## (\d+\.\d+\.\d+) — (\d{4}-\d{2}-\d{2}) — (.+)$", re.M)


def parse_version(v):
    """'2.1.0' -> (2, 1, 0). 'pre-X' sorts below everything."""
    if not v or v.startswith("pre-"):
        return (-1, 0, 0)
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return (-1, 0, 0)


def kit_version(kit_dir):
    with open(os.path.join(kit_dir, "VERSION"), encoding="utf-8") as fh:
        return fh.read().strip()


def changelog_entries(kit_dir):
    """[(version, date, title, body)] in file order (oldest first)."""
    with open(os.path.join(kit_dir, "CHANGELOG.md"), encoding="utf-8") as fh:
        text = fh.read()
    heads = list(_VERSION_RE.finditer(text))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out.append((m.group(1), m.group(2), m.group(3).strip(),
                    text[m.end():end].strip()))
    return out


# What each CHANGELOG version REQUIRES to be present in a repo for it to
# declare that version. Kept here rather than parsed out of the prose, so the
# check is a table an agent cannot misread — the prose in CHANGELOG.md is the
# explanation; this is the gate. Add a row when you add a CHANGELOG entry.
# Patch versions that change the TOOL and ask nothing new of a repo are listed
# with an EMPTY requirement list. currency.py treats an empty-requirement entry
# as satisfied by every repo, so a tool-only bump never reports the fleet
# behind by something it cannot act on. Repos still get the declaration bumped
# on their next retrofit, which is the right time.
TOOL_ONLY = {"2.0.1", "2.2.1", "2.2.2", "2.2.3", "2.4.1", "2.5.1"}  # 2.3.0/2.4.0 are NOT

REQUIREMENTS = {
    # 2.6.0 asks nothing of a repo: it changed how the CHECKER decides, not
    # what a repo must have. Requirements-free entries never appear in `behind`.
    "2.6.0": [],
    # 2.5.0: .gitattributes must be TRACKED, not merely present. Tonality found
    # their own repo declaring 2.4.1 with an untracked one — the check read [x]
    # while the LF policy could not reach a clone or CI, so the Windows-CRLF
    # hazard it exists to close was fully live. Shipped as a version with a
    # retrofit action rather than folded into 2.0.0: a tightening that flips
    # repos to BEHIND is a migration, and 2.2.0 set that precedent.
    "2.5.1": [],   # tool-only — kit_sync gains `untracked` (terrane)
    "2.5.0": [(".gitattributes is TRACKED", ".gitattributes", "tracked")],
    # 2.4.0: kit-owned gate code is VENDORED into .kit/ and checksum-pinned,
    # not copied. Checked by hash against the kit, which is also how the repo
    # proves it — no probe, no plant, no subprocess.
    "2.4.1": [],   # tool-only — receipts name the path they wrote; filer notes
    "2.4.0": [("kit gates vendored (.kit/ matches canonical)", None, "vendored")],
    # 2.2.1: tool-only — /retrofit Step 6 (completion notice) + retrofit_verify.
    # Asks nothing of the repo tree; a 2.2.0 repo is CURRENT against it.
    "2.2.1": [],
    "2.2.2": [],   # tool-only — probe restores .harness/ (L0006)
    "2.2.3": [],   # tool-only — currency renders ~/ ; Step 6 notices are public
    # 2.3.0: the gate must hide OTHER sessions' probe plants. Behavioural and
    # checkable: with a plant present and no KIT_LEAK_PLANT, the gate must NOT
    # fire. A repo whose gate still reds on a foreign plant is correctly BEHIND.
    "2.3.0": [("gate ignores foreign probe plants", None, "plant-invisible")],
    # 2.2.0: the leak gate must FIRE, not merely exist. Behavioural, per
    # spectral-morph-001. A repo at 2.1.0 with a POSIX-only gate is correctly
    # BEHIND this — that is the migration, not a silent tightening.
    "2.2.0": [
        ("leak_gate fires on POSIX identity", "verify", "gate-fires:posix"),
        ("leak_gate fires on Windows identity", "verify", "gate-fires:windows"),
    ],
    # 2.1.0 asks for a CLAUDE.md section; presence of the FILE is already
    # required by 2.0.0, and gating on the section's prose would reward the
    # words over the understanding (see CHANGELOG). So: no new mechanical
    # check — the retrofit still applies the entry, and a repo below 2.1.0
    # reads as behind until it does.
    "2.1.0": [],
    "2.0.1": [],
    "2.0.0": [
        # (label, relative path or callable-name, kind)
        ("CLAUDE.md", "CLAUDE.md", "file"),
        ("ROADMAP.md", "ROADMAP.md", "file"),
        ("DECISIONS.md", "DECISIONS.md", "file"),
        ("project.manifest.json", "project.manifest.json", "file"),
        ("INDEX.md", "INDEX.md", "file"),
        ("LIBRARY.md", "LIBRARY.md", "file"),
        ("traces/", "traces", "dir"),
        ("./verify", "verify", "exec"),
        ("verify wires leak_gate", "verify", "contains:leak_gate"),
        ("CI workflow", ".github/workflows", "dir-nonempty"),
        (".gitattributes (LF)", ".gitattributes", "contains:eol=lf"),
    ],
}


_GATE_CACHE = {}


def _gate_fires_cached(repo, plant_lines, key):
    """Behavioural checks run the repo's whole ./verify — seconds each, and the
    fleet checklist asks twice per repo across 46 repos. Cache on the repo's
    verify file content + git HEAD: if neither changed, the gate's behaviour
    did not either. A cache miss re-runs; a hit is free. Kept in-process only
    (one checklist run), so it can never go stale across runs.
    """
    import hashlib
    try:
        with open(os.path.join(repo, "verify"), "rb") as fh:
            vsum = hashlib.sha1(fh.read()).hexdigest()
    except OSError:
        vsum = "none"
    ck = (os.path.abspath(repo), vsum, key)
    if ck not in _GATE_CACHE:
        _GATE_CACHE[ck] = _gate_fires(repo, plant_lines)
    return _GATE_CACHE[ck]


def _tilde(path):
    """`<home>/x` -> `~/x`. Never commit machine identity (doctrine)."""
    home = os.path.expanduser("~")
    return "~" + path[len(home):] if path.startswith(home + os.sep) else path


def _sweep_stale_plants(repo, max_age=600):
    """Remove ORPHANED probe plants before planting a new one.

    A plant is written into a foreign working tree and removed in a finally
    block — but a `finally` does not run if the interpreter is killed, and Place
    hit exactly that (2026-08-18): a timed-out run left `.kit-currency-plant-*`
    behind, untracked and unignored, one `git add -A` from committing identity
    paths that leak_gate now ignores BY DESIGN. Their project-local
    plant_not_tracked check caught it; this closes it at the source so no repo
    has to carry a guard for our litter.

    Age, not pid, decides: pids are reused, and a live sibling probe's plant
    must survive. Probes time out at 180s, so anything older than max_age
    cannot belong to a running one.
    """
    import glob as _glob, time as _time
    now = _time.time()
    for f in _glob.glob(os.path.join(repo, ".kit-currency-plant-*")):
        try:
            if now - os.path.getmtime(f) > max_age:
                os.remove(f)
        except OSError:
            pass


def _harness_snapshot(repo):
    """Snapshot what the repo's OWN ./verify writes as a side effect, so a probe
    can put it back. juce-rag (2026-08-18): the gate-fires probe runs the
    target's `./verify fast`, and a CORRECTLY firing gate exits 1 — so the
    target's `record()` wrote `{"exit":1}` into `.harness/last-verify.json`
    and deleted `.harness/dirty`. The plant was removed; the record was not
    restored; the repo's Stop hook then blocked on a red that was actually
    this check PASSING. "Left untouched" must mean `.harness/` too."""
    hd = os.path.join(repo, ".harness")
    snap = {}
    for f in ("last-verify.json", "dirty"):
        fp = os.path.join(hd, f)
        try:
            with open(fp, "rb") as fh:
                snap[f] = fh.read()
        except OSError:
            snap[f] = None            # absent — restore means "absent again"
    return snap


def _harness_restore(repo, snap):
    hd = os.path.join(repo, ".harness")
    for f, data in snap.items():
        fp = os.path.join(hd, f)
        try:
            if data is None:
                if os.path.exists(fp):
                    os.remove(fp)
            else:
                os.makedirs(hd, exist_ok=True)
                with open(fp, "wb") as fh:
                    fh.write(data)
        except OSError:
            pass


def _vendored_current(repo):
    """True when the repo's `.kit/` matches the kit's current bytes exactly.

    This is the whole point of vendoring: the question "does this repo carry
    the real gate" becomes a hash comparison instead of a behavioural probe.
    Microseconds, no subprocess, no plant written into someone else's working
    tree, and therefore none of the failure family the probe created (record
    clobber, plant collision, ignore-blinding). A copy can lie; a hash cannot.
    """
    try:
        import kit_sync
    except ImportError:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import kit_sync
    try:
        # version-stale counts: the vendored BYTES are canonical, which is the
        # only thing a gate question can turn on. The version line is a label.
        return kit_sync.check(repo)[0] in ("current", "version-stale")
    except Exception:
        return False



def verify_cmd(target="fast"):
    """argv that runs a repo's own ./verify on every platform.

    Windows CreateProcess cannot exec a `#!/usr/bin/env bash` script directly;
    it raises OSError, and every probe here catches OSError as "the gate did
    not fire". So on the Windows machine the gate-fires probe was inert and
    reported nothing — the silent shape L0002 warns about, one level up: not a
    dead pattern but a dead process. Route through bash there (Git Bash is a
    stated requirement, INSTALL-GLOBAL §6b); POSIX runs the script as-is.
    """
    cmd = ["./verify", target]
    return ["bash"] + cmd if os.name == "nt" else cmd

def _gate_report(repo):
    """ONE ./verify run per repo, planting BOTH identity families in one file
    on separate lines, and reading which LINE the gate named. Halves the cost
    of the fleet checklist versus one run per family, and the result is more
    informative: {"posix": bool, "windows": bool}. Cached on verify content.
    """
    import hashlib, subprocess
    # FAST PATH: a vendored repo's gate is byte-identical to canonical by
    # construction, so every behavioural property canonical has, it has. Probing
    # it would only re-derive what the checksum already settled — and probing is
    # what writes files into a foreign working tree.
    if _vendored_current(repo):
        return {"posix": True, "windows": True, "plant_invisible": True}
    if os.environ.get("KIT_CURRENCY_NESTED"):
        return {"posix": False, "windows": False, "plant_invisible": False}
    v = os.path.join(repo, "verify")
    if not (os.path.isfile(v) and os.access(v, os.X_OK)):
        return {"posix": False, "windows": False, "plant_invisible": False}
    try:
        with open(v, "rb") as fh:
            vsum = hashlib.sha1(fh.read()).hexdigest()
    except OSError:
        vsum = "none"
    ck = (os.path.abspath(repo), vsum, "report")
    if ck in _GATE_CACHE:
        return _GATE_CACHE[ck]
    name = f".kit-currency-plant-{os.getpid()}.md"
    path = os.path.join(repo, name)
    result = {"posix": False, "windows": False, "plant_invisible": False}
    _sweep_stale_plants(repo)
    snap = _harness_snapshot(repo)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f"posix {_POSIX_PLANT}\nwindows {_WIN_PLANT}\n")
        # KIT_LEAK_PLANT: kit >=2.3.0 gates hide plant files from every run
        # EXCEPT the one that owns them, so our probe cannot red a concurrent
        # session's verify on this tree (mind-lathe, 2026-08-18). Older gates
        # ignore the variable and stay collision-prone — that is the retrofit.
        env = dict(os.environ, KIT_CURRENCY_NESTED="1", KIT_LEAK_PLANT=name)
        r = subprocess.run(verify_cmd(), cwd=repo, capture_output=True,
                           text=True, timeout=120, env=env)
        out = r.stderr + r.stdout
        # Second run, SAME plant, WITHOUT the ownership marker: this is what a
        # concurrent session's verify sees while we probe. It must NOT name the
        # plant — otherwise our probe reds their run on a file that vanishes
        # (mind-lathe, 2026-08-18). Costs one extra verify per repo, cached
        # with the rest; the alternative is grepping the gate's source, which
        # is the presence check 2.2.0 exists to reject.
        env2 = dict(os.environ, KIT_CURRENCY_NESTED="1")
        env2.pop("KIT_LEAK_PLANT", None)
        r2 = subprocess.run(verify_cmd(), cwd=repo, capture_output=True,
                            text=True, timeout=120, env=env2)
        result = {"posix": f"{name}:1:" in out, "windows": f"{name}:2:" in out,
                  "plant_invisible": name not in (r2.stderr + r2.stdout)}
    except (OSError, subprocess.TimeoutExpired):
        pass
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
        _harness_restore(repo, snap)
    _GATE_CACHE[ck] = result
    return result


def _gate_fires(repo, plant_lines):
    """Does the repo's OWN ./verify leak_gate go red on planted known-bad lines?

    spectral-morph-001 ask 2: `contains:leak_gate` was a presence check on the
    gate's NAME. A repo with a POSIX-only pattern (harness/verify shipped that
    for a month) read as compliant while blind to the Windows form. Kit README
    says every gate asserts the EFFECTIVE state; the currency checker was the
    exception. This plants each identity family in a scratch file inside the
    repo, runs `./verify fast`, and requires the gate to name the file. The
    plant is created and removed inside one call; the repo is left untouched —
    working tree AND `.harness/` (see _harness_snapshot).
    """
    import subprocess
    # RECURSION GUARD. autonomous's own ./verify runs `currency.py .`, and this
    # check runs `./verify fast` — so without a guard, checking autonomous is a
    # fork bomb: verify → currency → verify → currency … (it happened; ~100
    # nested plants before it was killed). An env var marks "we are already
    # inside a currency behavioural check"; a nested invocation must return the
    # honest answer for the outer one, and the honest answer for "does the gate
    # fire" cannot be established from inside the gate. So a nested call reports
    # NOT-fired, which makes the outer check fail loud rather than loop silent —
    # and verify's own self-check reads currency's --json, which the outer call
    # still produces correctly because it is not nested.
    if os.environ.get("KIT_CURRENCY_NESTED"):
        return False
    v = os.path.join(repo, "verify")
    if not (os.path.isfile(v) and os.access(v, os.X_OK)):
        return False
    name = f".kit-currency-plant-{os.getpid()}.md"
    path = os.path.join(repo, name)
    _sweep_stale_plants(repo)
    snap = _harness_snapshot(repo)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(plant_lines) + "\n")
        env = dict(os.environ, KIT_CURRENCY_NESTED="1", KIT_LEAK_PLANT=name)
        r = subprocess.run(verify_cmd(), cwd=repo, capture_output=True,
                           text=True, timeout=120, env=env)
        return name in (r.stderr + r.stdout)
    except (OSError, subprocess.TimeoutExpired):
        return False
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
        _harness_restore(repo, snap)


# Planted lines are ASSEMBLED, never written as literals: this file is greppable
# by every leak gate in the fleet, and a literal identity path here would make
# the currency checker itself the leak (Decision 55's test fixture lesson).
_POSIX_PLANT = "/" + "Users" + "/someone/secret"
_WIN_PLANT = "C:" + "\\" + "Users" + "\\someone\\secret"


def _present(repo, target, kind):
    import subprocess
    if kind == "gate-fires:posix":
        return _gate_report(repo)["posix"]
    if kind == "gate-fires:windows":
        return _gate_report(repo)["windows"]
    if kind == "plant-invisible":
        return _gate_report(repo)["plant_invisible"]
    if kind == "vendored":
        return _vendored_current(repo)
    p = os.path.join(repo, target)
    if kind == "file":
        return os.path.isfile(p)
    if kind == "dir":
        return os.path.isdir(p)
    if kind == "dir-nonempty":
        return os.path.isdir(p) and any(
            f.endswith((".yml", ".yaml")) for f in os.listdir(p))
    if kind == "tracked":
        # Presence is not policy: an UNTRACKED .gitattributes never reaches a
        # clone or CI, so the Windows-CRLF hazard it claims to close stays
        # fully live while the check reads [x]. Tonality found their own repo
        # in exactly that state, declaring 2.4.1 (2026-08-18). Same family as
        # 2.2.0's contains:leak_gate — the file existing is not the file
        # working. Two repos fleet-wide were in this state when it was fixed.
        return subprocess.run(["git", "-C", repo, "ls-files", "--error-unmatch", target],
                              capture_output=True).returncode == 0
    if kind == "exec":
        return os.path.isfile(p) and os.access(p, os.X_OK)
    if kind.startswith("contains:"):
        needle = kind.split(":", 1)[1]
        try:
            with open(p, encoding="utf-8", errors="ignore") as fh:
                return needle in fh.read()
        except OSError:
            return False
    raise ValueError(kind)


def declared_version(repo):
    m = os.path.join(repo, "project.manifest.json")
    try:
        with open(m, encoding="utf-8") as fh:
            v = json.load(fh).get("kit_version")
        return v if isinstance(v, str) and v else None
    except (OSError, ValueError):
        return None


def report(repo, kit_dir):
    """Currency COMPUTED from the tree, not read from a declaration.

    Until 2.6.0 this asked the manifest what version the repo claimed and
    diffed the CHANGELOG above it. That made the claim the gate, and a claim
    goes stale on its own: on 2026-08-18, 24 repos that had retrofitted THAT
    DAY read BEHIND again, and every one of them satisfied every requirement
    of every version it was behind. Zero needed work. The ledger was asking
    for 24 sessions to edit 24 strings.

    So the question changed from "what does this repo say" to "what does this
    repo MEET". A version is behind only when one of its requirements is
    actually unmet. Nothing to declare, nothing to go stale, and a kit bump
    now touches only the repos that genuinely fail its new requirement — the
    same nine versions that cost the fleet 24 sessions would have cost 2.

    `kit_version` in the manifest survives as PROVENANCE ("last deliberately
    retrofitted at X") and is reported, never gated on. It is the one thing
    the tree cannot tell you, which is exactly the thing a note is for.
    """
    kv = kit_version(kit_dir)
    declared = declared_version(repo)
    entries = changelog_entries(kit_dir)
    out = {
        # Absolute in JSON (machine-consumed, never committed); the human-facing
        # render tildes it — a notice pasting this lands in a PUBLIC repo.
        "repo": os.path.abspath(repo),
        "kit_version": kv,
        "declared": declared or "pre-2.0.0",   # provenance only
        "behind": [],
    }
    for ver, date, title, _ in entries:
        if ver in TOOL_ONLY:
            continue                            # tool-only bumps ask nothing
        reqs = REQUIREMENTS.get(ver, [])
        checks = [{"label": lbl, "present": _present(repo, tgt, kind)}
                  for lbl, tgt, kind in reqs]
        missing = [c["label"] for c in checks if not c["present"]]
        if missing:
            out["behind"].append({
                "version": ver, "date": date, "title": title,
                "checks": checks, "missing": missing,
            })
    out["current"] = not out["behind"]
    # Kept for consumers that still read it: under computed currency a repo
    # cannot "declare X while missing Y", because nothing is declared. An
    # unmet requirement is simply an unmet requirement, and it is in `behind`.
    out["declared_but_missing"] = []
    return out


def render(r):
    lines = [f"kit currency — {_tilde(r['repo'])}",
             f"  kit: {r['kit_version']}   declared: {r['declared']}   "
             + ("CURRENT" if r["current"] else f"BEHIND by {len(r['behind'])} entr{'y' if len(r['behind'])==1 else 'ies'}")]
    if r.get("declared_but_missing"):
        lines.append(f"  !! declares {r['kit_version']} but is missing: "
                     + ", ".join(r["declared_but_missing"]))
    for b in r["behind"]:
        lines.append(f"  → {b['version']} ({b['date']}) {b['title']}")
        for c in b["checks"]:
            lines.append(f"      [{'x' if c['present'] else ' '}] {c['label']}")
    if r["current"] and not r.get("declared_but_missing"):
        lines.append("  nothing to do — re-running the retrofit is a no-op")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--kit", default=_HERE)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not os.path.isdir(a.repo):
        print(f"currency: {a.repo} is not a directory", file=sys.stderr)
        return 2
    r = report(a.repo, a.kit)
    print(json.dumps(r, indent=2) if a.json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
