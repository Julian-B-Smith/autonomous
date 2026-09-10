# Research bibliography (dated ledger)

Running, dated record of every research pass and its primary sources. Each
pass appends a dated section; entries are one line each and link the full
report where the source is discussed. The landscape-audit loop (ROADMAP
deferred) consumes and extends this file — its per-topic "last checked" dates
live here.

**Convention:** a source appears under the date it was consulted. Re-consulting
under a later pass gets a new entry (consensus drift is the point of dating).

---

## 2026-07-08 — Promote-up knowledge loops (audit-loop research)

~50 primary sources across LLM-agent memory and human-organization
lessons-learned literatures (Army AAR/CALL, GAO, SRE postmortem culture,
pattern languages, SECI, CoP, Spotify model, golden paths, Tech Radar/ADR;
Generative Agents, ExpeL, AWM, RAPTOR, G-Memory, Agent-KB, H²R, Zep/Graphiti,
LongMemEval; PoisonedRAG, AgentPoison, MINJA, RobustRAG, OWASP ASI06).
Canonical annotated list: `audit-loop-research.md` in
[agent-knowledge-loop](https://github.com/Lifted-Truck/agent-knowledge-loop) *(archived 2026-08-18; now autonomous/loops/audit-loop/)*
(not duplicated here).

## 2026-07-10 — Multi-agent systems survey

Report: [2026-07-10-multiagent-systems-survey.md](2026-07-10-multiagent-systems-survey.md)

**Anthropic first-party:**
- How we built our multi-agent research system — https://www.anthropic.com/engineering/multi-agent-research-system
- Effective context engineering for AI agents — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Effective harnesses for long-running agents — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Harness design for long-running app development — https://www.anthropic.com/engineering/harness-design-long-running-apps (coverage: https://www.infoq.com/news/2026/04/anthropic-three-agent-harness-ai/)
- Claude Code best practices — https://code.claude.com/docs/en/best-practices

**Cognition / the debate:**
- Don't Build Multi-Agents (Walden Yan) — https://cognition.ai/blog/dont-build-multi-agents
- LangChain: How and when to build multi-agent systems — https://blog.langchain.com/how-and-when-to-build-multi-agent-systems/
- Devin independent eval coverage — https://www.theregister.com/2025/01/23/ai_developer_devin_poor_reviews/ · https://futurism.com/first-ai-software-engineer-devin-bungling-tasks
- Devin's 2025 Performance Review — https://cognition.ai/blog/devin-annual-performance-review-2025

**Academic / OSS:**
- MetaGPT — https://arxiv.org/abs/2308.00352
- ChatDev — https://arxiv.org/abs/2307.07924 (failure analysis: https://christophermeiklejohn.com/ai/agents/mas-series/2026/04/26/mas-series-03-wave-one.html)
- CAMEL — https://arxiv.org/abs/2303.17760
- AutoGen — https://arxiv.org/abs/2308.08155
- SWE-agent (ACI) — https://arxiv.org/abs/2405.15793
- OpenHands — https://arxiv.org/html/2511.03690v1
- AgentCoder — https://arxiv.org/abs/2312.13010
- MAST: Why Do Multi-Agent LLM Systems Fail? — https://arxiv.org/abs/2503.13657

**Industry fleets:**
- Factory.ai Code Droid technical report — https://factory.ai/news/code-droid-technical-report
- Sweep (postmortem signals) — https://github.com/sweepai/sweep · https://news.ycombinator.com/item?id=43490121
- Gas Town (Steve Yegge) — https://steve-yegge.medium.com/welcome-to-gas-town-4f25ee16dd04
- Ralph Wiggum loops — https://ghuntley.com/ralph/ · https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md · https://www.theregister.com/2026/01/27/ralph_wiggum_claude_loops/
- Worktree fleet experience — https://www.developersdigest.tech/blog/git-worktrees-claude-code-parallel-agents-guide · https://medium.com/@ooi_yee_fei/parallel-ai-development-with-git-worktrees-f2524afc3e33 · https://addyosmani.com/blog/claude-code-agent-teams/

## 2026-07-10 — Coordination & isolation mechanics

Report: [2026-07-10-coordination-isolation.md](2026-07-10-coordination-isolation.md)

**Isolation & merging:**
- Claude Code worktrees — https://code.claude.com/docs/en/worktrees
- Git worktrees for parallel agents — https://www.augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution · https://www.mindstudio.ai/blog/parallel-ai-coding-agents-git-worktrees
- bors-ng — https://github.com/bors-ng/bors-ng
- Origin of merge queues — https://mergify.com/blog/the-origin-story-of-merge-queues
- Merge Queues Were Built for Humans (Danjou; "green is not coherent") — https://julien.danjou.info/blog/merge-queues-built-for-humans/
- Outgrowing GitHub merge queue — https://trunk.io/blog/outgrowing-github-merge-queue

**Boundaries & contracts:**
- Nx enforce-module-boundaries — https://nx.dev/docs/features/enforce-module-boundaries (approaches compared: https://www.stefanos-lignos.dev/posts/nx-module-boundaries)
- The shared library is a lie — https://dev.to/abdelaaziz_ouakala/the-shared-library-is-a-lie-fixing-your-nx-monorepo-architecture-3mie
- Coordinating multiple Claude Code agents (interface-first) — https://dev.to/alanwest/how-to-coordinate-multiple-claude-code-agents-without-losing-your-mind-1i9f
- Pact / consumer-driven contracts — https://docs.pact.io/ · https://pactflow.io/what-is-consumer-driven-contract-testing/
- Schema-registry contract testing — https://oneuptime.com/blog/post/2026-01-30-schema-registry-contract-testing/view
- Contracts Over Classes — https://medium.com/software-architecture-in-the-age-of-ai/contracts-over-classes-architecting-for-ai-understanding-not-just-developer-comfort-646882ebb93c

**Communication & task ledgers:**
- tick-md (markdown coordination) — https://purplehorizons.io/blog/tick-md-multi-agent-coordination-markdown
- Markdown as agent task format — https://dev.to/battyterm/the-case-for-markdown-as-your-agents-task-format-6mp
- Beads — https://betterstack.com/community/guides/ai/beads-issue-tracker-ai-agents/ · https://ianbull.com/posts/beads/
- LLM blackboard systems — https://arxiv.org/abs/2510.01285 · CodeCRDT https://arxiv.org/pdf/2510.18893

**CI as arbiter:**
- Code Review Is Dead (verification not approval) — https://blog.codacy.com/code-review-is-dead-why-ai-generated-code-needs-verification-not-human-approval
- Quality gates for AI-generated code — https://axiomstudio.ai/blog/quality-gates-for-ai-generated-code-automated-review-and-compliance
- Flaky quarantine — https://trunk.io/flaky-tests · https://flakyguard.com/blog/how-to-quarantine-flaky-tests · https://www.atlassian.com/blog/atlassian-engineering/taming-test-flakiness-how-we-built-a-scalable-tool-to-detect-and-manage-flaky-tests

**Topologies:**
- Team Topologies in the AI era — https://prommer.net/en/tech/guides/team-topologies-ai-era/ · https://prompt-pals.com/blog/team-topology-for-ai-agents
- Conway's law for agentic AI — https://medium.com/@amine.aitelharraj/-3eb5cd3dbcea

## 2026-07-10 — Memory & governance

Report: [2026-07-10-memory-governance.md](2026-07-10-memory-governance.md)

**Memory architectures:**
- MemGPT/Letta — https://lin-guanguo.github.io/llm-memory-research/letta.research/ · survey https://serokell.io/blog/design-patterns-for-long-term-memory-in-llm-powered-architectures
- Generative Agents — https://ar5iv.labs.arxiv.org/html/2304.03442
- Reflexion (failure post-mortems, +11pts) — https://medium.com/@Micheal-Lanham/memory-not-magic-what-agents-actually-remember-between-sessions-c05dadb53dc7
- Voyager (executable skill library) — https://arxiv.org/abs/2305.16291 · https://voyager.minedojo.org/

**Claude Code / context practices:**
- Claude Code memory docs — https://code.claude.com/docs/en/memory · slot-ceiling guide https://skillsplayground.com/guides/claude-code-memory/
- Auto-memory + hooks — https://yuanchang.org/en/posts/claude-code-auto-memory-and-hooks/ · https://medium.com/data-science-collective/claude-code-memory-management-the-complete-guide-2026-b0df6300c4e8
- Context rot (Chroma) — https://www.trychroma.com/research/context-rot · https://particula.tech/blog/chroma-context-rot-long-context-degradation

**Knowledge sharing & failure modes:**
- Agent knowledge-base anatomy — https://www.infoworld.com/article/4091400/anatomy-of-an-ai-agent-knowledge-base.html · https://ai.riera.co.uk/architecture/multi_agent_knowledgeops/
- Docs-as-code freshness — https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2 · https://openai.com/index/harness-engineering/ · https://dev.to/itlackey/building-agent-knowledge-bases-that-actually-scale-23pb
- Memory bloat (13% vs 39%) — https://tianpan.co/blog/2026-04-12-the-forgetting-problem-when-agent-memory-becomes-a-liability · https://arxiv.org/html/2603.11768v1
- Stale facts / poisoning — https://arxiv.org/pdf/2606.01435 · MemoryGraft https://arxiv.org/pdf/2512.16962
- Safety erosion with memory age — https://arxiv.org/html/2605.17830v1

**Governance & halting:**
- Circuit breakers — https://dev.to/waxell/ai-agent-circuit-breakers-the-reliability-pattern-production-teams-are-missing-5bpg · https://fountaincity.tech/resources/blog/ai-agent-cost-circuit-breaker/ · rate-based https://www.baristalabs.io/blog/ai-agent-spend-circuit-breaker
- Loop/no-progress detection — https://docs.bswen.com/blog/2026-03-11-prevent-ai-agent-infinite-loops/ · https://falconer.com/guides/agent-loops/
- Anthropic trustworthy-agents framework — https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents · https://www.anthropic.com/research/trustworthy-agents
- Anthropic measuring agent autonomy — https://www.anthropic.com/research/measuring-agent-autonomy
- OpenAI Practices for Governing Agentic AI — https://openai.com/index/practices-for-governing-agentic-ai-systems/
- DeepMind safely interruptible agents — https://intelligence.org/files/Interruptibility.pdf
- Replit incident — https://fortune.com/2025/07/23/ai-coding-tool-replit-wiped-database-called-it-a-catastrophic-failure/ · https://medium.com/@neerupujari5/inside-the-replit-ai-catastrophe-438e0f63b21c
- Runaway costs — https://www.supra-wall.com/en/learn/ai-agent-runaway-costs · https://www.nexgismo.com/blog/ai-agent-budget-guards-stop-runaway-api-costs · https://devtoolpicks.com/blog/ai-agents-runaway-claude-code-bills-overnight-2026
- GitClear code-quality data — https://www.gitclear.com/ai_assistant_code_quality_2025_research · https://www.gitclear.com/the_ai_code_quality_maintainability_gap
- Agent metrics — https://www.augmentcode.com/tools/autonomous-development-metrics-kpis-that-matter-for-ai-assisted-engineering-teams · https://www.braintrust.dev/articles/ai-agent-evaluation-framework

## 2026-07-11 — Landscape audit (monthly, first run)

Report: [proposals/2026-07-11.proposal.md](proposals/2026-07-11.proposal.md).
Six fan-out agents, each scoped to "what changed since <topic's last-checked
date>" (2026-07-08/07-10). Window was 1–3 days; most sources below predate
the strict window and are recorded because they are not yet cited in
`doctrine/`/`DESIGN.md`/`research/`, not because they are new-this-week.

**Multi-agent coordination:**
- Cognition, "Multi-Agents: What's Actually Working" (follow-up to "Don't
  Build Multi-Agents") — https://cognition.com/blog/multi-agents-working
  (fetch blocked, via search snippets)
- UIUC multi-agent token-multiplier study (4–220× range) — via
  https://www.augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution
  (secondary; primary not located)
- RecursiveMAS (embedding-space agent communication, −34–75% tokens) —
  https://arxiv.org/abs/2604.25917 (via VentureBeat coverage)
- Overstory (worktree-fleet orchestrator, archived 2026-05-28, superseded by
  "Warren") — https://github.com/jayminwest/overstory
- "GasTown and the Two Kinds of Multi-Agent" — https://paddo.dev (commentary
  on Gas Town's operational-roles model)
- "$47K agent loop" postmortem (11-day unbounded live-messaging loop,
  Nov 2025 incident) — forensic writeups on dev.to/clyro.dev, ~Apr–Jun 2026
- Fleet (parallel coding-agent supervisor: Beads/Dolt queue, multi-backend
  coder routing, ask_human MCP, context-pressure termination) —
  https://github.com/sermakarevich/fleet (user-recovered from the audit's
  blocked HN thread; reviewed 2026-07-11 — conductor prior art, see ROADMAP)

**Agent memory & knowledge loops:**
- Claude Code changelog v2.1.204–207 —
  https://code.claude.com/docs/en/changelog (`/doctor` CLAUDE.md-trim check,
  2026-07-09; hook shell-injection hardening, 2026-07-11)
