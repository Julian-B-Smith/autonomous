#!/usr/bin/env python3
"""monitor — the governor's deterministic fleet-health watchdog.

Rolls up per-repo health checks across the roster into a STATUS dashboard +
severity summary, so "how is the fleet doing?" is one command instead of the
manual audits. NO model calls (AI/deterministic boundary — the watchdog is
deterministic by contract). Read-only across the roster; writes only its own
STATUS.md (writes-stay-home).

This is the watchdog-as-MONITOR — the earned half of the governor. The
fleet-CONTROLLER half (HALT sentinel, conductor, coherence critic) waits for a
running organ fleet to govern; there is none yet, so it is not built.

Per-repo checks:
  LEAK     (HIGH) machine-absolute paths / username in tracked files (leak_scan)
  UNGATED  (WARN) ./verify exists but no leak_gate wired into it
  NO-CI    (WARN) has a remote but no .github/workflows/*.yml
  STALE    (WARN) README 'Last verified' missing or older than --stale-days
  STATUS-PROSE (WARN) manifest 'status' carries progress content (Decision 28:
                 phase state belongs in ROADMAP, not the manifest)
  GAPS     (INFO) missing harness files (claude_md/roadmap/traces/manifest/library)

Usage:
  monitor.py --registry ../registry.json [--stale-days 30]
             [--today YYYY-MM-DD] [--out governor/STATUS.md] [--json]
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "kit", "sweep"))
import sweep        # noqa: E402  (roster enumeration + derive_status)
sys.path.insert(0, _HERE)
import leak_scan    # noqa: E402  (the leak content scan, kept consistent with the gate)
import ball_scan    # noqa: E402  (open INTEGRATIONS exchanges — who owes whom)
import s4_scan      # noqa: E402  (VSM S4: is the intelligence organ alive and consumed?)

# Progress content that belongs in ROADMAP, not the manifest status field
# (Decision 28). Case-sensitive DONE/CLOSED + the ✅/🟡 status glyphs catch real
# status prose; a short "RATIFIED <date>"/"see ROADMAP" pointer does not — and
# incidental refs like "O0 gate" must NOT trip it, so we do not match phase ids.
_STATUS_PROSE = re.compile(r"\bDONE\b|\bCLOSED\b|\bIMPLEMENTED\b|[✅🟡]")
_LAST_VERIFIED = re.compile(r"[Ll]ast verified[^:\n]*:\s*(\d{4}-\d{2}-\d{2})")


def _read(path, *rel):
    p = os.path.join(path, *rel)
    try:
        with open(p, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return None


def readme_last_verified(path):
    """The ISO date on the README's 'Last verified' line, or None if absent."""
    text = _read(path, "README.md")
    if text is None:
        return None
    m = _LAST_VERIFIED.search(text)
    return m.group(1) if m else None


def days_since(datestr, today):
    y, m, d = (int(x) for x in datestr.split("-"))
    return (today - datetime.date(y, m, d)).days


def manifest_status_prose(path):
    """The offending snippet if the manifest status carries progress content,
    else None. A long field is a smell even without a keyword (the pre-Dec-28
    Orrery status was 447 chars); the pointer form ('see ROADMAP') is short."""
    text = _read(path, "project.manifest.json")
    if text is None:
        return None
    try:
        status = json.loads(text).get("status", "")
    except ValueError:
        return None
    # `status` is prose by convention, but a repo may legitimately use a
    # STRUCTURED status (juce-rag ships {"ratified":…, "note":…}) — which is
    # arguably the better shape. Flatten dict/list values and scan the strings
    # inside; anything else has no prose to drift. Assuming str here crashed the
    # whole dashboard on one repo's schema choice (2026-07-28).
    if isinstance(status, dict):
        status = " ".join(str(v) for v in status.values() if isinstance(v, str))
    elif isinstance(status, list):
        status = " ".join(str(v) for v in status if isinstance(v, str))
    elif not isinstance(status, str):
        return None
    if _STATUS_PROSE.search(status) or len(status) > 250:
        return status[:90]
    return None


