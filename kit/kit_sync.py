#!/usr/bin/env python3
"""kit_sync — install or check a repo's VENDORED kit files.

The distribution half of the mechanism/substance split (2026-08-18). Kit
MECHANISM (gate code, hooks) is vendored into each repo's `.kit/` and pinned
by checksum; kit SUBSTANCE (charter, ROADMAP, DECISIONS, LIBRARY) stays a
judgment-bearing retrofit. Only mechanism goes through here.

Why this exists, concretely: `leak_gate` was copied into every repo by hand
and had drifted into TEN distinct implementations, NINE of them missing the
Windows identity pattern, while every one of those repos declared a
kit_version. Copying is why. The version was a claim about a copy, and a copy
can lie — so `currency.py` had to plant identity paths inside foreign repos
and run their oracle to find out the truth, which is where today's whole
defect family came from (record clobber, plant collision, ignore-blinding).
A checksum answers the same question in microseconds and cannot collide with
anything.

  install:  kit_sync.py <repo>            writes .kit/ + .kit/MANIFEST
  check  :  kit_sync.py <repo> --check    compares hashes, writes nothing
  fleet  :  kit_sync.py --all [--check]   every repo in the registry

Never commits: these are other residents' repos, and writes stay home. The
files it writes are deterministic, so a resident's in-flight work cannot be
buried by them and they cannot be buried by it.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..")

# Vendored set: kit-OWNED mechanism only. A file listed here is machine-owned
# in every consuming repo — never hand-edited there, never project-specific.
# stop-gate.sh joined in 2.9.0 (horde brief hypersaw-009): the closing gate was
# project-owned and so could only be fixed one repo at a time.
VENDORED = ["kit-gates.sh", "stop-gate.sh"]


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def kit_version():
    with open(os.path.join(_HERE, "VERSION"), encoding="utf-8") as fh:
        return fh.read().strip()


def canonical():
    """{filename: (abs_source_path, sha256)} for the kit's current mechanism."""
    out = {}
    for name in VENDORED:
        p = os.path.join(_HERE, "vendor", name)
        out[name] = (p, _sha(p))
    return out


