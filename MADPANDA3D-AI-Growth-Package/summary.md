# MADPANDA3D AI Growth Package — Utilization Summary

**Package path:** `/mnt/dev-env/projects/pandamonium/MADPANDA3D-AI-Growth-Package`  
**Status on disk:** English authoring candidate, not a release copy (built 2026-08-20)  
**Size:** 124 files — 77 chapters, 8 modules, 3 appendices, ~274 designed pages, plus a buyer workspace and a separate digital-product launch system

---

## 1. ELI5

This folder is an operating school for building AI systems you actually own, not a pile of magic prompts to paste into a soul file.

It teaches you, in order: what you already have, what the first job should be, how the network and host underneath the agent must behave, how the agent should talk, how to give it a durable workspace and tools, and how to run one measured business loop. Every lesson produces a filled-in record (inventory, contract, map, ticket, scorecard) instead of a chat that evaporates. The package itself says do not load the whole guide into one session. Point an agent at the router (`INGEST-ME-FIRST.md`), load one module, fill one template, update `STATUS.md`, and stop. A brand-new Hermes agent that dumps these 274 pages into `SOUL.md` will forget the method and drown in text. A brand-new Hermes agent that *uses* this folder as a library — soul points at the router, work happens in a copy of the buyer workspace, modules load on demand — will actually perform the knowledge in the pack.

---

## 2. Detailed summary

### What you were given

The pack is the next-edition MADPANDA3D AI Growth Guide in customer-safe form. Canonical identity lives in `PACKAGE-INDEX.json` and `MANIFEST.json`. The long manuscript is duplicated as `01-AI-GROWTH-GUIDE.pdf` (~1.2 MB) and `02-AI-GROWTH-GUIDE.txt` (~976 KB). Split Markdown in `guide/` is what an agent should actually read. `modules/*.json` are per-track manifests. `templates/` are blank buyer-owned records. `06-BUYER-WORKSPACE/` is the empty project brain. `07-DIGITAL-PRODUCT-LAUNCH-SYSTEM/` is a versioned Product 01 playbook for turning experience into one digital offer. `PROVENANCE.md`, `SOURCES.md`, and `SHA256SUMS.txt` are the rights, source-family, and integrity layer.

It is labeled **ENGLISH AUTHORING CANDIDATE — NOT RELEASE COPY**. Appendix C still quotes an older 57-chapter / 195–215-page target; the live index is 77 chapters and 274 designed pages. Treat the index and hashes as truth, not the stale appendix numbers. `release_authority` is false. You may use it internally. You may not republish the pack, its templates, or MADPANDA3D branding as a product.

### How the pack wants to be used (this is the utilization doctrine)

`INGEST-ME-FIRST.md` is the intelligence router. The prescribed loop is:

1. Read `PACKAGE-INDEX.json`.
2. Ask which outcome is needed *now*.
3. Open only the matching `modules/<id>.json`.
4. Read that module’s guide slice, named templates, accepted inputs, and current `STATUS.md`.
5. State known / assumed / unknown before proposing work.
6. Close with artifact path, result, blocker or pass, evidence, unresolved risk, and one next owner action.

Never request credentials. Prepare or read by default. Send, publish, spend, delete, permission-change, or deploy only under the chapter’s authority plus an owner approval record. If a required input is missing, stop at `BLOCKED`, name one owner task, and preserve state.

Learning depth (`ORI-02`) is Quick, Operator, Builder, Architect, or Lab. Depth changes detail, not authority. Start Operator unless you only need a decision (Quick) or live access is not authorized (Lab).

Every material fact is labeled **OBSERVED**, **OWNER-STATED**, **RESEARCHED**, **ASSUMPTION**, or **UNKNOWN**. `RECOMMENDATION` is a proposed action, not evidence. Current provider/system-of-record readback outranks memory. That labeling system is the pack’s real “intelligence,” more than any chapter of networking or MCP trivia.

### The eight modules (what knowledge is actually in here)

**Orientation (`guide/00-orientation.md`, ORI-01–03).** Creates the workspace tree, chooses depth, and sets the human/LLM working contract. The agent facilitates, researches, and drafts. The owner keeps goals, accounts, approvals, and consequential actions. Output: `STATUS.md`, a learning-depth decision, and the working protocol.