- FARMA: Forged Reasoning Attacks on LLM Agent Memory —
  https://arxiv.org/abs/2607.05029 (~2026-07-06, fetch blocked)
- WhisperBench: Stealthy Memory Injection in Persistent Personal Agents —
  https://arxiv.org/abs/2607.05189 (~2026-07-06, fetch blocked)
- GhostWriter: Memory Poisoning Attacks on LLM Agents —
  https://arxiv.org/abs/2607.06595 (~2026-07-06, fetch blocked)
- AgentPrizm "AgentMemory" product launch (2026-07-09) — market signal only,
  no stable primary URL found

**Governance, halting, and agentic safety:**
- Future of Life Institute, "AI Safety Index — Summer 2026" (2026-07-07) —
  https://futureoflife.org/ai-safety-index-summer-2026/
- Adversa AI, "GuardFall" open-source coding-agent guard bypass
  (2026-06-30) —
  https://thehackernews.com/2026/06/guardfall-exposes-open-source-ai-coding.html
- Claude Code GitHub Action permission-check bypass, patched in
  claude-code-action v1.0.94 (2026-06) —
  https://thehackernews.com/2026/06/claude-code-github-action-flaw-let-one.html
- Google DeepMind, "Securing internal systems against increasingly capable
  and imperfectly aligned AI" / AI Control Roadmap (2026-06-18) —
  https://deepmind.google/blog/securing-the-future-of-ai-agents/
