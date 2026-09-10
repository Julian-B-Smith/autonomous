# Repo visibility & licensing — roster policy and decisions

> Records which repos are public vs private and why, plus a suggested license
> stance per category. Decision of record: DECISIONS #21. Visibility is
> tracked live by the sweep (`sweep.py list --visibility`, a network gh
> lookup) — this file is the *policy + rationale*, the sweep is the *current
> state*. When the two disagree, the sweep is truth; update this file.
>
> *Not legal advice.* For anything you would actually patent or sell, consult
> an IP attorney — especially the international-novelty point below.

## The governing asymmetry
Private is reversible; disclosure is not. Un-publishing does not un-disclose
(already-public code was cloneable/archived, and any patent clock already
started). So: for anything not already committed to open-sourcing, staying
public spends optionality you can't recover — private now preserves it.

Patent note (jurisdictional): most countries outside the US require *absolute
novelty* — any public disclosure before filing destroys patentability. The US
grants a 1-year grace period but the clock starts at disclosure. If a device
might be worth patenting, public code forecloses the strongest options.

## Policy by category

- **Infrastructure & methodology → PUBLIC (exposure is an asset).**
  Open-sourcing is the differentiator; these are portfolio/credibility for the
  consulting angle. autonomous, agent-knowledge-loop, claude-code-best-practices,
  the-governor, distillery, dispatch, ai-integration-methodology, life-os-app,
  substack2pdf, portolan-ingest, attest, visual-history.
  *Suggested license:* permissive (MIT/Apache-2.0) — invite use, build reputation.

- **Novel music/audio devices → PRIVATE by default (preserve optionality).**
  Real novel work with plausible productization/patent upside and undecided
  intent. The synthesis engines, the sequencer, the analysis cores.
  *Suggested license at eventual release:* source-available/non-commercial
  (e.g. PolyForm Noncommercial) or all-rights-reserved until a commercial
  decision — NOT permissive, or you hand competitors the product.
  *Kept PUBLIC deliberately (resume showcase, human decision 2026-07-13):*
  **Tonality**, **Audiology**.

- **Client-confidential → PRIVATE (already correct).**
  harness-grader (leather-harness client designs — verified PRIVATE 2026-07-13,
  after an earlier mislabel), lochlin-smith-designs, life-os-data(-mirror),
  monarch, mind.lathe, Portolan, babysynth.

- **Utilities / low-stakes → either; public is fine.** Nothing to protect.

## Licensing decisions (2026-07-13)

- **Public showcase (Tonality, Audiology): PolyForm Noncommercial 1.0.0.**
  `LICENSE.md` grants the public non-commercial use; commercial rights are
  reserved to the copyright holder (Julian Smith / Julian-B-Smith) by default.
  Source-available, resume-friendly, commercial-protected. Canonical text:
  polyformproject.org/licenses/noncommercial/1.0.0.
- **Private commercial candidates: intentionally UNLICENSED (all rights
  reserved) until productization.** A license *grants* rights; you do not grant
  rights on something you may sell. A private repo with no license is
  all-rights-reserved by default — maximum optionality. Adding even a
  non-commercial license now would hand the public NC rights that could
  undercut a future paid product or conflict with a chosen commercial model.
  So: no LICENSE file on the private music repos; pick the license *at* the
  productization decision, per product. (User decision — they may become
  commercial products.)
- Rule of thumb: **public → license it** (a public repo with no license still
  reads as all-rights-reserved, which confuses would-be users); **private and
  possibly-commercial → leave unlicensed** until you decide the business model.

## Music devices recommended PRIVATE (the actionable list)
Excludes Tonality + Audiology (kept public per human decision). Each is a
synthesis engine, sequencer, or audio device with productization potential.
Run per repo: `gh repo edit <name> --visibility private`.

- Orrery — multi-engine generative sequencer (the flagship)
- tonality-core — native C++ Tonality engine (the productization-grade core;
  judgment call given Tonality itself is public — but this is the valuable IP)
- Auricle — glitch grain manipulator
- morphos — VST3 morphogenetic-synthesis synthesizer
- morphogen — the morphogenetic-synthesis engine behind morphos
- tensegrity — variational sound-synthesis engine
- sympath — sympathetic resonance on an endless Tonnetz
- limen — coupled Hopf-oscillator voice
- catena — dispersion-engineered string synthesis
- curvature — Riemannian-manifold synthesis engine
- plexus — graph-Laplacian modal synthesis
- edgewise — topologically-protected-edge-mode struck instrument
- tribos — thermal polyphonic physical-modeling synth
- Terrane — path-dependent adaptive instrument
- Place — geographic wave-terrain wavetable generator
- Wend — (audio project; trace-compatible with Orrery)
- wavetable-generator — wavetable synthesis utility/engine

**Verify before deciding (unclear classification):** Automata, grust — check
whether they are audio/novel before choosing; not on the list above.