**Foundation (`guide/10-foundation.md`, FND-01–06).** Inventory people, hardware, services, data, access, and workflows before buying anything. Turn three ranked outcomes into workloads and constraints. Score infrastructure maturity and agent maturity *separately* from 0–5 (ad hoc → operated; chat → business partner). Convert needs into roles and flows. Compare three placement patterns: workstation-first, starter single-node, and separated/hybrid. Capstone is `FOUNDATION-BUILD-BRIEF.md`: one outcome, architecture, authority boundary, resource path, recovery path, first slice, and stop conditions.

**Networking (`guide/20-networking.md`, NET-01–12; accepted for continued authoring).** Requirements and inventory; end-to-end agent traffic path; physical/logical/data-flow topologies; OSI-style layer diagnosis; addressing and subnets; DNS/DHCP/time dependencies; routing, NAT, ports, egress allowlists; wireless and private operator access; trust zones (NIST 800-207 style, location is not trust); capacity, latency, failover; telemetry, SLOs, change; troubleshooting and recovery capstone. Twelve templates, including `NETWORK-INVENTORY.template.csv`. Completion: one fictional or approved isolated AI path is mapped, protected, observed, diagnosed, recovered, and verified without leaking private topology.

**Operating systems (`guide/25-operating-systems.md`, OS-01–20; draft for independent QA).** The densest track: the host *beneath* the agent. Host operating contract; request-to-hardware trace; users vs service identities vs privilege vs authority; processes/threads/services; scheduling AI work with evidence; physical memory and fragmentation; virtual memory, working sets, cache, swap; concurrency and shared state; races/deadlocks/livelock/starvation; devices, drivers, accelerators, I/O; storage, volumes, RAID, failure domains; filesystems and metadata; file ownership, locks, publication; host network stack, sockets, ports, names, time; service startup/readiness/health/shutdown; process vs container vs VM isolation and resource limits; translating the contract across Linux/Windows/POSIX/OCI platforms; performance baselines; patch/protect/recover/maintain; OS-aware AI host acceptance under load and failure. Twenty templates, one per chapter. Completion: one declared AI host is mapped, resource-bounded, recoverable, measured, failure-tested, and independently accepted without granting undeclared authority.

**Infrastructure (`guide/30-infrastructure.md`, INF-01–08).** Equipment roles; sourcing parts from live requirements; compute and model-fit contracts; state, storage, backup, restore; safe container/service deployment; truthful health, queues, backpressure, incidents; retrieval *before* calling it memory (searchable archive vs compact reviewed memory, ten known-answer tests, leakage checks); then the choice among instructions, retrieval, tools, or fine-tuning, plus a ten-step failure-diagnosis ladder from power/host up to user acceptance. This module is the direct argument against stuffing the folder into a soul: transcripts and documents belong in an archive; only reviewed facts belong in compact memory.

**Communication (`guide/40-communication.md`, COM-01–10; accepted for continued authoring).** Communication contract; audience, identity, privacy, context; observation vs inference vs assumption vs unknown; language, ambiguity, ownership; tone, channel, format, accessibility (WCAG 2.2); capture–check–respond–record; respond to emotion without pretending to feel; disagree, repair, escalate, restore trust; score response quality and diagnose the failure layer; responsible adaptation capstone. Nine communication templates plus a fact/inference/unknown CSV ledger. Completion: one bounded communication behavior is specified, tested, independently scored, repaired or deferred, and adapted only through an evidence-supported layer.

**Agents and MCP (`guide/50-agents-mcp.md`, AGT-01–04, MCP-01–06).** Durable workspace (control files vs separate source repo). Roles: owner, coordinator, specialists, verifier/runner, control plane — more agents are not more intelligence. Tickets as durable work packages with liveness. Turn the communication contract into operating rules (`AGENTS.md` in the buyer workspace is the seed). MCP: hosts/clients/servers/capability; tool contracts humans and agents can read; secrets vs permissions vs configuration; one service with observable health; direct vs brokered vs managed vs no connection; rehearse, recover, and prove one vertical slice. Completion: one service and workflow preserve identity, authority, task state, resource liveness, health, external readback, recovery, and independent verification.

**Business (`guide/60-business.md`, BUS-01–08).** One closed measured loop: trigger → approved context → decide → prepare → approve if required → execute → read back → evidence → durable state → next review. Skills (how) vs plays (one move) vs playbooks (sequence) — knowing how to publish is not permission to publish. Four reference patterns: (A) website/lead/CRM/follow-up, (B) content research/production/rights, (C) support and maintenance tickets, (D) client onboarding and reporting. Apply communication quality to those interactions. Activate the included launch system as an optional module. Weekly operator review. 30/60/90 roadmap that defers sprawl. Final capstone: the next evidence-earning move, not a bigger architecture.