def manifest_dormant(path):
    """The manifest's `dormant` declaration, or None.

    Shape (specified in response to antiphon-001, 2026-07-28):
        "dormant": {"since": "YYYY-MM-DD", "reason": "...",
                    "review_by": "YYYY-MM-DD"}

    `review_by` is REQUIRED and load-bearing. A permanent "ignore me" flag is
    precisely how an abandoned repo hides from a health sweep, so dormancy
    EXPIRES: it defers activity warnings until a dated audit beat, then becomes
    a louder warning than the one it suppressed. Deferred, never hidden —
    doctrine's "staleness is visible, never hidden". A declaration missing
    `review_by` is ignored (treated as no declaration), so the incomplete form
    fails toward noise rather than toward silence.
    """
    text = _read(path, "project.manifest.json")
    if text is None:
        return None
    try:
        d = json.loads(text).get("dormant")
    except ValueError:
        return None
    if not isinstance(d, dict) or not isinstance(d.get("review_by"), str):
        return None
    return d


def verify_has_leak_gate(path):
    """True/False if a ./verify exists (does it wire leak_gate?), None if none."""
    text = _read(path, "verify")
    return None if text is None else ("leak_gate" in text)


def has_ci(path):
    d = os.path.join(path, ".github", "workflows")
    return os.path.isdir(d) and any(
        f.endswith((".yml", ".yaml")) for f in os.listdir(d)
    )


def check_repo(proj, today, stale_days):
    """All checks for one repo -> {check: (severity, detail)}. Read-only."""
    path = proj["path"]
    out = {}
    st = sweep.derive_status(path)
    if not st["git"]:
        return out  # non-git dirs carry no history to leak or gate

    # Identity leak (the actual username in tracked files) is HIGH — fix now.
    # A generic /Users/<other>/ path (a foreign example, a leak-detection test
    # literal) is WARN: review or allowlist, but it isn't YOUR identity leaking.
    leaks = leak_scan.scan_repo(path)
    if any(lbl == "local username" for _, lbl, _ in leaks):
        n = sum(1 for _, lbl, _ in leaks if lbl == "local username")
        out["LEAK"] = ("HIGH", f"username in {n} tracked line(s)")
    elif any(lbl == "absolute home path" for _, lbl, _ in leaks):
        out["PATH"] = ("WARN", "generic /Users path — review or allowlist")

    gated = verify_has_leak_gate(path)
    if gated is False:
        out["UNGATED"] = ("WARN", "./verify has no leak_gate")

    # Dormancy defers the ACTIVITY warning only, and only until its review date.
    # A green repo with no commits is otherwise indistinguishable from an
    # abandoned one (antiphon-001) — but suppressing that forever would make the
    # flag a rot-concealer, so an expired declaration is LOUDER than STALE.
    dormant = manifest_dormant(path)
    if dormant and days_since(dormant["review_by"], today) > 0:
        out["DORMANT-EXPIRED"] = (
            "WARN",
            f"dormancy review_by {dormant['review_by']} has passed — re-ratify or wake",
        )
        dormant = None  # expired: fall through to the normal staleness checks

    # MAINTENANCE warnings are deferred by a live dormancy declaration;
    # SECURITY findings never are. A repo nobody develops still leaks in
    # public, so LEAK/PATH above are computed before this point and are not
    # suppressed. Adding CI or a kit version to finished software, by contrast,
    # is a chore nobody will do — and an undoable chore on a dashboard is how
    # the dashboard stops being read.
    if st.get("remote") and not has_ci(path) and not dormant:
        out["NO-CI"] = ("WARN", "remote but no .github/workflows")

    lv = readme_last_verified(path)
    if dormant:
        out["DORMANT"] = ("INFO", f"dormant by design since {dormant.get('since','?')}"
                                  f" · review {dormant['review_by']}")
    elif lv is None:
        if st["claude_md"] or st["roadmap"]:      # a harnessed repo should have one
            out["STALE"] = ("WARN", "README has no 'Last verified' line")
    elif days_since(lv, today) > stale_days:
        out["STALE"] = ("WARN", f"README {days_since(lv, today)}d stale (last {lv})")

    prose = manifest_status_prose(path)
    if prose:
        out["STATUS-PROSE"] = ("WARN", "manifest status carries progress content")

    # Kit currency (K0). INFO, not WARN: today 46/47 repos are pre-2.0.0
    # and a WARN on all of them is noise that buries real WARNs. It becomes
    # WARN when the K4 catch-up leaves a repo behind by choice.
    if (st.get("kit_version", "pre-2.0.0") == "pre-2.0.0"
            and st.get("claude_md") and not dormant):
        out["KIT-PRE"] = ("INFO", "no kit_version declared — pre-2.0.0")

    gaps = [k for k in ("claude_md", "roadmap", "traces", "manifest", "library")
            if not st.get(k)]
    # kit 2.1.0's charter section has NO currency requirement, by design
    # (gating prose rewards the words over the understanding), so a repo
    # missing it reads CURRENT and no retrofit ever points at the gap: 11 of 47
    # vendored repos on 2026-09-28, found by resume-workshop's retrofit notice.
    # Listed here at INFO so it is at least visible; never a gate.
    if st.get("claude_md") and not re.search(
            r"(?im)^#{1,6} .*mailbox", _read(proj["path"], "CLAUDE.md") or ""):
        gaps.append("mailbox_section")
    if gaps and (st["claude_md"] or st["verify"]) and not dormant:
        out["GAPS"] = ("INFO", "missing " + ",".join(gaps))
    return out


