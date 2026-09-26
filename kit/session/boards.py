#!/usr/bin/env python3
"""boards — render both boards, decide which changed, and log the run. K5.

The one entry point a routine or a session calls. Deterministic code decides
WHAT to publish; the calling Claude session only performs the publish, because
publishing an artifact is a tool call no script can make. That split is the
AI/deterministic boundary applied to bookkeeping: a session never judges
whether a board "looks changed", it reads the verdict this prints.

Why a scheduled Claude session and not GitHub Actions or a cloud routine: an
Actions runner cannot publish an artifact, and neither it nor a cloud routine
can see this machine's session registry or sibling repos' working trees, which
are exactly what the boards show. The Claude app's scheduled tasks run on this
machine with the folder access launchd lacked (Decision 42), so nothing here
needs Full Disk Access.

Output, one line per board, for the caller to act on:

    session-board  CHANGED    <out>/session-board.html  <url or ->
    threads-board  UNCHANGED  -                         <url or ->

and `NOT-PUBLISHER` for both when run outside the standards repo.

A board counts as published only when the caller CONFIRMS it, after the
publish succeeded: `boards.py --out <dir> --confirm <board>`. Recording at
render time was the first design and was wrong the day it ran — a failed or
forgotten publish left the marker saying "published", the next run said
UNCHANGED, and the stale page stayed up with nothing to show it. With
confirm-after-publish, a forgotten confirm costs one redundant republish next
tick: noise, never silent staleness, which is the safe direction.

Each run is
appended to `<registry>/boards.log` — the evidence for K5's gate ("one week of
routines producing artifacts the human actually read"), which the human
measures; this log only proves the routine RAN, never that anyone read it.

  boards.py --out <dir> [--why wakeup|breakdown|closeout|routine]
  boards.py --out <dir> --confirm session-board|threads-board
"""
import argparse, datetime, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import registry          # noqa: E402
import render_registry   # noqa: E402
import render_threads    # noqa: E402

BOARDS = (
    # name,           render fn,               marker,                 url file
    ("session-board", render_registry.render, ".board-render",        "BOARD_URL"),
    ("threads-board", render_threads.render,  render_threads.MARKER,  "THREADS_URL"),
)


def _url(root, name):
    try:
        with open(os.path.join(root, name), encoding="utf-8") as fh:
            return fh.read().strip() or None
    except (OSError, TypeError):
        return None


def run(out, why="routine", root=None):
    """[(board, verdict, path|None, url|None)]. Writes pages for CHANGED boards
    only, each with a pending `<board>.digest` beside it. Records nothing: the
    digest becomes the comparison point only through confirm()."""
    if not render_registry.is_publisher():
        return [(b[0], "NOT-PUBLISHER", None, None) for b in BOARDS]
    root = root or registry.root()
    os.makedirs(out, exist_ok=True)
    results = []
    for name, render, marker, url_file in BOARDS:
        try:
            page = render()
        except Exception as e:          # one broken board never blanks the other
            results.append((name, f"ERROR:{type(e).__name__}", None, None))
            continue
        is_new, digest = render_registry.changed(page, root=root, marker=marker)
        path = None
        if is_new:
            path = os.path.join(out, f"{name}.html")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(page)
            with open(os.path.join(out, f"{name}.digest"), "w", encoding="utf-8") as fh:
                fh.write(digest)
        results.append((name, "CHANGED" if is_new else "UNCHANGED", path,
                        _url(root, url_file)))
    _log(root, why, results)
    return results


def confirm(out, board, root=None):
    """Record a board as published, from the pending digest run() left in
    `out`. Returns False (and records nothing) if there is no pending digest
    — confirming a board this run did not render is a caller error, and
    recording a guess would reintroduce the silent-staleness bug."""
    markers = {n: m for n, _, m, _ in BOARDS}
    if board not in markers:
        return False
    try:
        with open(os.path.join(out, f"{board}.digest"), encoding="utf-8") as fh:
            digest = fh.read().strip()
    except OSError:
        return False
    root = root or registry.root()
    render_registry.record(digest, root=root, marker=markers[board])
    os.remove(os.path.join(out, f"{board}.digest"))
    _log(root, "confirm", [(board, "PUBLISHED", None, None)])
    return True


def _log(root, why, results):
    if not root:
        return
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = stamp + " " + why + " " + " ".join(f"{n}={v}" for n, v, _, _ in results)
    try:
        with open(os.path.join(root, "boards.log"), "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass                            # bookkeeping never blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="directory for rendered pages")
    ap.add_argument("--why", default="routine")
    ap.add_argument("--confirm", metavar="BOARD",
                    help="record BOARD as published (after the publish succeeded)")
    a = ap.parse_args()
    if a.confirm:
        ok = confirm(a.out, a.confirm)
        print(f"{a.confirm:<14} {'CONFIRMED' if ok else 'NOTHING-PENDING'}")
        return 0 if ok else 1
    for name, verdict, path, url in run(a.out, a.why):
        print(f"{name:<14} {verdict:<13} {path or '-'}  {url or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
