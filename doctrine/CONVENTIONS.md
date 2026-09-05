# Project-type conventions (portable; read on demand)

> Conventions specific to a KIND of project. Synced across machines (this is
> the doctrine repo) but deliberately NOT auto-loaded — context budget,
> Decision 28. Read the relevant section when working on that project type.
> The pointer lives in DOCTRINE.md.

## Audio plugins (VST / AU / CLAP)

- **Brand — every plugin ships under the company/manufacturer name
  "Mind Lathe".** JUCE `COMPANY_NAME "Mind Lathe"`, the AU/VST3 manufacturer
  display field, and the bundle-identifier prefix `com.mind-lathe.<Plugin>`.
  ("Lifted Truck" was a placeholder, never a brand — ruled 2026-09-04 with the
  GitHub account rename; each plugin repo adopts the new name in its next
  session.) Applies to all VST/AU/CLAP builds, forward-going.
- **Identity that never changes on a rename: the VST3 class ID and the AU
  four-char codes.** Hosts bind saved sessions to those, not to names — 28
  Ableton sets kept loading across Horde's earlier HYPERSAW→horde rename
  precisely because the class ID stayed fixed. A rename may touch every
  human-readable string and must touch neither of these; changing them, or
  the parameter IDs the host saves state against, is a compatibility break
  that gets its own decision in that repo, never a side effect of branding.
  (The machine-local BUILD process — toolchain, codesign seal, `auval` — stays
  in the global `~/.claude/CLAUDE.md`; only the portable brand fact lives here,
  so it syncs to every machine that builds plugins.)
