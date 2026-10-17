# kit/plan/ — the plan map (DRAFT, format `kit.plan/0`)

The opt-in kit module of Decision 97, from horde's brief hypersaw-016. **Draft:**
the first instance is autonomous itself (`plan/`), and the format is open for
objection in thread plan-map before `/spinup` and `/retrofit` offer it to other
repos.

A plan map is a MAP of a repo's records, not a second copy of them.
`ROADMAP.md` stays the single source of truth for task state; the plan says,
for every part of the project, which rows and decisions govern it, where it
stands, and what it waits on, and checks that all of that is true.

    python3 kit/plan/plan.py build <dir>   # regenerate PLAN.md and plan-map.html
    python3 kit/plan/plan.py check <dir>   # headless checks; exit 1 if any is red

## Files in `<dir>`

| File | Written by | What |
|---|---|---|
| `parts.json` | a person or agent, by hand | the plan's structure (`kit.plan/0`) |
| `queue.json` | a person or agent, by hand | what is waiting on the human (`kit.queue/0`, the decision queue of Decision 90) |
| `PLAN.md` | `plan.py build` | the plan as a document; never hand-edited |
| `plan-map.html` | `plan.py build` | the plan as a picture; self-contained, no fetch |

## `parts.json` (`kit.plan/0`)

    {
      "format": "kit.plan/0", "title": "...", "lede": "...", "about": "...",
      "verified": {"date": "YYYY-MM-DD", "roadmap_commit": "<sha>", "decisions_max": <n>},
      "targets": ["<part id>", ...],          // critical paths are computed to these
      "tracks": ["<lane name>", ...],         // optional lane order on the map
      "status_meaning": {"<status>": "...", ...},
      "parts": [ {
        "id": "k3",                           // [a-z0-9][a-z0-9.-]*, never reused
        "title": "...", "what": "one line", "track": "<lane>", "note": "optional",
        "status": "closed | built | in progress | ruled | planned | later | parked | superseded",
        "rows": ["K3"],                       // ROADMAP labels: **K3 —, **Phase R —, or a heading
        "adrs": [77],                         // DECISIONS.md numbers
        "basis": ["D77", "R:K3", "file:kit/session"],   // the records that justify the STATUS
        "needs": ["k0"],                      // dependencies the records state
        "needs_inferred": ["o05"],            // the plan's own inference: drawn dashed
        "code": ["kit/session"]               // optional code layer: tracked paths
      } ],
      "inconsistencies": ["..."]              // where the records disagree, said, not chosen
    }

**One status vocabulary for every repo.** horde and loupe each hand-drew a map
before this module existed, with two different vocabularies:

| horde | loupe | kit |
|---|---|---|
| built | built | built, or closed once its gate is recorded as met |
| in progress | in progress | in progress |
| ruled | ready | ruled |
| planned | planned | planned |
| post-1.0 | later | later |
| parked | parked | parked |
| superseded | | superseded |

## `queue.json` (`kit.queue/0`)

    {"format": "kit.queue/0", "items": [
      {"id": "...", "question": "...", "raised": "YYYY-MM-DD",
       "recommendation": "...", "blocks": ["<part id>"], "lands_in": "where the answer is recorded"} ]}

An item leaves the file when the human rules, and the ruling cites it.

## The checks

Each has a must-fail control in `test_plan.py`. Red:

1. **Records exist.** Every cited row, decision and basis exists.
2. **Acyclic.** The dependency graph has no cycle.
3. **Well formed.** Ids, statuses, edges, targets and tracks are well formed.
4. **Generated files are fresh.** `PLAN.md` and `plan-map.html` match what the source generates.
5. **Status changes cite records** (brief lesson 2):
   - a status other than `planned` cites a record;
   - a status that changed since HEAD changed its basis too.

   An agent's reading goes in as a queue item or an inconsistency, never as a closure.
6. **Code paths exist.** Every `code` path matches a tracked file.
7. **Queue items are well formed.** Each names real parts and carries a recommendation.

Reported, never red (observe first, Decision 97):

- **Freshness:** decisions and ROADMAP commits since `verified`.
- **Critical path:** the longest chain of unfinished parts to each target, over cited edges only, with ties listed.
- **Parts ahead of their prerequisites:** parts recorded further along than a part they cite.

## Open for objection (thread plan-map)

- **The status vocabulary above**, and `closed` versus `built`.
- **Rows by label.** A row is cited by its ROADMAP label, not by a separate row-id column. horde uses B-numbers.
- **The code layer** is plain paths today. A loupe adapter would replace path counts with loupe's `file:` nodes (Decision 97).