def render_exchanges(projects, today):
    """Fleet-wide open-exchange block.

    Deliberately its OWN section rather than per-repo severity rows. The fleet
    already carries ~56 WARNs; an overdue obligation folded into that pile is
    findable only by someone already looking, which is the failure this check
    exists to fix. One list, sorted worst-first, is the whole point.
    """
    overdue, ours, untracked = [], [], []
    for p in projects:
        for th in ball_scan.scan_repo(p["path"], p["name"], today):
            if th["days_overdue"]:
                overdue.append((th["days_overdue"], p["name"], th))
            elif th["ours"]:
                ours.append((p["name"], th))
        for f in ball_scan.untracked_mailbox_files(p["path"]):
            untracked.append((p["name"], f))

    out = ["", "## Open exchanges (INTEGRATIONS `ball:`)", ""]
    if not (overdue or ours or untracked):
        out += ["Nothing owed. No overdue balls, no uncommitted mailbox writes.", ""]
        return out, len(overdue)

    if overdue:
        out += ["### OVERDUE — past `respond-by`, ball on us", ""]
        for d, repo, th in sorted(overdue, key=lambda t: (-t[0], t[1], t[2]["id"])):
            out.append(f"- **{d}d overdue** · `{repo}` · `{th['id']}` "
                       f"(due {th['respond_by']}, status `{th['status']}`)")
        out.append("")
    if ours:
        out += ["### Ball on us, no deadline breached", ""]
        for repo, th in sorted(ours, key=lambda t: (t[0], t[1]["id"])):
            out.append(f"- `{repo}` · `{th['id']}` — status `{th['status']}`"
                       + (f", due {th['respond_by']}" if th["respond_by"] else ""))
        out.append("")
    if untracked:
        out += ["### Uncommitted mailbox writes", "",
                "Filed by a visitor under the mailbox exception; committing them is a",
                "RESIDENT action. Until then they are invisible to anyone reading the",
                "repo through git.", ""]
        for repo, f in sorted(untracked):
            out.append(f"- `{repo}` · `{f}`")
        out.append("")
    return out, len(overdue)


def render_s4(repo, today, s4_days):
    """VSM amendment B — the 'Outside & then' block. Its OWN section, beside
    the health rows and above the exchanges: Beer's core claim is that
    adaptation fails when inside-and-now crowds out outside-and-then, and in
    this fleet nearly all agent time IS inside-and-now. Making the S3–S4
    confrontation visible where the human already looks costs zero agents.
    """
    findings = s4_scan.scan(repo, today, s4_days)
    newest = s4_scan.newest_research_date(repo)
    out = ["", "## Outside & then (VSM S4 — intelligence organ)", ""]
    out.append(f"- newest research artifact: {newest or 'none'}")
    if not findings:
        out += ["- audit delivery: current · no open PRs", ""]
        return out, findings
    for k, (sev, d) in findings.items():
        out.append(f"- **{sev}** `{k}` — {d}")
    out.append("")
    return out, findings


