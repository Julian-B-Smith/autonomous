# INDEX — pointers into LIBRARY.md (autonomous)

One line per entry; the LIBRARY is the source of truth. INDEX↔LIBRARY
consistency is this loop's atomic-write duty (contract §Validation stance).

- L0001 — sshd hardening on cloud images: drop-ins win; assert with `sshd -T` — canonical · origin life-os-app#L0002
- L0002 — a gate never fired against known-bad is not a gate; `git grep -E` has no `\s \d \b` — canonical
- L0003 — MCP SDK 2.0 moved `mcp.server.fastmcp`; try-2.x-fall-back-1.x — shim safe only on `@tool`/`.run()` — candidate
- L0004 — consumer-authored contract tests catch the dialect the provider does not write — candidate
- L0005 — a detector shares assumptions with what it measures; a must-read-zero control needs a paired corruption — canonical
- L0018 — a detector keyed on the current machine's identity or path conventions is a different detector on every machine — candidate
- L0017 — a control proves a detector can see, not that it looked everywhere; testimony outranks a clean scan — canonical
- L0016 — an action list from an eventually-consistent index names finished work and hides pending work — canonical
- L0015 — an eventually-consistent index is a cache; an action list must read the source — canonical
- L0014 — four checks asked a question next to the one that mattered: exists vs reachable-by-its-consumer — canonical
- L0013 — a format-on-write hook rewrites vendored bytes and breaks the checksum, silently — canonical
- L0012 — an optional-dependency fallback needs CI without the dependency, or it rots unseen — canonical
- L0011 — a pinned version in a template ages on someone else's clock; prove a major bump on a real run — canonical
- L0010 — an artifact two independent readers misread is defective, however defensible — canonical
- L0009 — a tool writing into a foreign tree sweeps its own orphans on ENTRY; `finally` cannot — canonical
- L0008 — a green oracle chained by && still does not cover `git add -A` in a mailbox repo — canonical
- L0007 — a firing gate is worthless if the operator proceeds past its exit code; chain commit TO verify with && — canonical
- L0006 — a probe that runs the target's oracle inherits its side effects; "untouched" includes .harness/ — canonical
