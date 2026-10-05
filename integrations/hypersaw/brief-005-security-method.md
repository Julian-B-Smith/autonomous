---
id: hypersaw-005
from: HYPERSAW
to: autonomous
thread: security-method
status: ratified — method adopted, four rulings; see response-007-security-method.md
ball: HYPERSAW
seq: 1
filed: 2026-10-05
answered_by: response-007-security-method.md
respond-by: 2026-11-02
cites: none
re: a fleet method for software security (vulnerability catalogue, enforced guards, independent pentests), with an audio-plugin domain pack as its first instance
---

> **Origin.** The horde (HYPERSAW) lead session, 2026-10-05. The human opened a security overhaul
> in horde (ROADMAP B446), verbatim: "I've also realized that I haven't nearly enforced enough
> security measures over the life cycle of this build, and we will need to conduct a major security
> overhaul searching for commonly exploitable vulnerabilities and replacing them with secure
> patterns. I'm not an expert in this matter and will need you to guide me to best practices." They
> then asked for the method to live in autonomous for the whole fleet, with audio devices as a
> particularly rigorous instance. This brief is the horde lead's proposal for that method. The
> human may bring their own framing directly; where it differs, theirs governs.

# Brief: a fleet method for software security, plus an audio-plugin domain pack

## 1. The ask

Adopt a **fleet security method** in autonomous: a doctrine tenet, a kit deliverable set, and a
home for **domain packs**. Rule on the design in §3 (adopt, amend or counter-design). horde
volunteers as the first instance, and the audio-plugin pack (§5) as the first pack.

## 2. Why, and what exists today

**What exists.** The fleet's security posture today is leak prevention:
- `governor/REPO-HYGIENE.md` (identity, secrets and binary-metadata scans);
- `leak_gate` in every `./verify`;
- `governor/leak_scan.py` and `monitor.py`.

These are strong for what they cover. Nothing yet covers **exploitable defects in the code we
ship**, the **supply chain** we build from, or **the agent toolchain** itself.

**Why now.** The gap matters more as projects ship:
- Several are about to put binaries on strangers' machines. horde 1.0 freezes its roster on
  2026-10-07, and its FX modules come from sibling projects.
- An audio plugin runs inside the user's DAW, with the DAW's privileges. A crafted preset or
  session file that corrupts memory in our loader is a route into that machine.
- Most of our code is agent-written, so the patterns an agent defaults to become the fleet's
  attack surface.
- Several repos are public, so an attacker can read the code.

**The design constraint.** It comes from existing doctrine. The AI/deterministic boundary, oracle
discipline and "safety by construction, not vigilance" already say how this must work:
- deterministic gates decide;
- AI proposes and judges, but is never the validator;
- guidance that lives only in prompts is the weakest control, not the main one.

## 3. The proposed method (eight parts)

### 3.0 Inventory the attack surface first

Before any vulnerability research, each project writes a **trust-boundary inventory**: every place
untrusted data enters, and what it can reach. Examples:
- files and presets;
- host or OS-supplied values;
- GUI text;
- network input;
- inter-process messages;
- mailbox filings and tool output read by agents.

A generic vulnerability list describes other people's bugs, so guards built from it alone cover
the list, not the product. Concrete case: the audio vulnerability lists the human gathered do not
mention a plugin's embedded web view and its JavaScript bridge. In horde that bridge may be the
second-largest surface (`src/gui/hypersaw_gui_common.h`, `web.bind`).

### 3.1 Research per surface, from verified sources

A research pass (a swarm where the project warrants one) gathers known vulnerability classes for
each surface in the inventory. Every entry needs a **primary source a reader actually opened**: a
CWE entry, a CVE in NVD, a vendor advisory or a paper.
- **AI research fabricates plausible CVE numbers.** horde received a list citing two CVEs the lead
  could not verify.
- **Page summarisers misreport.** Two of horde's recent research lanes caught summarisers inventing
  figures and inverting an ordering rule.

Unverified entries are marked as such and never relied on.

### 3.2 A versioned catalogue and a coverage gate

