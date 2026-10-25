#!/usr/bin/env bash
# distillery-daily-async — SessionStart hook: start distillery's daily sweep
# (distillery `bin/daily`, its decision 23; autonomous Decision 101) in the
# background, and return at once.
#
# WHY A SESSION HOOK: launchd cannot read ~/Documents (macOS privacy
# protection; Decision 42 and fleet-sweep-async.sh tell that story), and a
# Claude session can. The sweep only matters on days lessons change, which
# are days a session runs.
#
# Once a day is bin/daily's own rule (its stamp and its runner lock). The
# check here only spares a session start the cost of launching Python on the
# days it has already run.
set -uo pipefail
D="${DISTILLERY_HOME:-$HOME/Documents/Claude/distillery}"
S="${DISTILLERY_DAILY_HOME:-$HOME/.claude/fleet/distillery}"
[ -x "$D/bin/daily" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0
[ -f "$S/last-run" ] && [ "$(cat "$S/last-run" 2>/dev/null)" = "$(date +%F)" ] && exit 0
mkdir -p "$S"
# Detached: the session must never wait on a sweep, a fetch or a verify.
nohup python3 "$D/bin/daily" >>"$S/hook.out" 2>&1 </dev/null &
exit 0
