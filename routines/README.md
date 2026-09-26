# routines — scheduled processes that operate on this repo

Prompt files for recurring routines, versioned here so they're reviewable,
diffable, and portable across machines/substrates.

## fleet-boards (local, on a cadence) — K5

**Live variant: LOCAL** — the `fleet-boards` scheduled task in the Claude
desktop app on the primary machine, whose stored prompt is one line:
"In ~/Documents/Claude/autonomous, execute routines/boards.prompt.md."
[boards.prompt.md](boards.prompt.md) is the single definition. It runs
`kit/session/boards.py`, which renders the Session Board and Threads Board,
decides deterministically which changed (ignoring each page's own clock), and
logs every run to the session registry's `boards.log`; the scheduled session
only publishes what the script names. Local because the boards show this
machine's registry and sibling working trees, which no cloud routine or
Actions runner can see; and the Claude app has the folder access launchd
lacked, so nothing needs Full Disk Access (Decision 42). Runs only while the
app is open; a missed tick runs at next launch. Gate (ROADMAP K5): one week of
runs producing boards the human actually read, measured by the human.

## landscape-audit (monthly, propose-only)

**Live variant: CLOUD** —
[landscape-audit.cloud.prompt.md](landscape-audit.cloud.prompt.md) is the
single canonical definition of the process, running as a cloud routine
(since 2026-07-10). Output: a PR with
`research/proposals/<date>.proposal.md` (DELETIONS section required) + a
dated bibliography append. The routine never merges its own PR.

History: a local scheduled-task variant (`monthly-landscape-audit`, the
primary machine's Claude app) ran once as a test on 2026-07-10 and was
retired in favor of the cloud routine — its prompt survives at
`~/.claude/scheduled-tasks/monthly-landscape-audit/SKILL.md` (inert) and the
test surfaced the request-blockage lesson now baked into the prompt's
resilience section. If a local fallback is ever needed again, recreate the
task with a thin prompt: "pull github.com/Julian-B-Smith/autonomous and
execute routines/landscape-audit.cloud.prompt.md, skipping the cloud-setup
section." Never run two variants in the same month.

**To run the cloud variant via GitHub Actions**, a minimal workflow shape
(not installed — add deliberately, with `ANTHROPIC_API_KEY` in repo
secrets, and disable the local task's schedule to avoid double runs):

```yaml
# .github/workflows/landscape-audit.yml (example — not active)
name: landscape-audit
on:
  schedule: [{cron: "0 9 10 * *"}]   # UTC in Actions, unlike local tasks
  workflow_dispatch: {}
permissions: {contents: write, pull-requests: write}
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g @anthropic-ai/claude-code
      - run: claude -p "$(cat routines/landscape-audit.cloud.prompt.md)" --permission-mode acceptEdits
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Canonical-copy note:** the process definition effectively exists in two
places (the local task's stored prompt and the cloud prompt file). Tolerated
for now because the local task is mid-testing; once testing settles, the
clean fix is to thin the local task's prompt down to "pull the repo and
execute routines/landscape-audit.cloud.prompt.md, skipping the cloud-setup
section" — making THIS file the single canonical definition. Flagged as a
dedup item; see DECISIONS.md.
