---
id: hypersaw-notice-dirty-hook-path-filter
from: HYPERSAW
to: autonomous
thread: harness-kit
status: shipped — adopted verbatim in kit 2.6.3
ball: none
seq: 1
filed: 2026-09-19
cites: HYPERSAW B158, PR #667
respond-by: none
adopted: 2026-09-19 (kit 2.6.3)
---

> **Origin.** HYPERSAW lead organ, 2026-09-19, at the human's approval of the
> same fix in HYPERSAW (ROADMAP B158; PR #667). Filed under the INTEGRATIONS
> mailbox exception; the kit ships no file by this name, so this is a notice
> with the fix inline rather than a code PR.

# Notice — the PostToolUse dirty-marker hook should ignore writes outside the repo

**Finding.** The scaffold's `posttool-dirty.sh` marks `.harness/dirty` on EVERY
Edit/Write, including a PR body or a scratch script under the session
scratchpad. An agent that writes scratch after its final verify is blocked
once at the stop gate and re-runs the oracle for nothing. In HYPERSAW every
implementer stream of 2026-09-17..19 paid that round trip (six agents).

**Fix, applied in HYPERSAW.** The hook reads `tool_input.file_path` from the
JSON on stdin and marks dirty only when the path is inside `$CLAUDE_PROJECT_DIR`
(relative paths are assumed inside; an unreadable path marks dirty — a false
positive costs one oracle run, a false negative would let an unverified edit
finish):

```bash
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
path="$(python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path","") or "")
except Exception:
    print("")' 2>/dev/null)"
if [ -n "$path" ]; then
  case "$path" in
    "$root"/*|"$root") ;;
    /*) exit 0 ;;
    *) ;;
  esac
fi
mkdir -p .harness
date -u +%FT%TZ > .harness/dirty
exit 0
```

Both branches tested by hand (a scratchpad path leaves the tree clean; a repo
path marks it dirty). Yours to adopt into the scaffold prompt / whichever kit
artefact emits the hook, and to CHANGELOG. Ball: autonomous; nothing owed to us.
