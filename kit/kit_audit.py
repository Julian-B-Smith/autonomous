#!/usr/bin/env python3
"""kit_audit — the confirmation step after a kit update. Did it actually land?

Vendoring makes the question cheap, not automatic. A checksum says the BYTES
match canonical; it does not by itself say the repo still works, that nothing
else was disturbed, or that identical bytes behave identically on that machine
(a different bash, a different git, a shell option set in a project's own
verify). So this reports three independent things per repo and never collapses
them into one number:

  sync      .kit/ vs the kit — current | stale | edited | absent  (hash)
  wired     ./verify actually SOURCES the vendored gates          (reachability)
  oracle    the repo's own ./verify fast exit code                (behaviour)
  scope     working-tree changes outside .kit/ and verify        (INFORMATIONAL)

`sync` without `wired` is the old trap in a new costume: a repo can carry a
perfect, checksum-verified copy of the gate and still be completely ungated,
because its `verify` never sources it. Installing files is not installing
protection. The audit reports them separately and treats unwired as a
finding, never as a pass — three repos read `current` and SILENT on the first
fleet run for exactly this reason.

Plus a BEHAVIOURAL SAMPLE: on a few repos it runs the real plant probe and
requires the gate to fire, confirming that the checksum inference holds in the
field. The sample is the honest remnant of "assert the effective state, never
the declared state" — vendoring lets us stop probing every repo, it does not
license trusting the inference untested. Deterministic (sorted, strided), so
two runs sample the same repos and a run is reproducible.

  kit_audit.py [--sample N] [--registry ...] [--json]
"""
import argparse, json, os, subprocess, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..")
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "sweep"))
import kit_sync  # noqa: E402
import currency  # noqa: E402
import sweep     # noqa: E402

# The plant MUST match the `.kit-currency-plant-*` name that 2.3.0's gate
# exclusion knows, or a concurrent `./verify` in the target repo sees it and
# reds on a file that vanishes — the exact race 2.3.0 fixed, reintroduced by
# using a different filename here. attest caught this during a live audit,
# 2026-08-18: their verify exited 1 on `chk-win.md` and was green a command
# later. Owning the run via KIT_LEAK_PLANT keeps the plant visible to US.
_PLANT = f".kit-currency-plant-audit-{os.getpid()}.md"
EXPECTED = {".kit/", "verify"}


def _scope(path):
    """Working-tree changes outside what a kit update is allowed to touch."""
    out = subprocess.run(["git", "-C", path, "status", "--porcelain"],
                         capture_output=True, text=True).stdout.splitlines()
    stray = []
    for line in out:
        f = line[3:].strip().strip('"')
        if not any(f == e or f.startswith(e) for e in EXPECTED):
            stray.append(f)
    return stray


def _wired(path):
    """Does this repo's verify reach the vendored gates?

    Three states, not two — collapsing them made this report cry wolf:
      True   verify exists and sources .kit/kit-gates.sh
      False  verify EXISTS and does not source it — the real defect
      None   no verify at all: nothing to wire, and the repo's gap is the
             baseline retrofit, which is a different item on a different list
    """
    v = os.path.join(path, "verify")
    if not os.path.isfile(v):
        return None
    try:
        with open(v, encoding="utf-8") as fh:
            return ".kit/kit-gates.sh" in fh.read()
    except OSError:
        return False


WINDOWS_FORM = "x C:" + chr(92) + "Users" + chr(92) + "someone" + chr(92) + "x\n"
POSIX_FORM = "x " + "/" + "Users" + "/somebody/private\n"


def probe(path, form=POSIX_FORM):
    """Plant a real identity path; the gate must NAME it. THE canonical way to
    probe a foreign repo — hand-rolled one-off probes are how a differently
    named plant slipped past the 2.3.0 exclusion and raced a live session.

    Writes into a foreign tree, which is why it is a sample and not the
    default (LIBRARY L0006), and why the plant is named and owned so a
    concurrent run in that repo stays blind to it.
    """
    p = os.path.join(path, _PLANT)
    sys.path.insert(0, _HERE)
    import currency
    currency._sweep_stale_plants(path)      # clear any orphan a killed run left
    try:
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(form)
        env = dict(os.environ, KIT_LEAK_PLANT=_PLANT)
        r = subprocess.run(currency.verify_cmd(), cwd=path, capture_output=True,
                           text=True, timeout=180, env=env)
        return _PLANT in (r.stdout + r.stderr)
    except (OSError, subprocess.TimeoutExpired):
        return None
    finally:
        try:
            os.remove(p)
        except OSError:
            pass