- Sen. Mark Warner, discussion draft "AI AGENT Act" (2026-06-29) —
  https://www.warner.senate.gov/newsroom/press-releases/warner-unveils-discussion-draft-of-legislation-to-create-innovative-market-for-secure-artificial-intelligence-agents/
- Bank of England, agentic-AI trading "kill switch" feasibility study
  (2026-07-01) —
  https://www.resultsense.com/news/2026-07-01-boe-breeden-agentic-ai-kill-switch/
- Sysdig "agentic ransomware" claim (2026-07-02) — unverified, aggregator
  mentions only, no primary reached
- Cloud Security Alliance, "Autonomy Levels Framework" reversibility
  critique (~March 2026, fetch blocked) —
  labs.cloudsecurityalliance.org

**Verification and CI-as-arbiter:**
- METR, "GPT-5.6 Sol pre-deployment evaluation" (2026-06-26) —
  https://metr.org/blog/2026-06-26-gpt-5-6-sol/
- OpenAI, "Why we no longer evaluate against SWE-bench Verified"
  (2026-02-23) —
  https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- "Reward Hacking Benchmark (RHB)" (2026-05-04) —
  https://arxiv.org/abs/2605.02964
- "The Verification Horizon: No Silver Bullet for Coding Agent Rewards"
  (~2026-06) — https://arxiv.org/abs/2606.26300 (fetch blocked)
- "Auditing Reward Hackability in Code RL Training Environments" (~2026-06)
  — https://arxiv.org/abs/2606.16062 (fetch blocked)
- "Understanding Dominant Themes in Reviewing Agentic AI-authored Code"
  (2026-01) — https://arxiv.org/abs/2601.19287
- Code Review Agent Benchmark / c-CRAB (~2026-03) —
  https://arxiv.org/abs/2603.23448
- "Why Are Agentic Pull Requests Merged or Rejected? An Empirical Study"
  (2026-05) — https://arxiv.org/abs/2605.22534
- Trunk.io changelog (incremental flaky-test tooling, no confirmed
  in-window release) — https://trunk.io

**Context engineering and harness design:**
- Claude Code changelog v2.1.206 (2026-07-09) / v2.1.207 (2026-07-11) —
  https://code.claude.com/docs/en/changelog
- Practitioner critique of CLAUDE.md compliance (dev.to, date unconfirmed,
  fetch blocked) — dev.to/minatoplanb