### Buyer workspace (`06-BUYER-WORKSPACE/`)

This is the agent’s project brain. Copy it *out* of the purchased pack before filling it. Root files: `AGENTS.md` (operating contract and session start/end order), `STATUS.md` (stage, blockers, next action), `DECISIONS.md` (dated choices and revisit triggers), `SYSTEM-MAP.md` (roles, flows, data, recovery, acceptance tests), `MEMORY.md` (compact durable facts with provenance — not a transcript), `BUGS.md`, `HANDOVER.md` (exact resume point), `BACKLOG.md` (ideas that are not commitments). `artifacts/` holds generated worksheets. `evidence/` holds minimized, redacted proof. `tickets/` has six truthful states: open, in-progress, completed, failed, blocked, skipped. `AGENTS.md` already encodes approval gates for outbound messages, purchases, deletes, deploys, and a recovery gate (independent backup + restore drill before replacing an accepted path).

### Digital Product Launch System (`07-DIGITAL-PRODUCT-LAUNCH-SYSTEM/`)

A separate Product 01 (v1.0.0) for launching one source-backed digital offer. Treat the purchased files as read-only. Work in a private folder. Plays 0–8: agent/tool intake → extract buyer problem → validate demand and offer → design the product → build the package → independent product QA → buyer path + independent path QA → organic launch → 30-day evidence loop. Assets include research matrix, offer scorecard, content calendar, QA rubric, launch-readiness checklist, delivery-defect log, and revenue/feedback scorecard. Resume integrity: mismatched package hash stops without mutation; missing artifacts rewind the earliest producing play and block downstream PASS states. License: internal use and commercial use of *original* outputs from your own knowledge; no redistribution of package text, templates, or MADPANDA3D marks. Privacy: no customer records, secrets, or card data in templates. Support: `support@madpanda3d.com` for access/download/update/refund only — not done-for-you creation.

### Templates, appendices, provenance

Fifty-plus templates under `templates/communication`, `networking`, `operating-systems`, and `system`, plus chapter/provenance/sources shells. Appendix A is the artifact index and the routing rule (load one path). Appendix B is source classes (MADPANDA-operator, public-primary, private-academic), freshness (evergreen / before-release / live-readback), and the rule that current official docs outrank remembered commands. Academic families consulted: Wood (communication), Solomon & Kim (networking), McHoes & Flynn 2018 (stable OS concepts only). Public families: NIST AI RMF, NIST AI 600-1, NIST 800-207, 800-61, 800-40, IETF RFCs, CISA, WCAG 2.2, Linux kernel docs, POSIX.1-2024, Microsoft process/working-set docs, OCI specs, current MCP spec (recheck before freeze). Appendix C is a package-completion scorecard for the author, not a customer release stamp.

### What this folder is *for* (uses, not just contents)

- **Operator school** for you: walk chapters at Operator depth and fill the buyer workspace against the real 24/7 Labs cluster.
- **Agent operating system:** `AGENTS.md` + tickets + handover is a portable control plane that maps cleanly onto Hermes Kanban (open/in-progress/completed/failed/blocked/skipped ≈ ready/running/done/failed/needs_input).
- **Cluster documentation factory:** NET and OS templates can produce the missing host, path, trust-zone, model-fit, and recovery records for pve-prod, vm-hermes, inference nodes, Tailscale, GitLab, CompAI, Lightpanda, Vane, Odysseus, Pandamonium.
- **Communication QA:** COM templates can score lead replies, support, voice agents (Odysseus), and bot-room tone without claiming the model “feels.”
- **MCP hardening:** MCP-01–06 are a contract/readiness/recovery kit for every MCP already in this Cursor session (browser, Context7, Lightpanda, Tailscale, HypeJet).
- **Business loop design:** BUS-03 Pattern A is a blueprint for CompAI CRM lead ownership; Pattern C for cluster incidents; Pattern D for client upgrade packs (Business/Music Upgrade).
- **Productization:** the launch system can ship *original* 24/7 Labs offers (playbooks, operator kits) without copying MADPANDA prose.
- **Retrieval corpus (carefully):** INF-07 says index a small approved slice with ten known-answer tests before calling it memory. The guide Markdown + templates are a good pilot corpus. The PDF/TXT duplicates and empty buyer templates are not.
- **Not a soul paste, not a second Kanban, not a license to publish the pack, not legal/security/tax advice, not a sales guarantee.**