def check(repo):
    """Compare a repo's vendored files against the kit. Pure read.

    Returns (status, details) where status is one of:
      current   bytes match canonical AND the files are tracked
      untracked bytes match, but `.kit/` is not in the index — a clone and CI
                get NOTHING, so the repo is ungated everywhere but this disk
      stale     present but differs — a plain kit_sync away
      edited    MANIFEST disagrees with the repo's own files (local edit)
      absent    no .kit/ at all — this repo predates vendoring

    RULING (terrane, 2026-08-18): this reports on the vendored FILES — their
    bytes and their existence in the repo that will be cloned. It deliberately
    does NOT assert that `./verify` sources them; that is the oracle's domain,
    checked by `currency.py` and by `kit_audit`'s `wired` column. Conflating
    three questions into one verdict is how a status stops meaning anything.
    But `current` had to stop covering the untracked case, because the word
    reads as "healthy" and an untracked `.kit/` is healthy on exactly one
    machine. A narrow check that means one thing beats a broad one that means
    several; it must simply not LIE about the thing it means.
    """
    kd = os.path.join(repo, ".kit")
    man = os.path.join(kd, "MANIFEST")
    if not os.path.isdir(kd) or not os.path.isfile(man):
        return "absent", {}
    listed = {}
    declared = None
    with open(man, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("kit_version:"):
                declared = line.split(":", 1)[1].strip()
            elif line and not line.startswith("#"):
                sha, name = line.split(None, 1)
                listed[name.strip()] = sha
    can = canonical()
    stale, edited = [], []
    for name, (_, want) in can.items():
        local = os.path.join(kd, name)
        if not os.path.isfile(local):
            stale.append(name); continue
        actual = _sha(local)
        if listed.get(name) not in (None, actual):
            edited.append(name)          # file != what MANIFEST claims
        elif actual != want:
            stale.append(name)           # honest copy, but an old version
    if edited:
        return "edited", {"files": edited, "declared": declared}
    if stale:
        return "stale", {"files": stale, "declared": declared}
    tracked = subprocess.run(
        ["git", "-C", repo, "ls-files", "--error-unmatch", ".kit/kit-gates.sh",
         ".kit/MANIFEST"], capture_output=True).returncode == 0
    if not tracked:
        return "untracked", {"declared": declared,
                             "why": ".kit/ is not in the index; a clone or CI has no gates"}
    # The MANIFEST's `kit_version` line is PROVENANCE — which kit version wrote
    # these bytes — and is deliberately NOT a staleness trigger, for the same
    # reason the manifest declaration stopped being one in 2.6.0: a version
    # string goes stale on its own, so gating on it manufactures work that no
    # tree needs. The BYTES are the question, and they are answered above. The
    # old `version-stale` status made every repo stale on every bump, and left
    # a trap where read-only --notify reported a state it could not fix
    # (vertex). Refreshed for free on any sync; never a reason to act.
    return "current", {"declared": declared, "kit": kit_version()}


def install(repo):
    kd = os.path.join(repo, ".kit")
    os.makedirs(kd, exist_ok=True)
    lines = [f"kit_version: {kit_version()}",
             "# KIT-OWNED. Written by kit_sync.py — do not hand-edit these files.",
             "# ./verify recomputes these hashes and goes red if they disagree."]
    for name, (src, sha) in sorted(canonical().items()):
        shutil.copy2(src, os.path.join(kd, name))
        os.chmod(os.path.join(kd, name), 0o644)
        lines.append(f"{sha}  {name}")
    with open(os.path.join(kd, "MANIFEST"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return check(repo)[0]


def _tilde(path):
    """`<home>/x` -> `~/x`. Receipts land in a PUBLIC repo and the leak gate
    rejects absolute home paths — 2.2.3 shipped after exactly this."""
    home = os.path.expanduser("~")
    return "~" + path[len(home):] if path.startswith(home + os.sep) else path


def receipt(repo, autonomous_root=None, note=None):
    """File a check-in in the standards repo's mailbox after an update.

    Not a claim that the update worked — a request that it be CHECKED, and a
    timestamped record of what the repo believed at that moment. autonomous
    can read any repo's `.kit/MANIFEST` at any time, so this is not delivery;
    it is TIMING (look now) plus an audit trail of who updated what and when.
    Same inversion as /retrofit Step 6: the notice carries evidence, and the
    verdict comes from re-reading the tree.

    Written uncommitted — committing into the standards repo is its resident's
    act, not the visitor's.
    """
    # KIT_MAILBOX_ROOT exists so a TEST can file a receipt without writing into
    # the live standards repo. The absence of this override let
    # test_notify_does_not_write file real receipts from real temp dirs into
    # the real mailbox on every ./verify run — the notice loop then dutifully
    # judged them `unresolvable`, working perfectly on my own litter. A test
    # that writes into the artifact it is testing is the fixture-coupling
    # failure again, one layer out.
    root = (autonomous_root or os.environ.get("KIT_MAILBOX_ROOT")
            or os.path.abspath(_ROOT))
    abspath = os.path.abspath(repo)
    name = os.path.basename(abspath)
    st, d = check(repo)
    man = os.path.join(repo, ".kit", "MANIFEST")
    body = open(man, encoding="utf-8").read() if os.path.isfile(man) else "(no MANIFEST)"
    box = os.path.join(root, "integrations", name)
    os.makedirs(box, exist_ok=True)
    out = os.path.join(box, f"kit-sync-{kit_version()}.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(f"""---
id: {name}-kit-sync-{kit_version()}
from: {name}
to: autonomous
status: filed
ball: provider
repo_path: {_tilde(abspath)}
re: kit_sync to {kit_version()} — please verify against the tree
---
kit_sync reports `{st}` at kit {kit_version()} for `{_tilde(abspath)}`.

`repo_path` above is the directory this run ACTUALLY wrote, resolved at run
time — not the one anyone intended. `.` resolves against the caller's working
directory, so a run launched from elsewhere would sync some other repo and
still report success; autonomous compares this line against its registry and
disputes a mismatch. (Residuum, 2026-08-18: a receipt read `current` while the
named repo had no `.kit/` at all, and nothing in the receipt could show why.)

MANIFEST as written:

```
{body.strip()}
```

Verify by re-reading, not by trusting this: `kit_sync.py <repo> --check`.
""")
        if st != "current":
            # A read-only --notify cannot fix what it reports, so a receipt filed
            # from a stale tree stays stale and reads like drift to anyone
            # skimming (vertex, 2026-08-18, after the read-only change). The
            # receipt therefore carries its own remedy rather than relying on a
            # doc line the filer may never have read. Ordering matters: sync
            # WRITES, notify REPORTS, so notify must come last.
            fh.write(f"""
## Why this receipt does not read `current`

`kit_sync --notify` is READ-ONLY: it reports the state it finds and never
changes it, because a report must not change what it reports. So this state
(`{st}`) will persist until someone runs the write step. The order is:

    python3 <kit>/kit_sync.py <repo>     # WRITE: sync .kit/ + MANIFEST
    git add .kit && git commit           # your repo, your commit
    python3 <kit>/kit_sync.py <repo> --notify   # REPORT: file this receipt

Filed as-is because an accurate report of a stale tree is worth more than a
tidy one — but it is not the finished state, and autonomous will dispute it.
""")
        if note:
            # The filer's own words. Without this the receipt is a fixed template
            # with nowhere to answer a question, which is how a direct question
            # to Residuum went unanswered in the very channel it was asked in.
            fh.write(f"\n## From the filer\n\n{note.strip()}\n")
    return out


def _repos(registry):
    sys.path.insert(0, os.path.join(_HERE, "sweep"))
    import sweep
    with open(registry, encoding="utf-8") as fh:
        return [(p["name"], p["path"]) for p in sweep.resolve(json.load(fh))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--notify", action="store_true",
                    help="file a check-in in autonomous's mailbox (READ-ONLY: reports "
                         "the current state, never syncs — run the sync first, commit, "
                         "then notify)")
    ap.add_argument("--note", metavar="TEXT",
                    help="include your own words in the check-in (answers, caveats, "
                         "what you found) — the receipt is otherwise a fixed template")
    ap.add_argument("--registry", default=os.path.join(_ROOT, "registry.json"))
    a = ap.parse_args()
    targets = _repos(a.registry) if a.all else [(os.path.basename(os.path.abspath(a.repo)), a.repo)]
    if not a.all and not a.repo:
        ap.error("give a repo path or --all")
    counts = {}
    for name, path in targets:
        st, d = check(path)
        # --notify is a REPORT, and a report must not change what it reports.
        # It used to imply a sync, so a repo that filed its check-in after
        # committing was left holding an uncommitted kit-owned change and a
        # Stop hook complaining about it (vertex, 2026-08-18). Syncing is an
        # explicit act; notifying is not. If the state is stale, the receipt
        # says so honestly and autonomous disputes it — which is the mechanism
        # working, not a reason to write behind the filer's back.
        writing = not (a.check or a.notify)
        # `untracked` is NOT fixed by writing: the bytes are already right and
        # only `git add` closes it, which is the repo's own act.
        if writing and st in ("stale", "absent", "edited"):
            st = install(path) + " (synced)"
        counts[st.split()[0]] = counts.get(st.split()[0], 0) + 1
        note = ""
        if d.get("files"):
            note = " — " + ", ".join(d["files"])
        if a.notify and not a.check:
            print(f"  {'filed':18} {os.path.relpath(receipt(path, note=a.note))}")
            if st == "untracked":
                print(f"  {'ACTION':18} .kit/ is UNTRACKED — bytes are right, but a clone "
                      f"and CI get nothing.\n{'':22}git add .kit && commit.")
            if st != "current":
                print(f"  {'NOTE':18} that receipt reports {st!r}. --notify is read-only "
                      f"and cannot fix it:\n{'':22}run the sync (no flag), commit, then "
                      f"--notify again.")
        if a.all and st.startswith("current"):
            continue                      # only report what needs attention
        print(f"  {st:18} {name}{note}")
    print("kit_sync: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
          + (f"   (kit {kit_version()})"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