**Open-scope — new categories:**
- OpenAI, GPT-5.6 tiered release (Sol/Terra/Luna) (2026-07-08/09) —
  https://openai.com/index/gpt-5-6/ ,
  https://openai.com/index/previewing-gpt-5-6-sol/ ,
  https://www.cnbc.com/2026/07/08/openai-expanding-gpt-5point6-ai-model-release-ending-government-limits.html
- xAI/Cursor, Grok 4.5 launch (2026-07-08) —
  https://x.ai/news/grok-4-5 , https://cursor.com/blog/grok-4-5 ,
  https://devops.com/spacexais-grok-4-5-undercuts-anthropic-and-openai-on-coding-agent-pricing/
- SpaceX to acquire Cursor/Anysphere, $60B (2026-06-16) —
  https://www.cnbc.com/2026/06/16/spacex-spcx-cursor-acquisition-ipo.html ,
  https://www.forbes.com/sites/sandycarter/2026/06/16/spacex-buys-cursor-in-largest-startup-acquisition-ever-at-60-billion/
- Anthropic, Fable 5 / Mythos 5 launch, export-control shutdown and reversal
  (2026-06-12 through 06-30) —
  https://www.washingtonpost.com/technology/2026/06/30/white-house-drops-export-controls-anthropics-mythos-fable-ai-models/
  , https://www.cnn.com/2026/06/30/tech/anthropic-export-control-ban-lifted-white-house
  , https://www.pbs.org/newshour/show/anthropic-disabled-fable-5-and-mythos-5-after-a-us-security-directive
- Anthropic, "Claude Sonnet 5" (2026-06-30) —
  https://www.anthropic.com/news/claude-sonnet-5
- METR, "Time Horizon 1.1" (2026-01-29/02-21) —
  https://metr.org/blog/2026-1-29-time-horizon-1-1/
- MCP release candidate — stateless protocol layer, Extensions framework
  (2026-07-28 RC) — https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/
- MCP donated to the Agentic AI Foundation / Linux Foundation (2025-12-09) —
  https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation
- Agent identity/payment protocol consolidation (Mastercard Agent Pay, Visa
  Trusted Agent Protocol, Google AP2, MCP-I, W3C Agent Identity Registry) —
  https://www.biometricupdate.com/202603/vendors-race-to-build-identity-stack-for-agentic-ai
  , https://www.w3.org/community/agent-identity/
- Vercel, "eve" durable-workflow agent framework (2026-06-17) —
  https://vercel.com/blog/introducing-eve
- AI-agent liability insurance market forming (Corgi, Testudo, Armilla,
  Klaimee) — https://www.factmr.com/report/ai-agent-liability-insurance-services-market

## 2026-07-13 — Human-AI epistemics (harvested, not web-researched)

Report: [2026-07-13-human-ai-epistemics-delegate52.md](2026-07-13-human-ai-epistemics-delegate52.md).
Source: the user's own methodology document "The Applied Epistemics of AI
Integration" (canonical in the sibling `ai-integration-methodology/` project),
NOT a web pass — so these are attributed to that document, and where it cites a
primary the primary is flagged for verification.

- DELEGATE-52 benchmark (19 models × 52 domains × 20 interactions; invisible
  failure in stronger models; ~80% of loss in sparse catastrophic collapses;
  agentic tools worsened performance ~6pts absent tight scoping) — attributed
  to "2026 Microsoft Research"; **primary URL not located / not verified in
  this harvest — landscape-audit TODO.**
- Illusion of explanatory depth (Rozenblit & Keil lineage) — via the doc.
- Attractor-basin / basin-escape account of LLM generation — the doc's own
  synthesis; mechanism-level, not a single citable paper.
- Seven-mode failure taxonomy (Consensus Trap, XY-at-scale, Competency Erosion,
  Invisible Dependency, Confidence Spiral, Translation Gap, Remediation Cliff)
  — the doc's framework.

## 2026-08-10 — Landscape audit (monthly, second run)

Report: [proposals/2026-08-10.proposal.md](proposals/2026-08-10.proposal.md).
Six fan-out agents (multi-agent coordination, agent memory, governance/
halting/safety, verification/CI-as-arbiter, context engineering/harness
design, open-scope), each scoped to "what changed since 2026-07-11." Genuine
one-month window (vs. the first pass's 1–3 days); substantial movement found.
Nearly all primary domains (arxiv.org, anthropic.com, claude.com, openai.com,
huggingface.co, aisi.gov.uk, metr.org, most security-news outlets,
web.archive.org) were network-level `EGRESS_BLOCKED` this pass — every entry
below is WebSearch-snippet-convergence-sourced (≥2 independent secondary
outlets per claim) unless marked otherwise; see the proposal's "Blocked /
unverified sources" section for the full accounting.

**Multi-agent coordination:**
- Claude Code v2.1.224, native cross-session agent messaging
  (`SendMessage`/`ListAgents`) — https://code.claude.com/docs/en/cross-session-messaging
  , https://www.macrumors.com/2026/08/08/claude-code-adds-cross-session-messaging/
- Claude Code changelog, subagent messaging reliability fixes (v2.1.211,
  v2.1.212) and concurrency/nesting/budget-cap churn (v2.1.217, v2.1.219,
  v2.1.221, v2.1.222) — https://code.claude.com/docs/en/changelog
- Overstory (archived) → Warren (worktree-fleet orchestrator successor) —
  https://github.com/jayminwest/overstory ,
  https://github.com/jayminwest/warren
- "Cheap Code, Costly Judgment" (Purdue case study, governance-conversion
  theory) — arXiv:2607.01087 (fetch blocked, via search snippets)
- ChainSWE (sequential bug-fix degradation benchmark) — arXiv:2607.02606
  (fetch blocked, via search snippets)
- ADE/worktree-tooling market consolidation (Conductor, Vibe Kanban,
  Gastown, Emdash, Claude Squad, Antigravity, Cursor Background Agents) —
  background market confirmation, no single primary

**Agent memory & knowledge loops:**
- FARMA: "Your Agent's Memories Are Not Its Own: Forged Reasoning Attacks on
  LLM Agent Memory and Defenses" — arXiv:2607.05029, 2026-07-06 (confirmed
  this pass; fetch blocked, via convergent search)
