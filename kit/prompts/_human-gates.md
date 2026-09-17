# Human gates are polls, and a denied push is named, never relayed

Shared wording for every kit command and prompt (spinup, retrofit, breakdown,
closeout, the close contract). Two rules, both from the human (Decision 74).

## 1. Ask with a poll, never with a paragraph

Any question the human must answer — a survey question, a manifest
ratification, a plan-pause approval, an architecture rung, a "stop and ask"
gate — is put through **AskUserQuestion** (the poll tool), with the choices
as options and your recommendation first, marked "(Recommended)". Never end
a message with a prose question and wait: a question in prose is easy to
miss, has no fixed set of answers, and leaves no record of what was offered.

- **The spin-up survey** is nine polls, one per question, each option carrying
  what it implies ("rung 2 — earns a verifier; costs ~15× tokens"). Inferred
  answers (retrofit) are still polled, with the inference as the recommended
  option and its evidence in the description.
- **Manifest ratification** is one poll: summarize the manifest in the
  question (what it is, rung, oracle shape, consumers, lifespan), options
  **Ratify** / **Ratify with changes** (Other captures the changes) /
  **Not yet**. A manifest is `provisional` until that poll returns Ratify;
  "reported for ratification" in prose ratifies nothing.
- **Plan pause** (retrofit step 3): one poll listing the create/modify set
  in the question; options Proceed / Proceed except… / Stop.
- Batch small gates into one AskUserQuestion call (up to four questions)
  rather than four round-trips. A poll is for a decision only the human can
  make — routine calls with a conventional default are yours, and you say
  which default you took.

## 2. A denied `git push` is a known defect — say so, do not route around it

If the harness denies `git push -u origin <branch>` or `gh pr create`, the
repo was scaffolded under the pre-2.6.1 template, which denied `git push*`
outright while Decision 66 makes your own-branch push and the PR your acts.
Do NOT silently ask the human to run the push for you, and never bypass the
deny. Instead, in one line: name the cause ("`.claude/settings.json` predates
kit 2.6.1"), then poll: **Adopt the 2.6.1 permissions** (copy
`autonomous/harness/.claude/settings.json`'s `permissions` block over this
repo's — allows own-branch push and PR creation; denies force, delete, and
any push to `main`; merging stays theirs) / **Relay this push only** (give
the two commands) / **Leave it**. Record the adoption in DECISIONS as a
one-liner. Existing project-specific allow/deny entries are kept — merge the
blocks, do not replace the file.