Findings land in a per-project `SECURITY-CATALOGUE` (YAML or a table). Each entry records:
- `id`, `cwe`, `source` (verified / recalled);
- `surfaces` (from the inventory);
- `guard` (which check covers it) and `control` (that guard's must-fail plant);
- `status` (guarded / accepted-with-expiry / open).

A kit gate (`security_coverage_check`) fails the build when any (vulnerability × surface) cell is
neither guarded nor explicitly accepted. It follows the same wired-or-explained pattern as horde's
`test_table_check`. A gap becomes a red build, not something a person must notice.

### 3.3 Guards, ranked by strength, each proven to fire

Prefer the strongest kind that fits:

1. **Safe by construction.** The vulnerable code cannot be written. Examples:
   - one bounded-reader type that every parser must use, so over-reads are impossible by design;
   - one path-building API (horde already routes every preset name through a single sanitiser,
     `src/gui/preset_store.h` `storeFile`).

   A cheap static check then bans going around the safe type.
2. **Dynamic.** Fuzzing plus sanitizers (AddressSanitizer, UndefinedBehaviorSanitizer,
   ThreadSanitizer; LLVM's RealtimeSanitizer where the toolchain has it). This is the **only layer
   that finds bugs on no list**, so it is the bridge from known to unknown classes.
3. **Static.** Lint rules, CodeQL, Semgrep, banned-API greps.
4. **Review.** Including AI review, under the independence rule in §3.6.

**Every guard ships with a must-fail control**: a planted instance of the vulnerability that turns
it red. Controls re-run on a schedule as **guard drills**, because a guard can quietly rot and stay
green forever. For example, a grep pattern stops matching after a refactor. This is the fleet's
detector-shares-assumption lesson applied to security.

Guards wire into the layers the harness already has:
- PostToolUse hooks for the cheap static checks;
- `./verify fast` for Layer-0 checks;
- CI for sanitizer and fuzz runs;
- the periodic repo audit for drills and catalogue review.

### 3.4 Continuous fuzzing

Fuzz harnesses live in the repo with their corpora:
- short runs in CI on every change;
- longer runs on a schedule;
- every crash becomes a corpus entry and a regression test.

For public repos, Google's OSS-Fuzz (subject to its acceptance criteria) or ClusterFuzzLite, which
runs inside GitHub Actions regardless, gives continuous fuzzing at no cost.

### 3.5 Prompt guidance: lean, placed at the boundary, and measured

Guidance helps agents write safer code the first time, but it is a hint, not a control.
- **Lean root files.** CLAUDE.md files stay lean (context budget). They carry a pointer to an
  on-demand `SECURE-PATTERNS.md` per domain pack, not the patterns themselves.
- **Trust-boundary banners.** The highest-value header is a short banner at each trust boundary in
  the code, for example: `UNTRUSTED INPUT ENTERS HERE: parse only through BoundedReader; see
  SECURE-PATTERNS §2`. That is exactly where an agent needs the reminder.
- **Delegation briefs.** These carry a short secure-patterns block whenever the scope touches a
  boundary.
- **Measured, not assumed.** A Layer-E eval gives agents tasks at a trust boundary in a sandbox and
  scores whether their output passes the guards. It is reported, never blocking, and shows whether
  the guidance actually changes behaviour.

### 3.6 Pentests: independent, event-triggered, closed-loop

- **Independence.** An AI red team of the same lineage, prompt and context as the author is one
  opinion twice (oracle doctrine). Vary the model, the prompt, the tools and the context. Use
  differently sourced static analysers. Eventually add something outside the AI loop: a human
  expert, or a public disclosure path (`SECURITY.md`) that invites reports.
- **Triggers.**
  - A new parser or surface.
  - A dependency bump.
  - Before every release.
  - A calendar cadence as the floor.
- **Closed loop.** Every finding becomes a catalogue entry AND a regression guard with its control,
  just as a bug becomes a regression test. A long run of empty pentests is a signal to change the
  red team's approach, since it may share the code's assumptions.

### 3.7 The axes a code-vulnerability frame misses

- **Supply chain.**
  - Dependencies pinned and verified by hash, including anything fetched at configure time.
  - CI actions pinned to commit SHAs, not tags.
  - Least-privilege workflow `permissions:` by default.
  - Dependabot for actions and dependencies.
  - OpenSSF Scorecard as a measured baseline.
  - An SBOM per release.
  - Signed and notarized release artifacts.
- **Repository settings.** Secret scanning with push protection, branch protection on the default
  branch, and required checks. These are applied by the human; the kit provides the checklist.
- **The agent toolchain.**
  - Prompt injection through mailbox filings, web pages, issues and tool output.
  - Which commands agents with shell access may run, enforced by hooks and permissions, not prose.
  - The rule that no security verdict is made by AI alone.

  The fleet already treats observed content as data. This makes the enforcement explicit.
- **Response.** A disclosure policy (`SECURITY.md`), a patch-release runbook, and a user update
  path. Audio plugins have no auto-update, so this needs real design.
- **Risk acceptance.** Findings that will not be fixed are recorded in DECISIONS with a reason and
  an **expiry date**, after which they are re-examined. Security assumptions rot like any lesson.

### 3.8 Fleet structure: the method, domain packs, and the knowledge loop

- **autonomous holds the method:**
  - the doctrine tenet;
  - the catalogue schema;
  - `security_coverage_check`;
  - the guard-drill harness;
  - the guard-strength ranking;
  - pentest triggers and runbook;
  - templates for `SECURITY.md` and `SECURE-PATTERNS.md`.
- **Domain packs hold the specifics.** Each pack carries a vulnerability catalogue seed, guard
  implementations and secure patterns for one kind of project: audio plugins (§5), later web apps,
  CLIs, and so on.
- **Each project instantiates** a pack against its own surface inventory (§3.0).
- **The existing audit loop carries findings upward.** A pentest finding in one project becomes a
  catalogue entry in its pack and reaches every sibling of that kind. Security becomes a use of
  the knowledge loop the fleet already runs, not a parallel system.

## 4. Metrics (measured, never the gate itself)

- coverage-matrix fill (guarded / accepted / open);
- guard-drill pass rate;
- fuzzing hours and code coverage per harness;
- time from finding to guard;
- findings per pentest, by severity, over time;
- the Layer-E guidance eval score.

## 5. The first domain pack: audio plugins

Proposed seed for the pack's catalogue and guards. Sources are to be verified in the pack's own
research pass (§3.1).

| Surface | Vulnerability class | Proposed guard (strongest first) |
|---|---|---|
| Preset, state and session loading (CLAP/VST3 state chunks, preset files; samples where a product loads them) | Trusting declared lengths, counts or channel numbers: heap and stack overflows (CWE-122/121), out-of-bounds reads (CWE-125) | A bounded-reader type for all parsing; libFuzzer harnesses on every loader under ASan/UBSan; a banned-raw-read check |
| The real-time audio thread | Locks, allocation, I/O or syscalls in `process`: stalls, priority inversion, denial of service | An allocation and lock counter test over a scripted session (preset loads, morphs); RealtimeSanitizer where available; preallocate at `activate` |
| DSP index and integer math | Unclamped host or modulation values reaching table indices: overflow, OOB reads (CWE-190/125) | Clamp at a single boundary choke point; the fuzzer drives extreme parameter values, sample rates and block sizes; UBSan |
| File names and paths | Names used as paths: traversal (CWE-22) | One path API; a ban on string-built paths; fuzz the sanitiser |
| Embedded web-view GUIs | Preset or user text reaching HTML: script injection; a JS→native bridge reachable from injected script | Escape all text; a strict Content-Security-Policy; no remote content; validate every bridge argument; fuzz the bridge |
| Host-supplied values | NaN or infinity, out-of-range parameters, odd sample rates and block sizes | Sanitise at the boundary; fuzz the host-facing API |
| Plugin-format boundaries | State-chunk size limits (hosts can silently drop large chunks); latency and tail changes (a mid-playback change can force a restart); wrapper translation quirks | Size caps with tests; latency as a plugin constant; never signal tail or latency changes from audio paths |
| Distribution | Unsigned or unnotarized binaries; installer tampering | Signing and notarization in the release pipeline; checksums; an SBOM |

**First instance.** horde will run this as its B446 P0:
1. surface inventory;
2. per-surface audit lanes;
3. catalogue;
4. guards with controls.

horde will report what the method got wrong in practice. The audio siblings that ship inside horde
(dynamics, reverb, saturation and the morphable FX network) share horde's attack surface and would
inherit the pack.

## 6. Proposed doctrine tenet (draft wording for autonomous to edit)

> **Security by enforcement.** Inventory every trust boundary before researching vulnerabilities.
> Each known vulnerability class on each surface is either covered by a deterministic guard that
> has been seen to fail on a planted instance, or explicitly accepted with an expiry. Prefer guards
> that make the defect unwritable, then fuzzing and sanitizers, then static checks. Prompt guidance
> is a measured hint, never the control. Pentests are independent of the author, triggered by
> change as well as by the calendar, and every finding becomes a regression guard that travels up
> the knowledge loop.

## 7. Questions for autonomous

1. **Location.** Should the method be a new doctrine tenet plus a `kit/security/` deliverable set,
   or an extension of `governor/REPO-HYGIENE.md` (today's leak-focused security spec)?
2. **Where domain packs live:** in autonomous (`kit/security/packs/<domain>/`), or in a
   group-level scope (for example, the synthetic-worlds parent for audio)?
3. **The gate.** Should `security_coverage_check` be kit-core (every repo, failing closed when the
   catalogue is absent) or opt-in until a project ships binaries?
4. **Pentest cadence.** Is a fleet-wide floor (for example, before each release and quarterly) set
   in doctrine, or per project?
5. **Independence.** What is the fleet's minimum standard for an independent red team? A different
   model family, a different prompt lineage, or a human?

## 8. Offered contract tests

horde will run `security_coverage_check` and the guard-drill harness in its own `./verify` as soon
as autonomous ships them, and report results in this thread. It also offers its first fuzz harness
(state and preset loading) as the pack's reference example once it exists.

`ball: provider`.
