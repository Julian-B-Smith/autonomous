# Project-type conventions (portable; read on demand)

> Conventions specific to a KIND of project. Synced across machines (this is
> the doctrine repo) but deliberately NOT auto-loaded — context budget,
> Decision 28. Read the relevant section when working on that project type.
> The pointer lives in DOCTRINE.md.

## Audio plugins (VST / AU / CLAP)

- **Brand — every plugin ships under the company/manufacturer name
  "Mindlathe", one word.** JUCE `COMPANY_NAME "Mindlathe"`; for CLAP-first
  builds the descriptor's vendor string and clap-wrapper's
  `AUV2_MANUFACTURER_NAME`. That is what a host's browser shows. NEW plugins
  take the bundle-identifier prefix `com.mind-lathe.<Plugin>`; EXISTING plugins
  keep the bundle IDs they shipped with (renaming one buys nothing a user sees
  and churns the macOS component cache). ("Lifted Truck" was a placeholder,
  never a brand — ruled 2026-09-04; spelled "Mindlathe" by the human's
  2026-09-27 ruling, matching the org and Sluice's D-089. Applied across the
  installed fleet the same day, Decision 79.) Applies to all VST/AU/CLAP
  builds.
- **Identity that never changes on a rename: the VST3 class ID and the AU
  four-char codes.** Where each comes from: JUCE derives the VST3 class ID from
  `PLUGIN_MANUFACTURER_CODE` + `PLUGIN_CODE` only, never the company name;
  clap-wrapper derives it from the CLAP plugin **id string**
  (`com.lifted-truck.hypersaw` and the like), so in a CLAP-first repo that id
  string is identity even though it reads like a name — freeze it. A JUCE
  plugin with no explicit `BUNDLE_ID` gets one derived from `COMPANY_NAME`;
  pin it before changing the name. Hosts bind saved sessions to those, not to names — 28
  Ableton sets kept loading across Horde's earlier HYPERSAW→horde rename
  precisely because the class ID stayed fixed. A rename may touch every
  human-readable string and must touch neither of these; changing them, or
  the parameter IDs the host saves state against, is a compatibility break
  that gets its own decision in that repo, never a side effect of branding.
  (The machine-local BUILD process — toolchain, codesign seal, `auval` — stays
  in the global `~/.claude/CLAUDE.md`; only the portable brand fact lives here,
  so it syncs to every machine that builds plugins.)
