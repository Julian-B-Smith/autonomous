# handbook/ — the human operator's manual, and its audit

Two living documents, authored by the human, that turn the broader philosophy
behind this framework into load-bearing instructions:

| File | What | Audience |
|---|---|---|
| [NAVIGATOR.md](NAVIGATOR.md) | **Machine Horticulture — Navigator's Handbook.** The fourteen principles, the three nested loops, the operating procedures (starting a task, watching a run, gate decisions, failure, selection, the weekly review), anti-patterns, glossary. | The human running an agentic development process without reading most of the code. |
| [GAP-SCHEMATIC.md](GAP-SCHEMATIC.md) | **Autonomous — Gap Integration Schematic.** Maps each principle to what this repo has built, designs the four missing components (variety ledger, uncertainty channel, algedonic channel, population selection), and sequences them. | Whoever builds the gaps; the resident auditing the claims. |

## Rules for this directory

- **Markdown is the source.** Edit the `.md`; the PDFs under `exports/` are
  renderings, re-exported when the source changes and dated in their
  filename. A PDF newer than its Markdown is a bug.
- **The author's text is the author's.** The resident audits, and records
  findings in the schematic's *Audit* column and in this file — never by
  silently rewriting a claim. Where the audit disagrees with a status, both
  stand side by side until the human rules (Decision 74: rulings arrive as
  polls).
- **Audited against the repo, not the other way round.** A component is
  "built" when the tree shows it working, never when a document says so —
  the same rule the kit's currency checker follows (README §1a, LIBRARY
  L0014).
- **Cadence.** Re-audited at every monthly landscape audit, and whenever a
  decision lands that changes a row (the decision's number goes in the Audit
  column). Vocabulary drift between these documents and `doctrine/` is a
  finding, not a style choice.

## Audit of record — 2026-09-20 (edition 2026-09-20, kit 2.6.3, Decision 75)

Full row-by-row notes are in the schematic's *Audit* column. The findings that
change a reader's picture:

1. **Algedonic channel (principle 12) is claimed missing but partly exists.**
   `governor/algedonic.py` has run weekly since Decision 47: deterministic,
   remote-visible fleet pain (red default branch, identity leak in a public
   tree) that bypasses every local sweep and notifies the human. What is
   missing is the *run-level* alarm the schematic designs (leash breach,
   verifier tamper, budget overrun). Gap 3 therefore extends a working channel
   rather than creating one.
2. **History is a tree (principle 7) is claimed adopted but is not in the
   repo.** No tenet, decision, or design section states it; git branches,
   append-only DECISIONS, and "supersede, don't erase" are the nearest
   practice. It needs the Phase 0 doctrine patch the schematic already
   schedules; until then the status is *held by the author*.
3. **Three rows understate what exists.** Per-capability contracts and a
   failure-surface rule exist at the repo seam (INTEGRATIONS: `INTEGRATION.md`,
   `contract/`, "degrade visibly"); the session loop has a comparator
   (`/wakeup` distrusts a verify result from another commit); the practised
   diagnostic protocol is "plant a known-bad and watch the detector fire"
   (LIBRARY L0002, L0014), which is principle 10 applied to detectors.
4. **Vocabulary to reconcile with `doctrine/`.** *Digest* in the handbook
   means a weekly distillery product; today the digest is dispatch's *daily*
   one and distillery emits no weekly summary. *Doctrine changes only at the
   week loop* is the aspiration; in practice doctrine changes land by PR
   whenever ratified (Decision 73 landed mid-week) and the monthly landscape
   audit is the slow loop. *Containment layer*, *leash*, *unknowns map*, and
   *population* have no counterpart in `doctrine/` yet; they enter with the
   gardener brief's response (`briefs/2026-09-19-gardener-loop-and-fence.md`).
5. **Author attribution.** The exported PDFs carry a placeholder author badge
   from the rendering tool; the Markdown editions name the author. Re-export
   from the source when convenient.

Corrected coverage: **nine principles embodied or briefed, one partly live
(12), four missing (2, 11, 14, and 7 pending its doctrine patch)**. Nothing in
the target architecture or the phase order changes as a result.

## Relationship to the rest of the repo

- `doctrine/DOCTRINE.md` is what every session loads; the handbook is what the
  human reads. When they disagree, the doctrine is the gate and the handbook
  is the proposal — reconcile through a decision, never by editing either
  alone.
- The schematic's phases are candidates for `ROADMAP.md`; they enter it only
  when the gardener brief's response is ratified, so that one plan governs.
- `DESIGN.md` §4 (the governor) and the schematic overlap on the algedonic
  channel and the watchdog; the schematic is the human-facing statement, the
  design is the build spec.
