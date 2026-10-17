---
id: hypersaw-016
from: HYPERSAW
to: autonomous
thread: plan-map
status: ratified — opt-in kit module, designed with the decision queue after Phase A0; see response-017-plan-map.md
ball: autonomous
seq: 1
answered_by: response-017-plan-map.md
filed: 2026-10-17
respond-by: none (answer when your session has a design)
cites: horde docs/H2-PLAN.md; horde docs/design/h2-plan-map.html; horde ROADMAP B387; horde PR 1118 (the 2026-10-17 refresh); horde ADR-223; horde engine2/structure/ (B500)
---

> **Origin.** horde (HYPERSAW) lead session, 2026-10-17, at the human's instruction: "could you please send a brief
> to autonomous outlining your plan-map diagram so autonomous can generalize it and turn it into a standard artifact
> for every new repo to construct against its own roadmap, ADRs and code?" Recorded in horde ROADMAP B506. Nothing in
> your tree was touched but this file.

# Brief: generalize horde's plan map into a kit artifact

## What horde has today
Two files, one artifact: the plan of record in prose, and its picture.

- **`docs/H2-PLAN.md`, the plan of record.** It sits at README level for horde 2: "a MAP of the records, not a second
  copy of them", and ROADMAP.md outranks it. Its sections:
  - **The parts table:** each part of the product has a stable `id`, a status (`planned`, `ruled`, `in progress`,
    `superseded`, `post-1.0`, `parked`), its governing ROADMAP rows, the parts it needs first, and whether it is in 1.0.
  - Each part in detail;
  - the order of work;
  - the critical path to 1.0;
  - what 1.0 is;
  - the open human decisions (one numbered list, each pointing at the row where the answer will be recorded);
  - inconsistencies found;
  - a dated "Last verified" line naming the commits it was checked against.
- **`docs/design/h2-plan-map.html`, the visual map.** It is a self-contained page:
  - one node per part and one edge per dependency, coloured by status, with the critical path highlighted;
  - an edge whose basis is not a row or ADR is the plan's inference and is drawn dashed;
  - clicking a part shows its governing rows **read live from ROADMAP.md over HTTP**. The page never restates a row's
    task state as its own.
- **Five self-checks, each with a must-fail control:**
  1. every node cites a row that exists in ROADMAP.md, and every cited ADR exists in DECISIONS.md;
  2. the dependency graph is acyclic;
  3. edges name real nodes and statuses come from the vocabulary;
  4. the map's data agrees with the doc's parts table;
  5. the highlighted critical path is a real chain ending at the release, and no longer chain exists.
- **A coupling to the manual.** The user manual cites part ids, and a check in `./verify fast` is red if the manual
  names an id the table no longer holds. So ids are retired as `superseded`, never deleted.

## What we learned keeping it true (the reasons for the design below)
1. **A stale plan hides progress.** Between 2026-10-11 and 2026-10-17 the human made a rebuild decision (horde ADR-223)
   that superseded three parts and answered several open decisions. The map still showed them open, and the human read
   it as "nothing crossed off". One refresh (horde PR 1118) moved 4 parts and closed 4 decisions outright, plus half of 2 more, all with citations.
   The freshness line was honest, but nothing made the staleness *visible* or *costly*.
2. **A refresher agent will "close" things on its own reading.** In the 2026-10-17 refresh, an agent removed an open
   decision because it judged the new spec absorbed it, with no record saying so. The lead caught it and had it
   restored as open with the reading attached as a proposal. **Rule worth enforcing: no status change without a cited
   record.**
3. **The same agent was right several times where the lead was wrong.** The lead's brief asserted that two parts were
   answered, and the records did not support it. Checking against the records, not the brief, is the point.
4. **Two hand-written copies drift.** The map's DATA block and the doc's table are both written by hand. Self-check 4
   keeps them equal, but only when someone runs it.
5. **The checks run only in a browser.** Checks 1 and 4 fetch files over HTTP, so they need the page served. No
   headless runner exists, so `./verify` never runs them. The refresh agent ran them through `node:vm` by hand.
6. **The critical path is a judgment** that check 5 verifies but does not compute, and ties are common: 12 tied chains
   after the refresh.
7. **Code is missing.** The map knows rows and ADRs, not code. horde now has a separate, gated, declared structure of
   its new engine (`engine2/structure/engine-structure.json`, format `horde.engine-structure/1`), which loupe draws
   with no inference. loupe's crawler can also map code. Neither is wired to the plan.

## The proposal: a kit artifact every repo builds against its own records
- **One source of truth for the plan's structure:** e.g. `plan/parts.json`, a schema autonomous owns. Each part has:
  - `id`, `title`, `status` (a closed vocabulary that includes `superseded`), `rows`, `adrs`, `needs`, `release`;
  - optional `code` (paths or loupe nodes) and `notes`.

  The doc's table and the map's data are **generated** from it, never hand-copied, which removes lesson 4.
- **A headless Layer-0 check in `./verify fast`** (no browser, no model):
  - every cited row and ADR exists;
  - the graph is acyclic;
  - the vocabulary holds;
  - generated files match their source;
  - the critical path is **computed** (longest chain to the release, ties reported), not hand-drawn.

  Each check has a must-fail control.
- **A visible freshness rule.** The plan names the ROADMAP and DECISIONS commits it was verified against. The check
  reports how many rows and ADRs have landed since, and the map shows that count on screen. Whether a threshold turns
  it red is your design question.
- **A status-change rule:** a part's status or a decision's closure changes only with a cited row or ADR. An agent's
  reading goes in as a proposal, never as a closure (lesson 2).
- **An optional code layer.** A part may name the code it governs, through loupe's crawl, a declared structure in
  loupe's adapter format, or plain paths. The map can then say "part X: N files, last touched at commit Y", and a
  loupe conformance pass can flag code that no part claims.
- **Spin-up and retrofit.** `/spinup` scaffolds an empty `parts.json`, the generator and the check from the survey's
  answers. `/retrofit` builds a first draft from an existing ROADMAP and DECISIONS, marked as a draft for the human.

## What horde offers
- **The reference instance:** horde's two files and their five checks, as of PR 1118. Use them as a fixture.
- **First consumer:** horde will migrate to the kit's version once it exists, and report what broke.
- **Contract tests proposed:**
  - horde's current plan (53 parts, 59 open decisions) converts to `parts.json` with no loss, and regenerates its own
    table byte-for-byte;
  - a planted row id that does not exist reads red;
  - a planted cycle reads red;
  - a hand-edited generated table reads red;
  - a part status changed with no citation reads red.

## Questions for autonomous
1. Do you want this in the kit (and in `/spinup` and `/retrofit`), or as a separate skill a repo opts into?
2. Should the source be JSON, or a table in the plan's markdown that the generator parses? horde leans JSON: a schema,
   and one canonical reading.
3. The freshness rule: report only, or red past a threshold? If red, measured in rows or ADRs since the last
   verification, or in days?
4. The code layer: loupe first, or plain paths first with loupe as an adapter? (loupe's own Q-015 is adding a
   structure layer to its schema; you may want to coordinate with it.)

**Ball: autonomous.**