### Best way to use this with a new Hermes agent

Do **not** paste the folder into `SOUL.md`. The pack forbids whole-guide ingest; INF-07 forbids stuffing archives into compact memory; Hermes SOUL/config edits on this cluster are Morpheus review cards, not silent Cursor writes.

**Recommended shape (router soul + working copy + on-demand modules):**

| Layer | What | Where |
| --- | --- | --- |
| Reference (read-only) | This pack | `/mnt/dev-env/projects/pandamonium/MADPANDA3D-AI-Growth-Package` |
| Soul (compact) | Identity, never-do, session start order, pointer to `INGEST-ME-FIRST.md` and `PACKAGE-INDEX.json`, evidence labels, approval gates | `~/.hermes/profiles/<slug>/SOUL.md` on vm-hermes — **review card**, not a silent edit |
| Working memory | Copied buyer workspace, filled over time | e.g. `/mnt/dev-env/docs/clients/madpanda-growth/` or a dedicated `projects/<slug>` workspace |
| On-demand intelligence | One module guide + templates per ticket | Loaded by the router, not preloaded |
| Optional retrieval | Chunked `guide/` + templates after a ten-query acceptance set | Pandamonium Chroma or existing KB — only after INF-07 tests pass |
| Optional later split | Specialist profiles (net, OS, comms, launch) | Only after one coordinator + one specialist vertical slice works (`AGT-02`) |

Soul should say: read `INGEST-ME-FIRST.md`, then `STATUS.md` in the working copy, then the one module the current ticket names. It should repeat the approval, credential, and recovery gates from buyer `AGENTS.md`. It should not contain chapter prose.

Map pack tickets onto Hermes Kanban rather than running a second board. Use pack `tickets/` inside the working copy for chapter artifacts; use Hermes Kanban for cluster execution. Keep implementation source in GitLab `projects/<slug>`, not inside the pack or the buyer workspace (`SYSTEM-MAP.md` links them).

First 30 days, if you follow the pack: copy the buyer workspace out; fill orientation; run a current-state inventory of this cluster (FND-01); pick one measured loop (likely CompAI lead follow-up or incident triage); write a foundation build brief for that slice only; then consider a Hermes profile whose soul is the router. Do not start by creating eight specialist bots.

---

## 3. Ten example prompts

These are written to run against **this cluster** with the pack as read-only reference and a **separate** working copy of `06-BUYER-WORKSPACE`. Replace `WORKSPACE` with that copy’s path. Replace `PACK` with `/mnt/dev-env/projects/pandamonium/MADPANDA3D-AI-Growth-Package`.

### Prompt 1 — Initialize the workspace the pack actually wants

> You are my MADPANDA3D AI Growth operator. PACK is read-only at `/mnt/dev-env/projects/pandamonium/MADPANDA3D-AI-Growth-Package`. My private WORKSPACE will live at `/mnt/dev-env/docs/clients/madpanda-growth/` (create it if missing). Read `PACK/INGEST-ME-FIRST.md`, `PACK/PACKAGE-INDEX.json`, and `PACK/06-BUYER-WORKSPACE/AGENTS.md`. Copy the buyer-workspace control files into WORKSPACE without copying the rest of the pack. Initialize `STATUS.md` with today’s date, package identity `madpanda3d-ai-growth-package-next-edition-english-authoring-candidate`, and stage “Orientation: in progress.” Write a `LEARNING-DEPTH-DECISION.md` recommending OPERATOR for the first outcome “durable cluster operating records + one measured business loop.” Fill `SYSTEM-MAP.md` with the known 24/7 Labs map from `/mnt/dev-env/MAP.md` (pve-prod, vm-hermes 192.168.1.192, GitLab CT311, CompAI 192.168.1.170, Lightpanda, Vane, Odysseus, Pandamonium, Tailscale). Label every host fact OBSERVED or UNKNOWN. Do not edit PACK. Do not ask for credentials. Show the proposed files, then wait.

### Prompt 2 — Design a Hermes soul as a router, not a dump

