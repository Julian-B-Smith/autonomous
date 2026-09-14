# Prompt: Integrate a self-improving knowledge loop into this agent

You are being extended with a persistent, self-improving knowledge loop. Your
existing purpose, tools, and instructions remain in force — this adds a meta-layer
on top of them; it does not replace them. Treat this as a one-time setup task.

The loop runs across three files at the project root:
- **CLAUDE.md** — protocol (how you work); read every session.
- **INDEX.md** — a compact map of accumulated knowledge; your retrieval layer.
- **LIBRARY.md** — durable, evidence-backed lessons; your long-term memory.

Work in four phases. **Do NOT write any files until Phase 3.**

## Phase 1 — SURVEY (read-only)
1. Inspect the project root. Report which of CLAUDE.md / INDEX.md / LIBRARY.md
   already exist, and if CLAUDE.md exists, summarize what it currently instructs.
2. Read your own standing instructions / system prompt / role.
3. From that, name the 3–6 categories of knowledge worth accumulating *for an agent
   doing this specific job* — the recurring gotchas, conventions, and hard-won facts
   a future session here would not want to re-derive. These become your retrieval
   tags. Be concrete to this domain; generic buckets ("bugs", "tips") are a smell.

## Phase 2 — PLAN (propose, don't write)
Present a short integration plan:
- Which files you will create vs. modify.
- For an existing CLAUDE.md: exactly where the loop section will be appended. You
  will append a clearly delimited section; you will NOT rewrite or reorder existing
  content.
- Your proposed domain-tuned tag vocabulary from Phase 1.
- Two forks, each with your recommended default and a one-line rationale:
  - (a) candidate lessons **inline** in LIBRARY (tagged `candidate`) vs. in a
    separate **QUARANTINE.md** that only promotes into LIBRARY on review;
  - (b) reflection trigger: **voluntary** (you remember) vs. **enforced**
    (a `/reflect` command or session-end hook).

Pause for confirmation before Phase 3.

## Phase 3 — APPLY (write, idempotently)
On approval:
- If CLAUDE.md exists: insert the PROTOCOL block below between the markers
  `<!-- KNOWLEDGE-LOOP:START -->` and `<!-- KNOWLEDGE-LOOP:END -->`. If those markers
  already exist, replace only what is between them (so re-running is safe). If
  CLAUDE.md does not exist, create it containing your existing role text plus the block.
- Create INDEX.md and LIBRARY.md only if missing.
- Seed LIBRARY with exactly ONE real lesson drawn from this setup session (e.g. a
  true fact you just learned about this project), formatted per the template, and add
  its INDEX pointer. Do not fabricate filler lessons.
- Never modify INDEX without LIBRARY, or vice versa.

## Phase 4 — VERIFY
- Confirm every INDEX id resolves to a LIBRARY anchor and back.
- Restate, in two sentences, how the loop will run on your *next* session, so the
  behavior is legible to the user.

---

## PROTOCOL block (insert verbatim into CLAUDE.md)

<!-- KNOWLEDGE-LOOP:START -->
## Self-Improving Knowledge Loop

Each session: read accumulated knowledge before acting, write distilled knowledge
after. This meta-layer sits on top of my primary role and never overrides it.

### Every session
1. **ORIENT** — Read INDEX.md in full (kept small on purpose). Pull ONLY the matching
   entries from LIBRARY.md into context. Never load all of LIBRARY by default.
2. **ACT** — Do the work, applying retrieved lessons. If a lesson proves wrong,
   correcting it outranks adding a new one.
3. **REFLECT** — Ask: "What did I learn that a future session needs and could not
   cheaply re-derive?" A lesson qualifies only if durable, evidenced (tied to a
   concrete trigger), and non-obvious. If nothing qualifies, write nothing.
4. **WRITE (atomic)** — Append the lesson to LIBRARY.md and a one-line pointer to
   INDEX.md in the same change. New lessons enter as `tier: candidate`; promote to
   `canonical` only when a second occurrence is SHOWN independent — a different
   root cause, not the same shared file, prompt, or tool seen twice; say why in
   the promotion note — or on human review. Recurrence alone never promotes.

### Write gate (anti-poisoning)
This loop feeds its own output back as input, so a wrong lesson, written once, is
retrieved and reinforced forever. Therefore: prefer not writing over writing
unverified; every lesson states what would falsify it; if a retrieved lesson
contradicts present evidence, trust the evidence and demote the lesson.

### Consolidation (periodic)
When LIBRARY exceeds ~30 entries, merge duplicates, delete superseded entries,
promote recurring candidates, tighten tags. Refactor it like code; don't grow it
like a log.

### LIBRARY entry template
`[Lxxxx] <title> | tier | added: YYYY-MM-DD | tags: … | lesson: … | evidence: … | falsifier: … | supersedes: …`
<!-- KNOWLEDGE-LOOP:END -->
