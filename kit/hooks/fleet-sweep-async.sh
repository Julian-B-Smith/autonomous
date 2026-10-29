#!/usr/bin/env bash
# fleet-sweep-async — SessionStart hook (async). Refreshes the governor's sweep
# cache in the background for the NEXT session to read.
#
# WHY THIS AND NOT launchd/cron: tried that first and it failed silently.
# macOS TCC protects ~/Documents, and a LaunchAgent does not inherit Full Disk
# Access, so `python3 monitor.py` under launchd returns "Operation not
# permitted" — exit 512 — while STATUS.md keeps whatever mtime a manual run last
# gave it. The job looks installed, the dashboard looks fresh, and nothing runs.
# That is the exact silent-success shape the governor exists to catch, so it is
# not an acceptable way to run the governor. Granting Full Disk Access to a bare
# interpreter would fix it and is a far worse trade.
#
# A Claude Code session already has access to these paths, so running the sweep
# from a session hook sidesteps TCC entirely and needs no scheduler at all.
#
# PAIRING: `fleet-brief.sh` runs synchronously and reads the cache (instant);
# this runs async and rewrites it (~4s, off the critical path). So a session
# reports the previous sweep immediately and leaves a fresh one behind. The
# freshness gap is one session, and fleet-brief prints the cache age so the gap
# is visible rather than assumed.
set -uo pipefail

REPO="${AUTONOMOUS_HOME:-$HOME/Documents/Claude/autonomous}"
[ -f "$REPO/governor/monitor.py" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# KIT_CURRENCY_NO_PROBE: this sweep never runs a repo's ./verify (Decision
# 107). Currency's behavioural probe does, for any repo whose vendored kit is
# stale, and it ran on every session open in every repo: culture's verify
# pinned the CPU with orphaned trace runs. Hashes only here; a stale repo reads
# BEHIND (not proven) until it syncs, and a full probe is a manual run.
export KIT_CURRENCY_NO_PROBE=1

# --out is written atomically enough for our purposes: a reader that catches a
# partial file sees fewer findings, never wrong ones, and the next run fixes it.
python3 "$REPO/governor/monitor.py" \
    --registry "$REPO/registry.json" \
    --out "$REPO/governor/STATUS.md" >/dev/null 2>&1 || true
exit 0