- WhisperBench / MemGhost: "When Claws Remember but Do Not Tell: Stealthy
  Memory Injection in Persistent Personal Agents" — arXiv:2607.05189,
  2026-07-06 (confirmed this pass)
- GhostWriter: "When Agents Remember Too Much: Memory Poisoning Attacks on
  Large Language Model Agents" — arXiv:2607.06595, 2026-07-06 (confirmed
  this pass)
- DELEGATE-52 primary resolved: "LLMs Corrupt Your Documents When You
  Delegate," arXiv:2604.15597, Laban/Schnabel/Neville, Microsoft Research,
  2026-04-17 — https://arxiv.org/abs/2604.15597 ,
  code: github.com/microsoft/DELEGATE52 (corrects the "attributed, not
  verified" flag from the 2026-07-13 entry above; figures match this repo's
  harvested description)
- "Reproducing LightMem: Naive RAG Is Just as Good for Memory Management" —
  arXiv:2607.29104, ~2026-07-30 (fetch blocked, via search snippets)
- TencentDB Agent Memory v2.0 (shared team-memory hub, permissioned,
  Claude Code-compatible, MIT) — github.com/TencentCloud/TencentDB-Agent-Memory,
  stable release 2026-08-03
- Metis (Memory Foundation Model) — arXiv:2607.26760, 2026-07-29; Memory
  Decoder at Scale — arXiv:2607.27919, ~late July 2026 (parametric-memory
  watch items, fetch blocked)

**Governance, halting, and agentic safety:**
- OpenAI/Hugging Face sandbox-escape incident (disclosed 2026-07-21,
  widened 2026-08-01) — https://thehackernews.com/2026/07/openai-says-its-own-ai-models-escaped.html
  , https://www.infoq.com/news/2026/08/openai-huggingface-breach/ ,
  https://www.marktechpost.com/2026/07/25/why-the-openai-agent-broke-into-hugging-face-reward-hacking-not-malice-explained-for-engineers/
- Anthropic: 3 companies breached during cyber evals (disclosed 2026-07-30)
  — https://techcrunch.com/2026/07/30/anthropic-says-its-own-ai-models-breached-three-companies-during-security-tests/
  , https://www.cnbc.com/2026/07/30/anthropic-says-claude-gained-unauthorized-access-to-others-systems.html
- Meta: Muse Spark 1.1 breached a third-party company (disclosed
  2026-08-05/06) — https://www.bleepingcomputer.com/news/security/meta-ai-model-hacked-a-company-during-misconfigured-cyber-test/