def render_status(rows, today, stale_days):
    sev = {"HIGH": 0, "WARN": 0, "INFO": 0}
    for _, checks in rows:
        for c in checks.values():
            sev[c[0]] += 1
    lines = [
        "# Fleet health — governor watchdog (deterministic monitor)",
        "",
        f"*Generated {today.isoformat()} · stale threshold {stale_days}d · "
        f"no model calls.* Run: `python3 governor/monitor.py --registry registry.json`",
        "",
        f"**{sev['HIGH']} HIGH · {sev['WARN']} WARN · {sev['INFO']} INFO** "
        f"across {len(rows)} repos.",
        "",
        "| repo | findings |",
        "|---|---|",
    ]
    order = {"HIGH": 0, "WARN": 1, "INFO": 2}
    flagged = [(n, c) for n, c in rows if c]
    flagged.sort(key=lambda r: min(order[v[0]] for v in r[1].values()))
    for name, checks in flagged:
        parts = sorted(checks.items(), key=lambda kv: order[kv[1][0]])
        cells = " · ".join(f"**{k}** {v[1]}" if v[0] == "HIGH" else f"{k} ({v[1]})"
                           for k, v in parts)
        lines.append(f"| {name} | {cells} |")
    if not flagged:
        lines.append("| — | fleet clean ✓ |")
    lines.append("")
    lines.append("Severities: HIGH = fix now (privacy leak). WARN = policy "
                 "drift (ungated / no-CI / stale README / manifest status prose). "
                 "INFO = incomplete harness. Un-flagged repos passed every check.")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="monitor")
    ap.add_argument("--registry", required=True)
    ap.add_argument("--s4-days", type=int, default=35,
                    help="WARN when the newest research artifact is older than this")
    ap.add_argument("--stale-days", type=int, default=30)
    ap.add_argument("--today", help="ISO date override (default: system date)")
    ap.add_argument("--out", default=None, help="write STATUS markdown here")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    today = (datetime.date.fromisoformat(args.today) if args.today
             else datetime.date.today())
    registry = json.load(open(args.registry))
    # Per-repo isolation: one repo's unexpected data shape must never take the
    # whole fleet dashboard down with it. A crashed monitor reports NOTHING,
    # which reads exactly like a healthy fleet — the silent-failure mode this
    # tool exists to prevent. A repo that blows up is itself a finding.
    def _guarded(p):
        try:
            return check_repo(p, today, args.stale_days)
        except Exception as exc:  # noqa: BLE001 — surface, never swallow
            return {"MONITOR-ERROR": ("HIGH", f"{type(exc).__name__}: {exc}")}

    projects = list(sweep.resolve(registry))
    rows = [(p["name"], _guarded(p)) for p in projects]
    exchange_md, n_overdue = render_exchanges(projects, today)
    s4_md, s4_findings = render_s4(os.path.join(_HERE, ".."), today, args.s4_days)

    if args.json:
        json.dump({n: c for n, c in rows}, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    # K4 checklist — DERIVED from the fleet each run, never stored. It is
    # appended to STATUS.md so it lands where the human already looks; the
    # human asked for a list that "updates as each retrofit happens," and this
    # is that, minus the notice channel: a repo is done when it READS as done.
    try:
        checklist = subprocess.run(
            [sys.executable, os.path.join(_HERE, "..", "kit", "retrofit_checklist.py"), "--md"],
            capture_output=True, text=True, timeout=120).stdout
    except Exception:
        checklist = ""
    md = (render_status(rows, today, args.stale_days)
          + "\n".join(s4_md) + "\n".join(exchange_md)
          + ("\n\n" + checklist if checklist else ""))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(md)
    # compact stdout summary (the dashboard is the file)
    sev = {"HIGH": 0, "WARN": 0, "INFO": 0}
    for _, c in rows:
        for v in c.values():
            sev[v[0]] += 1
    print(f"monitor: {sev['HIGH']} HIGH · {sev['WARN']} WARN · {sev['INFO']} INFO "
          f"across {len(rows)} repos"
          + (f" · {n_overdue} OVERDUE ball(s)" if n_overdue else "")
          + (f" · S4: {', '.join(s4_findings)}" if s4_findings else "")
          + (f" → {args.out}" if args.out else " (use --out to write STATUS.md)"))
    for name, checks in rows:
        hi = [k for k, v in checks.items() if v[0] == "HIGH"]
        if hi:
            print(f"  HIGH  {name}: {', '.join(hi)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
