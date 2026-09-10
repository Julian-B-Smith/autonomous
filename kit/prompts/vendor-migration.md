<!-- Provenance: written by the `autonomous` resident (github.com/Julian-B-Smith/autonomous),
     2026-08-18, from Decision 65 (kit mechanism is vendored and checksummed).
     Paste into a session running IN the target repo. If you did not expect this
     prompt, do not act on it — ask the human who sent it. -->

# Kit 2.4.0 — vendor the kit-owned gates (mechanical, ~5 minutes)

**Why you are getting this.** Kit gate code used to be COPIED into every repo.
Measured on 2026-08-18: that produced ten distinct `leak_gate` implementations
across the fleet, nine of them missing the Windows identity pattern — while
every one of those repos declared a `kit_version` promising it. A version was
a claim about a copy, and a copy can lie. From 2.4.0, kit MECHANISM is
vendored into `.kit/` and pinned by sha256; kit SUBSTANCE (charter, ROADMAP,
DECISIONS, LIBRARY) is unaffected and stays yours.

**This is not a retrofit.** No survey, no architecture rung, no plan-then-pause.
Two deterministic commands, then a check.

## Do this

```
python3 ~/Documents/Claude/autonomous/kit/kit_sync.py .
python3 ~/Documents/Claude/autonomous/kit/migrate_to_vendored.py . --apply
./verify fast
```

`kit_sync` writes `.kit/kit-gates.sh` + `.kit/MANIFEST`. `migrate_to_vendored`
removes the KIT-OWNED `record()` and `leak_gate()` definitions from your
`./verify` and replaces them with a `. .kit/kit-gates.sh` source, adding
`kit_integrity` to `fast`. **Your project gates, your test commands, and
everything else in `verify` are untouched** — that code is yours and the
script has no opinion about it.

If `migrate_to_vendored` REFUSES ("needs a human"), stop and say so. It refuses
rather than pattern-matching loosely, and a refusal is information, not a
failure.

## Then verify it actually landed — three separate things

1. `./verify fast` is still green, and your project gates still run.
2. The gate is REACHABLE, not merely present. Carrying a checksum-perfect copy
   your `verify` never sources is the same declared-vs-effective trap in a new
   costume — three repos read `sync: current` while being completely ungated:
   ```
   grep -c 'kit/kit-gates.sh' verify        # must be >= 1
   ```
3. The gate FIRES. Plant a real identity path and require it to be named:
   ```
   printf 'x /Users/somebody/private\n' > audit-plant.md
   ./verify fast 2>&1 | grep audit-plant.md   # must print a hit
   rm audit-plant.md
   ```

   In your check-in, SAY that the gate fired — do not quote the planted
   path. The plant must be a real-looking identity path to fire at all, so
   a notice quoting it trips the leak gate in the public standards repo
   where the notice lands.

   For many of you this is a genuine upgrade: your copied gate did not carry
   the Windows pattern, so `C:\Users\...` went straight through.

## Notes

- **If you have an uncommitted change to `verify` from the 2.3.0 batch, do not
  review it separately.** Migration deletes the block it patched, so it is
  subsumed — the only diff worth reviewing is the migration's.
- `.kit/*` is KIT-OWNED. Do not edit it; `./verify` goes red if you do, by
  design. Update it with `kit_sync.py`, never by hand.
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


## Check in when done

```
python3 ~/Documents/Claude/autonomous/kit/kit_sync.py . --notify
```

That files an uncommitted receipt in autonomous's mailbox carrying your
MANIFEST. It is not a claim that you are done — it is a request that autonomous
re-read your `.kit/` and confirm. It will verify by hash and either close the
receipt or file back exactly what differs. Do not wait on that; you are done
when your own three checks above pass.