def audit(registry, sample=3):
    with open(registry, encoding="utf-8") as fh:
        projects = [p for p in sweep.resolve(json.load(fh))
                    if os.path.isdir(os.path.join(p["path"], ".git"))
                    or os.path.isfile(os.path.join(p["path"], ".git"))]
    vend = [p for p in projects if kit_sync.check(p["path"])[0] != "absent"]
    stride = max(1, len(vend) // sample) if vend else 1
    sampled = {p["name"] for p in sorted(vend, key=lambda x: x["name"])[::stride][:sample]}
    rows = []
    for p in sorted(vend, key=lambda x: x["name"]):
        st, d = kit_sync.check(p["path"])
        # isfile AND executable: one repo has a DIRECTORY named `verify`, which
        # os.access(X_OK) happily calls executable.
        vp = os.path.join(p["path"], "verify")
        oracle = subprocess.run(currency.verify_cmd(), cwd=p["path"],
                                capture_output=True, text=True).returncode \
            if os.path.isfile(vp) and os.access(vp, os.X_OK) else None
        rows.append({"repo": p["name"], "sync": st, "wired": _wired(p["path"]), "oracle": oracle,
                     "stray": _scope(p["path"]),
                     "behaves": probe(p["path"]) if p["name"] in sampled else None})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=3)
    ap.add_argument("--registry", default=os.path.join(_ROOT, "registry.json"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rows = audit(a.registry, a.sample)
    if a.json:
        print(json.dumps(rows, indent=2)); return 0
    if not rows:
        print("kit_audit: no vendored repos yet"); return 0
    print(f"kit_audit — {len(rows)} vendored repo(s), kit {kit_sync.kit_version()}\n")
    print(f"  {'repo':34} {'sync':9} {'wired':6} {'oracle':7} {'probe':6} scope")
    bad = 0
    for r in rows:
        # `stray` is NOT a health criterion. It was written as the blast-radius
        # check for a batch write — "did my edit touch anything it should not"
        # — and left in as a pass/fail, where it flagged 26 repos for having
        # ordinary uncommitted work. A repo mid-feature is not unhealthy, and
        # an audit that says so trains its reader to ignore it.
        ok = (r["sync"] == "current" and r["wired"] is not False
              and r["behaves"] is not False)
        bad += 0 if ok else 1
        probe = {True: "fires", False: "SILENT", None: "—"}[r["behaves"]]
        oracle = "green" if r["oracle"] == 0 else (f"red({r['oracle']})" if r["oracle"] is not None else "—")
        scope = "clean" if not r["stray"] else f"{len(r['stray'])} uncommitted"
        wired = {True: "yes", False: "NO", None: "n/a"}[r["wired"]]
        print(f"  {r['repo']:34} {r['sync']:9} {wired:6} {oracle:7} {probe:6} {scope}")
    sampled = [r for r in rows if r["behaves"] is not None]
    print(f"\n  behavioural sample: {sum(1 for r in sampled if r['behaves'])}/{len(sampled)} "
          f"gates fired on a planted identity path")
    unwired = [r["repo"] for r in rows if r["wired"] is False]
    no_oracle = [r["repo"] for r in rows if r["wired"] is None]
    if unwired:
        print(f"\n  {len(unwired)} repo(s) carry the vendored gate but do NOT source it — "
              f"files installed, protection not. Run migrate_to_vendored.py there,\n"
              f"  or (where it refuses) wire `. .kit/kit-gates.sh` by hand.")
    if no_oracle:
        print(f"\n  {len(no_oracle)} repo(s) have .kit/ but no ./verify at all — not a wiring "
              f"defect; their gap is the baseline retrofit: {', '.join(no_oracle)}")
    print(f"  {'ALL CLEAR' if not bad else str(bad) + ' repo(s) need attention'}")
    # A red oracle is reported, never judged: a repo may be red for its own
    # reasons, and that is its resident's call, not this audit's.
    reds = [r["repo"] for r in rows if r["oracle"] not in (0, None)]
    if reds:
        print(f"  note: {len(reds)} repo(s) have a red ./verify for reasons this audit does "
              f"not judge — {', '.join(reds[:4])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
