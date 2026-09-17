---
description: Scaffold a new project via the ecosystem spin-up procedure (survey → manifest → harness)
---

Spin up a new project: $ARGUMENTS

(Arguments — both optional: a target directory and a one-line description of
what the project is. **If no directory is given, the target is the current
working directory** — the normal case when the session was opened inside the
new folder. Before scaffolding into the cwd, confirm it is the intended
fresh project root: empty or near-empty, not inside an existing project or
one of the ecosystem repos; if in doubt, ask. If the description is missing,
ask for it — it seeds the survey's first question.)

**Composite?** If the arguments include `--composite`, or the project is one
deployable made of several modules behind a shared seam (a plugin hosting
engines, an app with plugins, a monorepo built together), follow
`ONBOARDING.md` → Part 2 → "Composite projects" instead (the five moves:
promote the seam to the contract; root charter + per-module sub-charters; a
`composite` manifest block with a `modules_dir`; record doc precedence; rung
2→3 by default). Worked reference: `~/Documents/Claude/synthetic-worlds/Orrery`.
Otherwise, the standard procedure:

Follow the canonical procedure at
`~/Documents/Claude/autonomous/ONBOARDING.md` → Part 2 → "Replicating the
structure for a NEW project (until kit v2 ships)" — all eight steps, exactly.
Three behaviors are non-negotiable:

1. **Survey first, scaffold second.** Conduct the 9-question spin-up survey
   (`autonomous/kit/README.md`) interactively with the human; write
   `project.manifest.json` before creating anything else. Never skip or
   backfill the survey.
   **Every question is a poll** (AskUserQuestion, one per question, options
   with what each implies) — canonical wording `kit/prompts/_human-gates.md`.
2. **The architecture rung is asked, never defaulted** (doctrine: right-size
   the agent architecture). Present the three-rung menu with what earns
   each; single-thread is the normal answer, not the fallback.
3. **Ratification is a poll, not a report.** When the scaffold is green,
   put the manifest to the human as ONE AskUserQuestion — the manifest
   summarized in the question; options Ratify / Ratify with changes / Not
   yet. The manifest stays `provisional` until that poll returns Ratify.

Gotcha: the Write tool does not set the exec bit — `chmod +x verify
.claude/hooks/*.sh` before running the oracle, or `./verify` fails
`permission denied`.

Finish by reporting: the ratification poll's result, the green
`./verify fast` output, and (if ecosystem-facing) which briefs were filed
and whether the project should be registered in autonomous's ecosystem
tracks. Reference implementations: `~/Documents/Claude/distillery/`,
`~/Documents/Claude/dispatch/`.

## Gates are vendored, never copied (kit >= 2.4.0)

`harness/verify` is a THIN template: it contains no gate code. After copying it
to `./verify`, run

    python3 ~/Documents/Claude/autonomous/kit/kit_sync.py <new repo>

which writes `.kit/kit-gates.sh` + `.kit/MANIFEST`, sha256-pinned and checked by
`kit_integrity` on every run. Never paste gate code into `./verify`: that is
what produced ten drifted `leak_gate` variants across the fleet, nine of them
missing the Windows identity pattern while declaring a kit_version that
promised it (Decision 65).
