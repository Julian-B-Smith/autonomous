# kit/security/ — security by enforcement

The fleet's method for software security. Adopted from horde's brief
hypersaw-005 (2026-10-05) under the human's rulings in **Decision 85**. Leak
and secrets hygiene stays in `governor/REPO-HYGIENE.md`; this covers what that
does not: exploitable defects in code we ship, the supply chain, and the agent
toolchain itself.

**Status: method adopted; kit deliverables not yet built** (ROADMAP Phase S).
horde runs the method first, as its B446 P0, and reports what it gets wrong.

## The method, in order

1. **Inventory the trust boundaries first.** Every place untrusted data
   enters and what it can reach: files and presets, host- or OS-supplied
   values, GUI text, network input, inter-process messages, and mailbox
   filings and tool output read by agents. A generic vulnerability list
   describes other people's bugs; guards built from it alone cover the list,
   not the product.
2. **Research per surface, from verified sources.** Every catalogue entry
   cites a primary source a reader actually opened (CWE, NVD, a vendor
   advisory, a paper). AI research fabricates plausible CVE numbers and
   page summarisers misreport; unverified entries are marked and never relied on.
3. **A versioned catalogue and a coverage gate.** Per project,
   `SECURITY-CATALOGUE` entries record `id`, `cwe`, `source` (verified /
   recalled), `surfaces`, `guard`, `control` (the guard's must-fail plant),
   `status` (guarded / accepted-with-expiry / open).
   `security_coverage_check` fails when any vulnerability × surface cell is
   neither guarded nor accepted. **Scope (Decision 85):** required for repos
   that ship binaries to others or parse untrusted input; opt-in elsewhere;
   enters observe-first like every gate (Decision 84).
4. **Guards, strongest first, each proven to fire.** (1) safe by
   construction — the defect cannot be written (one bounded reader, one path
   API), with a cheap check banning the way around it; (2) dynamic — fuzzing
   plus sanitizers, the only layer that finds bugs on no list; (3) static —
   lint, CodeQL, Semgrep, banned-API greps; (4) review. Every guard ships with
   a must-fail control, re-run on a schedule as a **guard drill**, because a
   guard can rot and stay green.
5. **Continuous fuzzing.** Harnesses and corpora in the repo; short runs in
   CI, longer on a schedule; every crash becomes a corpus entry and a regression test.
6. **Prompt guidance is a measured hint, never the control.** Lean root
   files point to a per-pack `SECURE-PATTERNS.md`; short banners sit at each
   trust boundary in the code; a Layer-E eval measures whether guidance
   changes agent output.
7. **Pentests: independent, event-triggered, closed-loop.** **Floor
   (Decision 85):** an AI red team counts as independent only with a different
   model family AND prompt lineage from the author; a human expert or a
   public disclosure path (`SECURITY.md`) before any binary ships to
   strangers. Triggered by a new parser or surface, a dependency bump, every
   release; a quarterly floor. Every finding becomes a catalogue entry and a
   regression guard.
8. **The axes a code frame misses.** Supply chain (hash-pinned deps, actions
   pinned to SHAs, least-privilege workflow permissions, Dependabot,
   Scorecard, SBOM, signed and notarized releases); repository settings
   (secret scanning with push protection, branch protection — applied by the
   human from a kit checklist); the agent toolchain (prompt injection through
   mailbox filings and tool output; command limits enforced by hooks and
   permissions, not prose; no security verdict by AI alone); response
   (`SECURITY.md`, a patch-release runbook, a user update path); risk
   acceptance in DECISIONS **with an expiry date**.

## Domain packs

`packs/<domain>/` (Decision 85: packs live here, versioned with the kit): a
catalogue seed, guard implementations and secure patterns for one kind of
project. A project instantiates a pack against its own surface inventory. The
audit loop carries a finding in one project up to its pack, so every sibling
of that kind inherits it. First pack: [`packs/audio-plugins/`](packs/audio-plugins/).

## Deliverables (Phase S — not yet built)

catalogue schema · `security_coverage_check` · guard-drill harness ·
`SECURITY.md` and `SECURE-PATTERNS.md` templates · supply-chain and
repository-settings checklists · pentest runbook.