- Anthropic, "Zero risk isn't the job: a CISO's guide to agentic AI" (Jason
  Clinton, 2026-07-17) — https://claude.com/blog/ciso-guide-to-agentic-ai
  (fetch blocked, via https://getaibook.com/news/anthropics-agentic-security-guide-mandates-ephemeral-vms/)
- "Pacing the Frontier" employee letter (1,200+ signatories across
  OpenAI/Anthropic/DeepMind/Meta, 2026-07-28) — techtimes.com/321905
- AI AGENT Act: discussion draft → S.5051 introduced (Sen. Warner,
  2026-07-21) — https://www.govinfo.gov/bulkdata/BILLSTATUS/119/s/BILLSTATUS-119s5051.xml
  , https://cyberscoop.com/ai-agent-act-senate-draft-bill-mark-warner/
- Singapore MAS confirms agentic AI in binding bank supervisory guidelines
  (2026-08-05) — https://www.techtimes.com/articles/323283/20260806/mas-confirms-agentic-ai-inside-binding-bank-rules-us-eu-fall-behind.htm
- GuardFall follow-up: bypass class remains unpatched as of this window
  [search-synthesis, unverified by direct fetch]
- Cursor "DuneSlide" (CVE-2026-50548/50549, CVSS 9.8) —
  https://www.catonetworks.com/blog/duneslide-two-critical-rce-vulnerabilities/
  ; AWS Kiro (CVE-2026-10591) — disclosed 2026-07-22

**Verification and CI-as-arbiter:**
- UK AISI, "Cheating behaviour in frontier model evaluations" (~2026-07-22)
  — aisi.gov.uk/blog/cheating-behaviour-in-frontier-model-evaluations (fetch
  blocked, via techtimes.com/321292, cuinfosecurity.com/a-32289)
- "Every Model Cheats: Prompt-Level Mitigation of Cheating on Offensive
  Cyber Tasks" (Dreadnode) — arXiv:2607.21763, ~2026-07-21 (fetch blocked)
- "Hardening Agent Benchmarks with Adversarial Hacker-Fixer Loops" —
  arXiv:2606.08960, code: github.com/few-sh/harden-v0 (fetch blocked)
- Microsoft `code-testing-generator` (dotnet/skills, mutation-testing
  agent, MIT, open-sourced 2026-08-06) — marktechpost.com (2026-08-06)
- "Why Are Agentic Pull Requests Merged or Rejected? An Empirical Study" —
  arXiv:2605.22534, ~2026-05 (fetch blocked; pre-window, not yet cited in
  this repo)
- EvalSafetyGap survey — arXiv:2606.30219, v1 2026-06-29 through v4
  2026-07-27 (fetch blocked)
- OpenAI, "Separating signal from noise in coding evaluations" (SWE-bench
  Pro audit, ~30% of 731-task public split found broken) — 2026-07-08
  (boundary-ambiguous vs. last pass's cutoff)
- NIST CAISI, "Cheating on AI Agent Evaluations" — nist.gov/caisi,
  2025-12-02 (pre-window background, not new)

**Context engineering and harness design:**
- Claude Code changelog, v2.1.208 (2026-07-14) through v2.1.226
  (2026-08-08) — https://code.claude.com/docs/en/changelog (hooks
  hardening, memory/CLAUDE.md fixes, subagent cap/nesting changes,
  compaction fixes, `/fork` + `/subtask` redesign, sandbox
  filesystem/network isolation flags, `SendMessage`/`ListAgents`,
  Claude Opus 5 default, auto-mode changes)
- Auto mode becomes default permission mode for Pro/Max/Team, effective
  2026-08-14 (announced 2026-08-07) — https://claude.com/blog/auto-mode-default-in-claude-code
  (fetch blocked, via https://simonwillison.net/2026/Aug/8/auto-mode/ ,
  https://9to5mac.com/2026/08/07/psa-claude-code-enabling-auto-mode-as-default-next-week-anthropic-says/)
- "The Harness Effect: How Orchestration Design Sets the Token Economics of
  Enterprise Agentic AI" — arXiv:2607.06906, 2026-07-08 (fetch blocked)
- "Rethinking the Evaluation of Harness Evolution for Agents" —
  arXiv:2607.12227, 2026-07-14 (fetch blocked)
- "Distributing Security Controls Through Harness Engineering" —
  arXiv:2607.25890, 2026-07-28 (fetch blocked)
- Anthropic, "How Anthropic secures its AI-native software development
  lifecycle" (Jason Clinton, 2026-07-21) — https://claude.com/blog/how-anthropic-secures-its-ai-native-software-development-lifecycle
  (fetch blocked, via https://cycode.com/blog/anthropic-claude-code-security-appsec/)
- "Instruction Adherence in Coding Agent Configuration Files: A Factorial
  Study of Four File-Structure Variables" (Damon McMillan) —
  arXiv:2605.10039, ~2026-05 (fetch blocked; pre-window, not yet cited in
  this repo)
- "Diagnosing and Mitigating Context Rot in Long-horizon Search" —
  arXiv:2606.29718, 2026-06-29 (boundary-ambiguous vs. last pass's cutoff)

**Open-scope — new categories:**
- Claude Opus 5 (2026-07-24) — https://www.anthropic.com/claude/opus (fetch
  blocked; effort-dial non-monotonic on coding tasks per system-card data)
- Gemini 3.6 Flash / 3.5 Flash-Lite / 3.5 Flash Cyber (2026-07-21) —
  https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/
- Kimi K3 open-weight release (2026-07-27, Moonshot AI)
- GPT-5.6 pricing cuts (Luna −80%, Terra −20%, 2026-07-30) — Codex defaults
  to gpt-5.6-sol, MCP 2026-07-28 support — releasebot.io/updates/openai
- MCP spec finalized 2026-07-28 (stateless core, Tasks extension, CIMD
  auth, legacy transport deprecation clock) —
  https://blog.modelcontextprotocol.io/posts/2026-07-28/
- AP2 donated to FIDO Alliance (~May 2026, pre-window, not previously
  logged) — https://www.pymnts.com/artificial-intelligence-2/2026/google-and-mastercard-contribute-agentic-commerce-standards-to-fido-alliance/
- W3C Agent Identity Registry Protocol Community Group (proposed 2026-04)
  — https://www.w3.org/community/agent-identity/
- Meta Muse Spark 1.1 (2026-07-09), native trained delegate/escalate
  orchestration — https://ai.meta.com/blog/introducing-muse-spark-meta-model-api/
- Cognition (Devin) $1B raise at $26B valuation (Aug 2026) —
  https://aibusiness.com/generative-ai/ai-coding-startup-valued-at-26-billion
- AI-liability insurance carve-outs by incumbent carriers —
  https://www.pymnts.com/news/artificial-intelligence/2026/big-insurance-backs-away-from-ai-risk-and-startups-rush-in/

## 2026-08-14 — VSM mapping pass

- Beer, Stafford. *Brain of the Firm* (1972) — S1–S5, recursion; consulted
  via the human's reading + standard secondary literature. Discussed in
  research/2026-08-14-viable-system-model-mapping.md.
- Beer, Stafford. *The Heart of Enterprise* (1979) — variety engineering,
  channel capacity/transduction. Same report.
- Beer, Stafford. *Diagnosing the System for Organizations* (1985) —
  pathology checklist applied to the fleet. Same report.
- Ashby, W. Ross. *An Introduction to Cybernetics* (1956) — Law of Requisite
  Variety; adopted as the standing channel-design test. Same report.

## 2026-09-10 — Landscape audit (monthly, third run)

Report: [proposals/2026-09-10.proposal.md](proposals/2026-09-10.proposal.md).
Six fan-out agents (multi-agent coordination, agent memory, governance/
halting/safety, verification/CI-as-arbiter, context engineering/harness
design, open-scope), each scoped to "what changed since 2026-08-10." Nearly
all primary domains (arxiv.org and every mirror, anthropic.com, claude.com,
openai.com, huggingface.co, aisi.gov.uk, metr.org, most security-news
outlets, web.archive.org) were `EGRESS_BLOCKED` again this pass — every
entry below is WebSearch-snippet-convergence-sourced unless marked otherwise;
see the proposal's "Blocked / unverified sources" section for the full
accounting, including one claim ("Nightingale Collective") explicitly flagged
as unreliable and not to be cited.

**Multi-agent coordination:**
- Claude Code changelog, v2.1.243–v2.1.267 (2026-08-25 to 2026-09-09): dense
  SendMessage/ListAgents/Agent-Teams work — https://code.claude.com/docs/en/changelog
- GitHub issue anthropics/claude-code#90481 (filed 2026-08-28): cross-session
  messaging permanently disabled for a user, survives reboot/reinstall —
  https://github.com/anthropics/claude-code/issues/90481
- Claude Code docs, Agent Teams (interactive-only, file-mailbox delivery) —
  https://code.claude.com/docs/en/agent-teams
- Claude Code docs, Cross-Session Messaging (supports unattended `-p` workers
  via `crossSessionInbound: accept`) — https://code.claude.com/docs/en/cross-session-messaging
- Overstory archived / Warren successor confirmation — https://github.com/jayminwest/os-eco ,
  https://github.com/jayminwest/overstory
- Gas Town architecture (Mayor/Polecats/Refinery/Witness; Beads-backed
  ledger) — https://github.com/gastownhall/gastown ,
  https://www.heise.de/en/background/Full-Control-Gas-Town-Orchestrates-Ten-or-More-Coding-Agents-11178824.html
- Beads v1.3.0-rc.1 (2026-08-28/31), lease-based multi-agent claim system —
  https://github.com/steveyegge/beads/releases
- Mergify, "State of Merge Queues 2026" (AI-PR break-rate data) —
  https://mergify.com/reports/state-of-merge-queues-2026 ,
  https://mergify.com/blog/merge-queues-and-ai-coding-agents
- METR/Redwood independent investigation of the OpenAI/Hugging Face incident
  (~1,200 agents, covert directory-name coordination channel), 2026-08-26 —
  https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/
  (blocked; via https://00011000.com/en/news/metr-redwood-agent-collusion-postmortem ,
  https://www.techtimes.com/articles/325705/20260827/)

**Agent memory & knowledge loops:**
- PoEM: "Proof-of-Execution Memory: Defending LLM Agents Against
  Forged-Reasoning Attacks by Verifying What Actually Happened" —
  arXiv:2608.16032, Aug 2026 — https://arxiv.org/abs/2608.16032
- PipePoison: "Transferable End-to-End Optimization for Indirect Long-Term
  Memory Poisoning in LLM Agents" — arXiv:2609.00523, ~2026-09-01 —
  https://arxiv.org/abs/2609.00523
- InjecMEM (single-interaction, retriever-agnostic memory injection) —
  arXiv:2608.23471, Aug 2026 — https://arxiv.org/abs/2608.23471 ,
  https://openreview.net/forum?id=QVX6hcJ2um
- GovMem: "When Not to Write Memory: Governing False Promotion from
  Correlated Agent Traces" — arXiv:2607.02579, submitted 2026-06-30 —
  https://arxiv.org/abs/2607.02579
- TMA-NM: "Securing LLM-Agent Long-Term Memory Against Poisoning:
  Non-Malleable, Origin-Bound Authority" — arXiv:2606.24322, 2026-06-23 —
  https://arxiv.org/abs/2606.24322
- "Utility Under Attack: Agent Memory Poisoning and the Limits of Content
  Screening and Provenance Ranking" — arXiv:2608.21230, 2026-08-21 —
  https://arxiv.org/abs/2608.21230
- "What Eviction Destroys: A Restore-Counterfactual Audit of Forgetting in
  Agent Memory" — arXiv:2609.08279, ~2026-09-08 —
  https://arxiv.org/abs/2609.08279
- TencentDB Agent Memory v2.0, stable release + Team Memory feature,
  2026-08-03 — https://github.com/TencentCloud/TencentDB-Agent-Memory
- Metis (Memory Foundation Model), latest revision 2026-08-04 —
  https://arxiv.org/abs/2607.26760
- OWASP Top 10 for Agentic Applications, ASI06 "Memory and Context
  Poisoning" — https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/

**Governance, halting, and agentic safety:**
- Anthropic, "An alignment assessment of recent cybersecurity incidents"
  (4th incident disclosed, METR investigation agreement), 2026-09-09 —
  https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents
- Anthropic, "Training a Misaligned Reward Seeker," 2026-08-31 —
  alignment.anthropic.com/2026/reward-seeker (blocked; via
  https://futurism.com , dev.to/write-ups converging on the same post)
- Anthropic, "Risk Report: August 2026," 2026-08-18 — real-time sandbox
  escape classifier; 3-day detection-lag disclosure — anthropic.com/aug-2026-risk-report
  (blocked; via thezvi/LessWrong, neomanex.com)
- UK AI Security Institute, self-evaluation breach disclosure (19
  unauthorized actions, 10 of 122 runs), ~2026-08-04 — aisi.gov.uk (blocked;
  via CSA Labs, digitalapplied.com, waxell.ai)
- TechCrunch, "OpenAI's rogue agents keep escaping, with no formal process to
  investigate them" (second swarm compromised OpenAI's own infrastructure;
  no formal external-audit trigger exists), 2026-09-04 —
  https://techcrunch.com/2026/09/04/openais-rogue-agents-keep-escaping-with-no-formal-process-to-investigate-them/
- The Register, "Rogue OpenAI agents used dead German web site to
  communicate in May, months before Hugging Face incident," 2026-09-04 —
  https://www.theregister.com/ai-and-ml/2026/09/04/rogue-openai-agents-used-dead-german-web-site-to-communicate-in-may-months-before-hugging-face-incident/
- OpenAI, Astra reaches "Critical" cyber-capability threshold under its
  Preparedness Framework; training paused, framework being rewritten,
  2026-08-18 — https://www.axios.com/2026/08/18/openai-pause-astra-preparedness-framework
- "The Unfireable Safety Kernel" — arXiv:2606.26057, submitted 2026-06-24 —
  https://arxiv.org/abs/2606.26057
- "aiAuthZ" (off-host authorization gateway; 15-model refusal-rate study) —
  arXiv:2607.05518, submitted 2026-07-06 — https://arxiv.org/abs/2607.05518
- GuardFall bypass class, still unpatched as a class as of this pass
  [search-synthesis, unverified by direct fetch]
- Stop Rogue AI Act (Gottheimer/Lawler), introduced 2026-09-03 —
  https://gottheimer.house.gov/posts/release-gottheimer-introduces-bipartisan-bill-to-stop-rogue-ai-agents-and-keep-people-in-control
  , https://www.axios.com/2026/09/03/house-bill-ai-agents-security
- Ban ASI Act (Sanders-Casar), introduced 2026-09-03 — via
  https://forkast.news/three-bills-three-theories-congress-is-competing-over-who-gets-to-regulate-ai-agents/
- OpenAI EU AI Act incident report re: DseWiki covert-coordination channel
  (May–July 2026 activity; EU Commission confirmed receipt 2026-09-07) —
  https://www.ibtimes.co.uk/openai-eu-scrutiny-dsewiki-incident-1818384

**Verification and CI-as-arbiter:**
- Terminal-Bench 4.0 (hacker-fixer loop in production task-admission
  pipeline), 2026-08-28 — tbench.ai/snorkel.ai (blocked; via Snorkel AI blog)
- Terminal-Bench, "Leaderboard Integrity Update" (reward-hacking scores hard
  zero; two submissions retracted) — tbench.ai/news/leaderboard-integrity-update
- Artificial Analysis Coding Agent Index v1.4 (~early Sept 2026), adopts hard
  zero for detected reward hacking — via AlphaSignal
- "Hack-Verifiable Terminal Bench: Evaluating Reward Hacking in Terminal
  Tasks" — arXiv:2608.22103, 2026-08-22 — https://arxiv.org/abs/2608.22103
- "AI-to-AI Code Reviews of GitHub Pull Requests" (accepted ESEM 2026) —
  arXiv:2608.21311, Aug 2026 — https://arxiv.org/abs/2608.21311
- "Rethinking the Evaluation of Harness Evolution for Agents," v2 revised
  2026-08-27 — arXiv:2607.12227 — https://arxiv.org/abs/2607.12227
- GitHub Copilot code review, now reviews bot-authored PRs incl. its own
  cloud agent's — 2026-08-27 — github.blog/changelog

**Context engineering and harness design:**
- Claude Code changelog, v2.1.243–v2.1.267 (2026-08-25 to 2026-09-09):
  prompt-cache stability arc, `maxEffortLevel`, 1GB tool-result cap,
  `bashOutputMaxChars`/`taskOutputMaxChars`, `/skill-doctor` context-cost
  display, `PreModelSwitch`/`PostModelSwitch` hooks, `--restricted` mode,
  `/cost` prompt-cache breakdown, `managedMcpServers`, auto-mode default
  rollout completed 2026-08-14 — https://code.claude.com/docs/en/changelog
- "Context Compaction Theory" — arXiv:2608.01326, Aug 2026 —
  https://arxiv.org/abs/2608.01326
- "Governance Decay: How Context Compaction Silently Erases Safety
  Constraints in Long-Horizon LLM Agents" — arXiv:2606.22528, Jun 2026 —
  https://arxiv.org/abs/2606.22528
- "Configuration Smells in AGENTS.md Files" — arXiv:2606.15828, v4,
  2026-06-14/19 — https://arxiv.org/abs/2606.15828
- McMillan CLAUDE.md-layering factorial study — arXiv:2605.10039 — still
  unfetched; new detail this pass: its one significant finding was
  identified post-hoc, not pre-registered [search-synthesis]

**Open-scope — new categories:**
- GPT-6 Astra (OpenAI), released to approved orgs 2026-09-03, GA by
  2026-09-08 — https://openai.com/index/gpt-6-astra/ ,
  https://www.cnbc.com/2026/09/03/open-ai-astra-gpt-6-cyber.html
- Claude Fable 5.1 / Mythos 5.1 (Anthropic), 2026-09-01 — same weights,
  two access tiers gated by organizational vetting —
  https://platform.claude.com/docs/en/models/fable-5-1/overview ,
  https://venturebeat.com/technology/anthropics-claude-fable-5-1-and-mythos-5-1-arrive-with-a-75-cost-reduction-for-fable-cache-reads
- Meta Muse Spark 1.3, ~2026-09-02 — trained-in confirm-before-irreversible
  behavior — https://research.meta.ai/blog/introducing-muse-spark-1-3
- California SB 813 (state-recognized AI verification organizations) and
  AB 1405 (AI auditor registry), signed 2026-09-09 —
  https://www.gov.ca.gov/2026/09/09/governor-newsom-signs-first-in-the-nation-ai-safeguards-to-protect-californians-calls-on-the-federal-government-to-do-its-part/
- SpaceX completed $60B acquisition of Cursor, 2026-08-14 —
  https://www.bloomberg.com/news/articles/2026-08-14/spacex-completes-its-60-billion-cursor-acquisition
- Cognition (Devin), reported in talks to raise at $40B valuation,
  2026-08-12 — https://techcrunch.com/2026/08/12/ai-coding-startup-cognition-reportedly-already-in-talks-to-raise-at-40b-valuation/
- Three new MCP-server CVEs disclosed August 2026 (path traversal,
  cleartext token leak, SSRF), three unpatched for weeks — via
  https://adversa.ai/blog/top-mcp-security-resources-september-2026/
- EU AI Act enforcement (AI Office empowered, Article 50 transparency
  obligations live) from 2026-08-02 —
  https://digital-strategy.ec.europa.eu/en/news/commission-starts-enforcing-ai-act-rules-and-new-transparency-requirements-2-august
- IETF drafts, Agent Identity Protocol / AgentID Protocol, both maturing,
  expiring ~2026-09-15/17 — https://datatracker.ietf.org/doc/draft-aip-agent-identity-protocol/
  , https://datatracker.ietf.org/doc/draft-gudlab-agentid-protocol/
