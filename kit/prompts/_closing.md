<!-- CANONICAL closing instruction for any agent-authored prompt that ends in a
     commit. Every prompt and command that tells a session how to finish quotes
     THIS text. Changed 2026-08-18 (Decision 66): sessions used to commit and
     stop, leaving the human to find and push each one by hand across dozens of
     repos — invisible work with no review surface. A PR is visible, reviewable,
     and merges on the human's schedule, which is the part that was always
     theirs. -->

## Finishing: open a PR, do not leave a commit sitting on main

1. Work on a branch, not `main`:
   `git switch -c <kind>/<short-slug>`  (e.g. `chore/kit-vendor-2.4.1`)
2. Commit there when your checks are green.
3. Push the BRANCH and open a PR:
   `git push -u origin HEAD && gh pr create --fill`
   If the harness DENIES the push, the repo predates kit 2.6.1: say so in
   one line and poll the human to adopt the 2.6.1 permissions block — never
   silently hand them the commands (`kit/prompts/_human-gates.md` §2).
   Put the evidence in the PR body — what you proved, and how. The PR is where
   the human reviews; a commit message they have to go looking for is not.
4. **Do not merge.** Merges are the human's, always. Report the PR URL.

**Write the commit message to a file and commit with `-F`, never `-m "..."`.**
A backtick inside a double-quoted `-m` string is a command substitution: the
shell RUNS the text between the backticks and splices its output into your
message. Twice in one week a message that named a file in backticks executed
that name instead (autonomous, 2026-09-01 and 2026-09-03). `-F <file>` passes
the text through untouched; there is no quoting discipline that makes `-m`
safe once the message quotes code.

Three cases where this does not apply, and what to do instead:

- **No remote** (some repos are local-only): commit on `main` and say so
  explicitly in your report — "no remote; commit <sha> is local-only". Do not
  invent a remote.
- **`gh` unavailable or unauthenticated**: push the branch anyway and report
  the compare URL so the human can open the PR in one click. Say that `gh` was
  unavailable rather than silently falling back.
**Order matters when you check in.** `kit_sync.py <repo>` WRITES; `--notify`
only REPORTS and cannot fix what it finds. So: sync, commit, *then* notify —
otherwise you file an accurate receipt describing a tree you have already
fixed everywhere except `.kit/MANIFEST`, which reads like drift to anyone
skimming (vertex, 2026-08-18).

- **You are not a resident of that repo**: you do not commit there at all.
  Writes stay home; file a brief in its mailbox instead.