> Act as the AGT-01 / AGT-02 / INF-07 facilitator from PACK `guide/50-agents-mcp.md` and `guide/30-infrastructure.md`. I want a new Hermes profile on vm-hermes whose intelligence is this pack, but I will not paste 274 pages into SOUL.md. Draft a compact SOUL (identity, never-do, session start order, evidence labels, approval gates, recovery gate) that **points at** `PACK/INGEST-ME-FIRST.md` and `PACK/PACKAGE-INDEX.json` and **reads** WORKSPACE `STATUS.md` / `HANDOVER.md` / the active ticket. Include a Load: note that module guides are opened only after the router selects one module. Propose the profile slug, wake phrase, and which existing cast member this must not collide with (Morpheus remains default decomposer; this profile is a specialist or coordinator, not a second orchestrator). Output: (1) proposed SOUL.md body, (2) proposed AGENTS.md delta, (3) a Morpheus review-card body I can paste — Cursor must not write `~/.hermes/` itself. Do not implement.

### Prompt 3 — Cluster current-state inventory (Foundation)

> Run FND-01 from `PACK/guide/10-foundation.md` against this lab. Interview from `/mnt/dev-env/MAP.md`, `apps/README.md`, and WORKSPACE `SYSTEM-MAP.md`. Produce `WORKSPACE/artifacts/CURRENT-STATE-INVENTORY.md` covering: people and maintenance capacity; every named host/LXC/VM (role, OS if known, owner, maintenance window); services (GitLab, Hermes Kanban, CompAI CRM, Lightpanda, Vane, Odysseus, Pandamonium, Qwen3-TTS, KB, Dark Horse KB, Community Hub); data stores and backup/restore UNKNOWN items; access paths (LAN, Tailscale Serve, what must never be Funneled); existing AI tools (Unsloth proxies, LM Studio, LiteLLM); workflows I already run (Kanban dispatch, Business/Music Upgrade, website skill, CRM). Ask one question at a time only when a fact changes architecture. Prefer reuse. End with a proposed `STATUS.md` update. No purchases.

### Prompt 4 — One closed CompAI lead loop (Business Pattern A)

> Using BUS-01 and BUS-03 Pattern A in `PACK/guide/60-business.md`, design the first measured loop for CompAI CRM at `http://192.168.1.170:3001` (API `:4000`, Postgres on that LXC, code `projects/compai-crm`, auth currently allowlist). Score ten repeated 24/7 Labs tasks I will paste, then recommend whether CRM lead ownership beats incident triage for slice one. Write `WORKSPACE/artifacts/28-FIRST-CYCLE.md` with trigger, source of truth, read vs write tools, per-action approval for any outbound message, authoritative readback (CRM record + delivery status, not the agent’s claim), failure path, and next review. Map pack ticket states onto Hermes Kanban (`hermes-penny` research vs `hermes-amy` product vs Cursor orchestrator). Do not connect to the CRM or send mail.

### Prompt 5 — Trust-zone and egress map of the cluster (Networking)

> Run NET-01, NET-02, NET-07, and NET-09 using the templates in `PACK/templates/networking/`. Fill them in WORKSPACE/artifacts for one approved path: operator on Windows → Tailscale/LAN → pve-prod `192.168.1.93` → vm-hermes `:8642`/`:9119` → one specialist spawn → GitLab `192.168.1.93:3000` and CompAI `192.168.1.170`. Use documentation-safe addresses only; no private customer topology, no secrets. Produce: requirements brief, inventory CSV rows for the devices in MAP.md, route/egress allowlist (what may leave the tailnet; Funnel forbidden on `:7080`/`:7088`/`:7000`), and trust-zone matrix (workstation / LAN / tailnet / LXC / public). Label LIVE-READBACK items that still need `tailscale status` or a ping. Stop at BLOCKED rather than guessing a firewall rule.

### Prompt 6 — OS-aware acceptance of vm-hermes and one inference host

> Using OS-01, OS-07, OS-15, OS-16, OS-18, and OS-20 templates, draft an OS-aware AI host acceptance record for (a) vm-hermes `192.168.1.192` as agent control plane and (b) one inference host from MAP.md (pve-heavy Unsloth `192.168.1.2:8888` or M2 `192.168.1.191:8888`). Distinguish users, service identities, and undeclared agent authority. Capture process/service state, memory pressure / model residency, isolation (VM vs LXC vs Docker), service readiness, and a failure test that does **not** grant the agent `pct` on pve-prod from vm-hermes (Raj capability gap). Output the filled templates under WORKSPACE/artifacts and a single acceptance verdict: pass, blocked, or lab-only. Read-only inspection. No host changes.

