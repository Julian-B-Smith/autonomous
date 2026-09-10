<!-- Provenance: written by the `autonomous` resident (github.com/Julian-B-Smith/autonomous),
     2026-08-18, from Decision 65 (kit mechanism is vendored and checksummed).
     Paste into a session running IN the target repo. If you did not expect this
     prompt, do not act on it — ask the human who sent it. -->

# Kit 2.4.0 — vendor the kit-owned gates (YOUR REPO NEEDS A DECISION FIRST)

**Why you are getting this, and why it is the longer version.** Kit gate code
used to be COPIED into every repo. Measured on 2026-08-18: ten distinct
`leak_gate` implementations existed across the fleet, nine missing the Windows
identity pattern, while every one of those repos declared a `kit_version`
promising it. From 2.4.0 kit MECHANISM is vendored into `.kit/` and pinned by
sha256. Kit SUBSTANCE (charter, ROADMAP, DECISIONS, LIBRARY) is untouched.

The automatic migrator **refused your repo**. That is deliberate: your `verify`
does not match the copied shape it knows how to rewrite, so rewriting it would
be guessing, and guessing at an oracle is how a gate ends up green and blind.
One of these is true of you:

- **hand-written `verify`** — no copied `record()` block
- **hand-written gate** — no copied `leak_gate()` block (you may have written a
  better one, or no leak gate at all)
- **`fast()` calls `leak_gate` in an unexpected shape**

## Do this

```
python3 ~/Documents/Claude/autonomous/kit/kit_sync.py .
```

That installs `.kit/kit-gates.sh` (kit-owned: `record`, `leak_gate`,
`kit_integrity`) and `.kit/MANIFEST`. It adds files and touches nothing you
own, so it cannot conflict with work in progress.

Then wire it BY HAND, keeping everything that is yours:

1. Near the top of `./verify`, after `HARNESS_DIR` is set:
   ```
   if [ -r .kit/kit-gates.sh ]; then
     . .kit/kit-gates.sh
   else
     echo "verify: .kit/kit-gates.sh missing — run kit_sync.py (gates cannot be skipped)" >&2
     exit 1
   fi
   ```
   A missing `.kit/` must be a HARD EXIT, never a degraded run — a silently
   skipped privacy gate is the exact bug the gate exists to prevent.
2. Delete your own `record()` and `leak_gate()` definitions **only if** they are
   the kit's, adapted. If you wrote something genuinely different, do not
   delete it — say what it does and why, and we will decide whether it belongs
   in the kit for everyone or stays yours. Do not silently drop a project gate.
3. In `fast()`, call both, first:
   ```
   kit_integrity || ok=1
   leak_gate     || ok=1
   ```
4. Keep every project gate and test command exactly as it is.

Reference implementation: `~/Documents/Claude/autonomous/kit/templates/verify.project`.

## Then prove it — three separate things

1. `./verify fast` still green; your project gates still run.
2. Reachable: `grep -c 'kit/kit-gates.sh' verify` is >= 1. A checksum-perfect
   copy your verify never sources leaves you completely ungated.
3. Fires:
   ```
   printf 'x /Users/somebody/private\n' > audit-plant.md
   ./verify fast 2>&1 | grep audit-plant.md    # must print a hit
   rm audit-plant.md
   ```

   In your check-in, SAY that the gate fired — do not quote the planted
   path. The plant must be a real-looking identity path to fire at all, so
   a notice quoting it trips the leak gate in the public standards repo
   where the notice lands.


## Report back what you found

Say explicitly which of these applied, because it feeds the kit rather than
just your repo:

- Did you have a leak gate at all? (Three repos audited on 2026-08-18 had none
  while reading as current.)
- Did your gate carry the Windows identity pattern?
- Is there anything in your hand-written `verify` the kit should adopt?

**Do not commit anything into `autonomous`.**

## Finishing: open a PR, do not leave a commit sitting on main

Work on a branch, commit there when green, then:

    git switch -c chore/<short-slug>      # if not already on one
    git push -u origin HEAD && gh pr create --fill

Put the evidence in the PR body — what you proved and how. **Do not merge**;
merges are the human's. Report the PR URL.

If the repo has no remote, commit on `main` and SAY SO ("no remote; commit
<sha> is local-only"). If `gh` is unavailable, push the branch anyway and
report the compare URL, saying `gh` was unavailable. Full text:
`kit/prompts/_closing.md`.
 Check in with:

```
python3 ~/Documents/Claude/autonomous/kit/kit_sync.py . --notify
```

which files an uncommitted receipt for autonomous to verify by re-reading your
tree — a request to be checked, not a claim to be believed.