### Prompt 7 — Retrieval pilot for the pack itself (do not call it memory yet)

> Act as INF-07 knowledge engineer. Do not ingest the whole filesystem. Pilot corpus = `PACK/guide/*.md`, `PACK/INGEST-ME-FIRST.md`, `PACK/PACKAGE-INDEX.json`, and `PACK/templates/**` — exclude `01-AI-GROWTH-GUIDE.pdf`, `02-AI-GROWTH-GUIDE.txt` (duplicates), empty buyer placeholders, and SHA files. Write `WORKSPACE/artifacts/15-KNOWLEDGE-AND-RAG.md` with provenance fields, sensitivity, chunking assumptions, and ten known-answer queries (example: “What file does a new session read first?” → INGEST-ME-FIRST.md; “How many OS chapters?” → 20; “May we dump the guide into SOUL?” → no). Include a leakage test so CompAI customer data and GitLab credentials cannot appear in this index. Prefer Pandamonium Chroma on `127.0.0.1:8110` or Dark Horse/KB only if the pilot fails for a named reason. Do not promote chunks into MEMORY.md without review.

### Prompt 8 — Communication contract for Odysseus and Hermes voice

> Run COM-01, COM-02, COM-05, COM-07, and COM-09 for two audiences: (1) Jason operating the cluster, (2) a live Odysseus caller on `https://prod.tail61d527.ts.net:7000`. Fill the audience/tone profile, tone-channel-accessibility matrix, validation/de-escalation ladder, and response-quality rubric. Rules the pack requires: no fake inner state; outbound SMS/email/WhatsApp still need exact-draft approval; voice may clarify but may not spend, publish, or change access. Produce `WORKSPACE/artifacts/BUSINESS-CONVERSATION-RECORD.md` with one scored fictional call and one scored Kanban update. Independent scoring of response quality vs task outcome. No live call, no TTS/STT changes.

### Prompt 9 — MCP tool-contract audit of this Cursor session

> Using MCP-01 through MCP-04 and templates `TICKET-STATE-AND-LIVENESS` and `SERVICE-PROCESS-READINESS`, inventory the MCP namespaces actually available here (cursor-ide-browser, Context7, Lightpanda `192.168.1.210:9223/mcp`, Tailscale, HypeJet, cursor GenerateImage). For each: outcome served, read vs write, data it may see, actions that always need approval, authoritative readback, stop conditions. Mark UNVERIFIED anything not proven in this session. Write tool contracts into WORKSPACE/artifacts. Recommend direct vs brokered vs no-connection per MCP-05. Do not add servers, do not print secrets, do not call `mcp_auth` unless I say so.

### Prompt 10 — Launch an original 24/7 Labs operator kit (not a resale of this pack)

> Activate `PACK/07-DIGITAL-PRODUCT-LAUNCH-SYSTEM/` as BUS-05. Read `START-HERE.md` and `PLAYBOOK.md`. Create a private launch workspace at `/mnt/dev-env/docs/clients/labs247-operator-kit/` beside PACK, not inside it. Copy `STATUS.template.md`, record package version and SHA-256 from PACK checksums, then open Play 0. Outcome: one original digital product — “24/7 Labs Cluster Operator Kit” — built from *our* MAP.md, Kanban playbook, and Trinity rules, using the launch *method* only. Do not copy MADPANDA3D chapter prose, templates-as-product, or trademarks into the customer archive. Play 1 should extract the buyer as “solo operator of a homelab/Proxmox AI cluster.” Stop after Play 0–1 artifacts pass (`AGENT-CAPABILITY-MAP.md`, `BUYER-PROBLEM-BRIEF.md`). Independent QA (Play 5–6) stays in a later ticket. No store listing, no publish, no spend.

---

## Quick don’ts

- Do not paste `02-AI-GROWTH-GUIDE.txt` into a Hermes SOUL.
- Do not edit files inside this gifted folder; copy the buyer workspace out.
- Do not treat Appendix C’s old page counts as current.
- Do not silently write `~/.hermes/profiles/*/SOUL.md` — that is a Morpheus review card.
- Do not redistribute the pack or sell its text as your product.
