# Part IV - Build the Self-Hosted AI Foundation

## 42. Audit Equipment and Assign Roles

> **Chapter handle:** `INF-01`.

Hardware planning starts with workloads, not parts. "I want an AI server" is not yet a requirement. A useful requirement sounds like this:

- one interactive user;
- local text chat with a response beginning within a few seconds;
- two background research or coding tasks at once;
- retrieval across a curated document collection;
- optional speech input and output;
- private remote access;
- nightly state backups;
- no public model endpoint.

### Map workloads to roles

Use roles to prevent one exciting feature from silently consuming the entire system.

| Role | Primary pressure | First placement |
| --- | --- | --- |
| Operator interface | Browser, light CPU, network | Existing laptop or desktop |
| Orchestrator | CPU, RAM, database I/O | Existing always-on system or small VM |
| Daily router/model | GPU VRAM, RAM, disk, latency | Best available GPU system |
| Coding/reasoning specialist | VRAM, context, sustained compute | Same model host at first; scheduled separately |
| Embeddings and retrieval | CPU or GPU, RAM, storage I/O | Orchestrator or model host |
| Speech-to-text | CPU/GPU, real-time latency | Compute host or dedicated service |
| Text-to-speech | CPU/GPU, audio latency | Compute host or CPU fallback |
| Bulk document storage | Capacity, integrity, backups | NAS, external disk, or existing storage server |
| Monitoring | Low CPU, persistent storage | Orchestrator or small separate service |

The first audit records facts without changing anything. On Linux, commands like these provide a useful read-only starting point:

```bash
uname -a
lscpu
free -h
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS,MODEL
df -hT
lspci | grep -Ei 'vga|3d|display'
nvidia-smi 2>/dev/null || true
ip -br addr
```

These commands can reveal local addresses, interface names, device models, mount paths, usernames, and other environment-specific identifiers. Keep the raw output in the private project workspace. In any shareable artifact, summarize component roles and capacity, and omit addresses, serial numbers, user paths, hostnames, credentials, and other identifiers that are not needed to explain the design.

Record operating system, CPU cores and threads, total and currently available RAM, GPU model and VRAM, free disk by device, network link speed, idle power draw if known, and whether the machine can remain on safely. Also record constraints: noise, heat, power, physical space, family use, business use, or a requirement that the machine remain a daily workstation.

Do not combine "total" and "available." A workstation with 32 GB installed but only 9 GB normally free does not offer 32 GB to an agent stack. Do not treat a nearly full system disk as model storage. Do not assume a GPU can be passed through to a VM until the platform, driver, and current display use have been checked.

### Exercise: create the equipment audit

Create `08-HARDWARE-INVENTORY.md` with:

1. current machines and their normal purpose;
2. CPU, RAM, GPU/VRAM, free disk, and network facts;
3. always-on suitability;
4. workloads each machine may host;
5. workloads each machine must not host;
6. unknowns that require a read-only check;
7. a one-sentence first deployment hypothesis.

Generalized example:

> The desktop remains the interactive workstation and temporary model-compute host. A low-power mini PC runs the private orchestrator, state database, and monitoring. Existing network storage holds documents and encrypted backups. No purchase is approved until one local model and one retrieval test establish the real bottleneck.

### Agent checkpoint prompt

```text
Act as my infrastructure auditor. Help me create 08-HARDWARE-INVENTORY.md.
Ask for one machine at a time. Separate verified facts from estimates and
unknowns. Do not recommend purchases yet. Map each required workload to a
possible current machine, identify conflicts such as shared GPU use or low
free disk, and finish with a smallest-safe first deployment hypothesis.
Do not run or suggest mutating commands. Return the final artifact in Markdown
and list the evidence still needed before hardware decisions.
```

**Produced artifact:** `08-HARDWARE-INVENTORY.md`

**Done when:** every proposed service has a possible current home or is explicitly marked unplaced; available resources are recorded; and no purchase is justified by enthusiasm alone.


## 43. Source Parts From Live Requirements

> **Chapter handle:** `INF-02`.

A fixed parts list decays quickly. Prices change, used-market inventory changes, motherboard revisions change, and a model that mattered six months ago may no longer be the best fit. The durable product is a sourcing workflow.

### The live sourcing sequence

1. **Name the measured bottleneck.** Examples: insufficient VRAM for the selected quantization, not enough free RAM for model offload, slow document storage, or no reliable always-on host.
2. **Set the workload target.** State concurrency, latency, context, storage, power, noise, and growth expectations.
3. **Set a full budget.** Include memory, storage, power supply, cooling, adapters, drive bays, cables, tax, shipping, and backup media.
4. **Research current options.** Use manufacturer specifications for compatibility and current reputable listings for price.
5. **Create at least three paths.** Reuse/upgrade, value new build, and higher-headroom build.
6. **Check the whole system.** GPU dimensions, power connectors, power-supply capacity, motherboard lanes, memory type, storage slots, cooling, case clearance, and virtualization support all matter.
7. **Evaluate used parts separately.** Ask about warranty, return window, mining history, drive health, fan noise, corrosion, and evidence of operation.
8. **Timestamp every price.** A sourcing report without an as-of date is not a purchasing decision.
9. **Choose based on cost per solved constraint.** The most expensive option is not automatically the safest.
10. **Recheck immediately before purchase.** Compatibility and availability must be live.

The agent should never invent listings, prices, benchmark results, or stock status. It should link current sources, state the access date, distinguish manufacturer claims from independent tests, and flag any compatibility claim that has not been verified.

### Exercise: produce three sourcing paths

Create `09-LIVE-SOURCING-DECISION.md`. For each path, include:

- the bottleneck it solves;
- parts being reused;
- parts being added;
- compatibility evidence;
- current estimated total cost;
- expected capability;
- power/noise/space implications;
- upgrade ceiling;
- risks and unknowns;
- a "do nothing yet" trigger.

Generalized example:

> A used GPU may be the best cost-per-VRAM option, but the existing case and power supply cannot safely support it. The actual choices are therefore a smaller compatible GPU, a case/power rebuild, or delaying the purchase while using a cloud specialist for rare large-model tasks.

### Agent checkpoint prompt

```text
Use 08-HARDWARE-INVENTORY.md and act as my live parts-sourcing analyst.
First ask which measured bottleneck we are solving and the maximum all-in
budget. Research current manufacturer specifications and current reputable
prices; do not rely on remembered prices. Build reuse/upgrade, value, and
headroom paths. Check physical, electrical, platform, memory, storage, cooling,
and virtualization compatibility. Timestamp sources and separate verified
facts from estimates. Do not purchase anything. Produce
09-LIVE-SOURCING-DECISION.md and end with the exact facts I must verify before
approving a purchase.
```

**Produced artifact:** `09-LIVE-SOURCING-DECISION.md`

**Done when:** the selected path solves a measured constraint, every major compatibility claim has evidence, the full cost is visible, and the decision can be revisited when prices change.


## 44. Prove Compute and Model Fit

> **Chapter handle:** `INF-03`.

Model selection is a systems test. A model can load and still be unusable. It can answer questions and still fail as a router. It can fit at a short context and fail when real history is loaded. It can be fast when warm and painfully slow after idle unload.

### Separate model roles

Do not force one model to win every category:

- **Router:** predictable tool selection, valid structured output, low latency.
- **General assistant:** good instruction following and conversation quality.
- **Reasoning/coding specialist:** deeper work where slower responses are acceptable.
- **Embedding model:** useful retrieval quality at sustainable indexing cost.
- **Speech models:** time to first audio and continuity matter more than benchmark prestige.

For GPU sizing, compare the quantized model artifact with available VRAM, then leave headroom for runtime overhead, context cache, display use, and concurrent services. If the model partly offloads to system RAM, measure the resulting latency instead of assuming it is acceptable. Disk capacity only answers whether the artifact can be stored.

### Minimum benchmark protocol

Keep the working baseline. Add one candidate. Run identical tests at identical settings:

1. cold start and model load time;
2. warm time to first token;
3. steady generation rate;
4. short and target-length context;
5. peak VRAM and system RAM;
6. strict JSON success rate;
7. correct tool selection;
8. refusal of tools outside the allowed set;
9. one real domain task;
10. recovery after malformed output or timeout.

Use a small router contract:

```json
{
  "tool": "answer_directly",
  "reason": "one short sentence",
  "params": {}
}
```

Test at least three allowed actions, an ambiguous request, a request that should use no tool, and a malicious request that attempts to select an unavailable tool. Validate the JSON in code. "It looked right" is not a pass.

Record results in a compact matrix:

```text
candidate:
quantization:
runtime:
context tested:
cold load:
warm first token:
generation rate:
peak VRAM:
peak RAM:
valid structured outputs: __ / __
correct route choices: __ / __
timeouts/errors:
decision: keep / specialist only / reject
```

For speech, add first-transcript latency, first-audio latency, interruption behavior, and long-response continuity. For embeddings, test retrieval, not just indexing speed.

### Exercise: run a one-candidate bakeoff

Create `10-MODEL-FIT-REPORT.md`. Compare the baseline with one candidate. Preserve the baseline until the candidate passes the role-specific gate. If neither passes, keep the system unchanged and refine the requirement.

### Agent checkpoint prompt

```text
Use 08-HARDWARE-INVENTORY.md and help me create 10-MODEL-FIT-REPORT.md.
Define separate acceptance gates for router, general assistant, specialist,
embedding, and speech roles that I actually need. Compare my working baseline
with only one new candidate. Give me repeatable commands or requests, a result
capture template, and validation logic for structured output. Do not delete
models or change the default route. Reject conclusions that lack cold/warm,
target-context, memory, error, and role-specific evidence. End with keep,
specialist-only, or reject and explain the measured reason.
```

**Produced artifact:** `10-MODEL-FIT-REPORT.md`

**Done when:** one candidate has been tested against the actual role, the baseline still works, resource use is measured, and the decision is reproducible.

### Apply the accepted OS evidence

Use OS-04 through OS-07 for process, scheduling, capacity, and pressure evidence. This chapter applies those records to model fit without redefining their host semantics.


## 45. Design State, Storage, Backup, and Restore

> **Chapter handle:** `INF-04`.

An agent is not only a model. Its valuable state may include sessions, task history, memory, documents, vector indexes, workspace files, configuration, and encryption material. If you cannot identify that state, you cannot back it up.

### Classify data before choosing storage

Use four classes:

1. **Authoritative state:** databases, approved memory, source documents, manifests, and configuration.
2. **Secret-bearing state:** credential vaults, session material, encryption keys, and provider tokens.
3. **Generated but valuable:** reports, approved artifacts, indexes that are expensive to rebuild.
4. **Re-derivable cache:** downloaded metadata, temporary extractions, model caches available elsewhere, and disposable logs.

Keep latency-critical runtime files close to compute. Put bulk documents and backup archives on capacity-oriented storage. Do not let model downloads consume the space required for databases, logs, or rollback archives.

### Build the backup contract

A recovery-ready backup process follows this sequence:

```text
inventory state
-> quiesce or transaction-safe database copy
-> archive approved paths
-> encrypt
-> write to separate storage
-> verify archive
-> record timestamp/hash/version
-> test restore in isolation
```

For SQLite, use SQLite's backup mechanism rather than copying a database during writes. A backup that contains the encryption key and encrypted vault should still be treated like a password. Keep it private and encrypt the destination.

Restore must be deliberately harder than snapshot:

1. verify the archive without extracting;
2. reject absolute paths, parent traversal, and unsafe links;
3. confirm application version compatibility;
4. stop or isolate writers;
5. rename current state to a timestamped pre-restore location;
6. extract only into the approved state directory;
7. verify ownership and permissions;
8. start the service;
9. run and record health, authentication, retrieval, and workflow checks;
10. keep pre-restore state until acceptance.

Container-managed volumes require explicit treatment. A host bind mount may be captured by a host backup, while a named volume may not. Inventory both.

### Exercise: perform a restore drill

Create `11-DATA-AND-RECOVERY.md` containing the data classification, storage placement, backup schedule, retention, encryption plan, and restore procedure. Then restore a backup into an isolated test directory or disposable service instance. Do not make the first restore test against live state.

Generalized example:

> Nightly backups include the application database, reviewed memory, configuration, and documents. Large temporary research output and rebuildable embeddings are excluded. A weekly encrypted copy leaves the primary host. Once per quarter, the newest archive is restored into an isolated instance and checked through login, retrieval, and one tool call.

### Agent checkpoint prompt

```text
Act as my backup and recovery designer. Inventory the state used by my agent
stack and classify it as authoritative, secret-bearing, valuable generated,
or re-derivable. Identify bind mounts, named volumes, databases, documents,
memory, indexes, model files, and configuration without printing secret values.
Produce 11-DATA-AND-RECOVERY.md with storage placement, encrypted backup,
retention, verification, and an isolated restore drill. Require a reversible
pre-restore rename and reject unsafe archive paths. Do not perform a live
restore or delete anything. End with evidence required to prove recovery.
```

**Produced artifact:** `11-DATA-AND-RECOVERY.md`

**Done when:** authoritative state is fully named, backups leave the primary failure domain, archive integrity is checked, and an isolated restore has completed with recorded health, authentication, retrieval, and workflow checks. Until then, report the status as **backup verified; restore unproven**.

### Apply the accepted OS evidence

Use OS-11 through OS-13 and OS-19 for storage, filesystem, publication, maintenance, and recovery evidence. This chapter owns application-state recovery and the buyer-known-answer restore.


## 46. Deploy Containers and Services Safely

> **Chapter handle:** `INF-05`.

Containers simplify packaging; they do not create security or backups automatically. Use the smallest deployment that can be understood and recovered.

Hostinger's current VPS selector offers three useful starting paths. Choose a [plain Linux or preconfigured application image](https://www.hostinger.com/support/1583571-what-are-the-available-operating-systems-for-vps-at-hostinger/) for maximum control, a panel such as Coolify, Dokploy, or CloudPanel for easier administration, or Ubuntu with Docker and the [changing Docker application catalog](https://www.hostinger.com/support/hostinger-docker-catalog-applications/) for faster validation. At package review, that catalog covered more than 1,000 entries across agent and AI tools, workflow automation, private cloud and media, business systems, databases, developer platforms, monitoring, and security. Representative choices included Ollama, Open WebUI, Flowise, n8n, Windmill, Nextcloud, Immich, Chatwoot, WordPress, WooCommerce, PostgreSQL, Qdrant, Grafana, Uptime Kuma, Authentik, and Vaultwarden. Catalog breadth is a menu, not proof that every service belongs on one server or fits the smallest plan.

At checkout, eligible new KVM purchases of 12 months or longer [may include one year of an eligible domain](https://www.hostinger.com/support/1583407-how-to-register-a-domain-for-free-at-hostinger/). Confirm the extension, claim deadline, and renewal price in the live cart; some panels also require a separate license. The VPS remains [a self-managed software environment](https://www.hostinger.com/support/8852150-what-is-a-self-managed-vps-at-hostinger/): templates reduce installation work, but they do not replace sizing, DNS and TLS, secrets, firewall rules, persistence, backups, updates, monitoring, or restore testing.

For a hosted deployment, use the same runbook and acceptance gates. Review the direct Hostinger affiliate carts for [KVM 1](https://www.hostinger.com/cart?product=vps%3Avps_kvm_1&period=12&referral_type=cart_link&REFERRALCODE=ZUWMADPANOFE&referral_id=0199a491-d783-7057-85d2-27de6e01e2c5), [KVM 2](https://www.hostinger.com/cart?product=vps%3Avps_kvm_2&period=12&referral_type=cart_link&REFERRALCODE=ZUWMADPANOFE&referral_id=0199a492-26cf-7333-b6d7-692e17bf8ce1), [KVM 4](https://www.hostinger.com/cart?product=vps%3Avps_kvm_4&period=12&referral_type=cart_link&REFERRALCODE=ZUWMADPANOFE&referral_id=0199a492-531e-70d3-83f5-e28eb919466d), and [KVM 8](https://www.hostinger.com/cart?product=vps%3Avps_kvm_8&period=12&referral_type=cart_link&REFERRALCODE=ZUWMADPANOFE&referral_id=0199a492-7ce9-70fb-b96c-2184abc56764) only after the target workload and minimum capacity are documented.

A generalized private service pattern:

```yaml
services:
  orchestrator:
    image: your-reviewed-image:version
    user: "10001:10001"
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp
    env_file: .env
    restart: unless-stopped
    volumes:
      - ./state:/app/state
      - ./config:/app/config:ro
    networks:
      - private
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3

  model:
    image: your-model-runtime:version
    user: "10001:10001"
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp
    volumes:
      - ./models:/models:ro
    networks:
      - private

networks:
  private:
    internal: true
```

This is a pattern, not a drop-in production file. Pin reviewed versions, document device access, run as an unprivileged user, keep the root filesystem and configuration read-only, drop capabilities, prevent privilege escalation, persist only named state, and add resource limits when contention matters. Verify that each image supports the assigned user and explicitly mounted writable paths; document and isolate any required exception. Avoid host networking, privileged mode, container-engine sockets, and broad host filesystem mounts unless a reviewed requirement proves them necessary.

The internal network also blocks outbound internet access. If a documented dependency requires egress, attach only the service that needs it to a separate egress network, constrain destinations with the host firewall or an authenticated proxy, and test both the allowed path and denial of unrelated destinations. Do not give the entire private service network unrestricted egress for convenience.

### Safe deployment sequence

1. record current version, health, and file hashes;
2. snapshot authoritative state;
3. save the current deploy definition;
4. validate configuration without starting;
5. build or pull a pinned version;
6. deploy only the affected service;
7. wait for its health check;
8. inspect recent logs for new errors;
9. test unauthenticated rejection;
10. test authenticated health and one exact model/tool path;
11. compare persistent state and ownership;
12. keep rollback until user acceptance.

After an approved authorization or connector change, identify and restart only affected persistent clients that are proven to cache the changed state. For example, a dashboard may maintain its own tool connection even when the gateway has restarted. Verify each affected surface independently.

### Exercise: create a reversible release

Create `13-DEPLOYMENT-RUNBOOK.md` with the exact preflight, deploy, verification, rollback, and acceptance commands for your stack. Use placeholders for secrets and environment-specific values. Practice the rollback on a noncritical release.

### Agent checkpoint prompt

```text
Act as my deployment reviewer. Using the artifacts created so far, produce
13-DEPLOYMENT-RUNBOOK.md for the smallest current stack. Prefer existing
platform features and pinned containers or system services. Define persistent
state, read-only config, unprivileged identities, internal networking,
health checks, log checks, authentication rejection, one real smoke test,
and rollback. Flag privileged mode, host networking, engine sockets, public
ports, broad mounts, floating versions, and unbacked volumes. Do not deploy,
restart, pull, or modify anything. Stop at an approval checkpoint.
```

**Produced artifact:** `13-DEPLOYMENT-RUNBOOK.md`

**Done when:** the release can be explained, verified, and rolled back from the runbook without relying on memory.

### Apply the accepted OS evidence

Use OS-15 and OS-16 for service lifecycle, shutdown, isolation, and effective resource limits. This chapter owns the reversible deployment record.


## 47. Make Health, Observability, and Incidents Truthful

> **Chapter handle:** `INF-06`.

A beautiful dashboard with untrusted data is decoration. Start with a small collector contract:

```text
collector input:
  inventory reference
  credential reference
  last successful run

collector output:
  metric samples
  normalized events
  collector health
  observed timestamp
  source timestamp
```

Collectors should use read-only credentials, have per-source timeouts and retry limits, redact errors before persistence, and be independently disableable. When a collector fails, preserve the last good result and mark it stale. Never turn "no new data" into "everything is healthy."

Normalize raw events before creating incidents. An incident needs:

- stable deduplication key;
- affected asset or workflow;
- severity and confidence;
- first and last observation;
- linked source evidence;
- current status;
- acknowledgement and notes;
- recommended review step;
- resolution evidence.

Use an explicit lifecycle:

```text
OPEN -> ACKNOWLEDGED -> INVESTIGATING -> RESOLVED
   \            \                         |
    +----------> SUPPRESSED <-------------+

A resolved incident may reopen when the same dedupe key returns
after the configured cooldown.
```

Thresholds prevent one transient failure from becoming an emergency. Examples include three consecutive endpoint failures, certificate expiry inside a defined window, unexpected DNS change, repeated authentication failures, stale backups, or two consecutive collector failures. Tune thresholds with real data before notifications.

Response maturity should advance slowly:

1. read-only evidence;
2. recommended runbook;
3. dry-run payload showing the exact proposed action;
4. manual approval;
5. narrow automation with audit, suppression, and rollback.

### Exercise: define five useful incidents

Create `14-OBSERVABILITY-AND-INCIDENTS.md`. Start with no more than five incidents that would genuinely change what you do. Include source, threshold, dedupe key, severity, evidence, runbook, and test method for each.

### Agent checkpoint prompt

```text
Act as my observability architect. Create
14-OBSERVABILITY-AND-INCIDENTS.md sized to the current stack and operating
needs. Define a normalized collector contract, stale-data behavior,
timeouts, retries, redaction, and source health. Propose no more than five
actionable incident rules with thresholds, dedupe keys, evidence, lifecycle,
and manual runbooks. Keep all collectors read-only and all response actions
recommendation or dry-run only. Include tests that prove a failed collector
cannot make the dashboard falsely healthy.
```

**Produced artifact:** `14-OBSERVABILITY-AND-INCIDENTS.md`

**Done when:** source failure is visible, stale data is honest, incidents deduplicate, and no monitoring component can mutate infrastructure.

### Apply the accepted OS evidence

Use OS-10 and OS-18 for device, queue, pressure, performance, and feedback evidence. This chapter owns operational health, alerting, and incident handoff.


## 48. Build and Evaluate Retrieval Before Calling It Memory

> **Chapter handle:** `INF-07`.

An agent becomes less useful when every transcript and document is stuffed into durable memory. Keep two layers:

- **Searchable archive:** documents, transcripts, handovers, logs, and source evidence.
- **Compact memory:** reviewed facts, preferences, decisions, and constraints.

Use a source-neutral ingestion path:

```text
source export
-> source-specific adapter
-> normalized manifest
-> preview and duplicate check
-> archive ingestion
-> retrieval test
-> reviewed memory candidates
```

Each item should carry provenance such as source title, path or record identifier, timestamp, content hash, and sensitivity. Metadata-only ingestion is useful when a transcript is too private or large to embed. Skip credentials by default.

### Prove retrieval with a small corpus

Do not begin by indexing every drive. Select a small approved collection with known answers. Run at least ten real queries:

```text
query
-> top five chunks
-> source title/date/reference
-> short answer with citations
```

For each query, record whether the obvious source appears in the top five, whether another project's data leaked into results, and whether the final answer cites the evidence it used. If retrieval fails, adjust document boundaries, chunking, metadata, or filters before changing embedding models or vector databases.

Only add a heavier vector platform when a real requirement appears: large-scale filtering, hybrid search, replication, migration, multi-tenant isolation, or operational throughput. A new framework is not a substitute for tested retrieval.

### Exercise: create a retrieval acceptance set

Create `15-KNOWLEDGE-AND-RAG.md` with corpus scope, sensitivity rules, manifest fields, chunking assumptions, ten test questions, expected sources, leakage tests, and the criteria for promoting a retrieved fact into compact memory.

### Agent checkpoint prompt

```text
Act as my knowledge and retrieval engineer. Help me create
15-KNOWLEDGE-AND-RAG.md. Separate searchable archive material from compact
reviewed memory. Design a source-neutral manifest with provenance, timestamp,
hash, sensitivity, and optional metadata-only handling. Select a small approved
pilot corpus and write ten known-answer retrieval tests using top-five chunks
and citations, including cross-project leakage checks. Prefer my existing
retrieval components. Do not ingest my whole filesystem, import credentials,
or recommend a new framework until the pilot identifies a specific limitation.
```

**Produced artifact:** `15-KNOWLEDGE-AND-RAG.md`

**Done when:** the pilot retrieves known sources, answers cite evidence, private scopes do not leak, and memory candidates require review.


## 49. Choose Instructions, Retrieval, Tools, or Fine-Tuning

> **Chapter handle:** `INF-08`.

When the system fails, begin below the application and move upward. Random restarts destroy evidence.

### Failure-diagnosis ladder

1. **Power and host:** Is the machine running, supplied with stable power, and free of storage or memory pressure?
2. **Network:** Is local networking healthy? Is the private overlay connected? Is name resolution correct?
3. **Service manager/container runtime:** Is the exact unit or container active? Did it restart?
4. **Recent logs:** What changed immediately before the failure? Are errors current or historical?
5. **Configuration:** Does validation pass? Are required variable names present without printing values?
6. **Ownership and permissions:** Can the service identity read only the files it should?
7. **Dependency health:** Can the orchestrator reach the model, database, vector store, and tool broker?
8. **Authentication:** Does an unauthenticated request fail? Does an authenticated request succeed?
9. **Exact workflow:** Can one bounded model, retrieval, or tool request complete?
10. **User acceptance:** Does the real browser, microphone, file download, or business workflow behave correctly?

Restart only the failed layer after evidence is captured. Then repeat its health, authentication, and workflow checks. Never overwrite task history. If a provider result arrives after a local timeout or failure, append a reconciliation event, verify the provider's external state before retrying, and record the final external disposition separately from the original task outcome. Give long-running tasks progress events, cancellation, questions, and a terminal timeout.

### Staged rollout

Use this progression:

```text
Stage 0: inventory and written boundaries
Stage 1: local interface + one model
Stage 2: private authenticated access
Stage 3: persistent sessions and task state
Stage 4: small retrieval corpus
Stage 5: read-only telemetry and incidents
Stage 6: one specialist worker
Stage 7: dry-run tools
Stage 8: one-time approved writes with readback
Stage 9: narrow audited automation
Stage 10: voice, visual polish, and scale
```

Every stage needs an acceptance file containing:

- scope;
- preconditions;
- exact test;
- expected result;
- observed result;
- logs or evidence reference;
- rollback;
- unresolved risks;
- human sign-off when physical or external behavior matters.

Keep the previous accepted stage available as rollback. Do not call a release complete because automated tests passed if the promise includes real audio, remote access, file delivery, payment, or another external surface. Test the promise.

### Exercise: create the release gate

Create `16-ROLLOUT-AND-RECOVERY.md`. Mark the current stage honestly. List only the next stage's required changes and acceptance tests. Add a stop condition for resource pressure, security uncertainty, data loss risk, or an unproven restore.

### Agent checkpoint prompt

```text
Use all prior artifacts and act as my release and recovery operator. Produce
16-ROLLOUT-AND-RECOVERY.md. Identify my current accepted stage, the smallest
next stage, preconditions, exact tests, expected and observed results,
evidence, rollback, stop conditions, and human acceptance. Include the
power-to-workflow diagnosis ladder, preserve task history, and reconcile late
provider results through external-state readback before any retry.
Do not broaden scope, automate writes, restart services, or declare completion
from automated evidence when the promised behavior requires a real external
test. End with one next action and one rollback action.
```

**Produced artifact:** `16-ROLLOUT-AND-RECOVERY.md`

**Done when:** the current capability is stated honestly, the next change is bounded, rollback is ready, and the user has personally tested every part of the promise that automation cannot prove.

## The Operating Rule That Holds It Together

The system becomes agentic through controlled capability, not maximum access. A dependable agent knows what it can read, what it may propose, what requires approval, where its evidence came from, how to report uncertainty, and how to recover after failure.

At the end of each work session, update the relevant artifact and leave a handover containing:

```text
current accepted state:
what changed:
what was verified:
what was not verified:
known risks:
rollback:
one next action:
```

That simple discipline prevents the next agent session from rebuilding context through guesswork. It also turns your infrastructure into something you can maintain, explain, migrate, and improve without depending on one long chat or one person's memory.

Build the smallest working layer. Test it under real conditions. Preserve the last good state. Then earn the next layer.

### Promote the system by evidence

At the end of an infrastructure stage, create a one-page promotion record. It
should name the capability that now works, the real test that proved it, the
accepted resource cost, the recovery evidence, the remaining risk, and the
next condition that would justify expansion.

Do not promote a stage because every planned task was completed. Promote it
because the promised behavior works and the operating burden remains
acceptable. A smaller system that can be restored and explained is more useful
than a larger system whose state depends on memory.

Use this closeout prompt:

```text
Close the current infrastructure stage from evidence.

Read STATUS.md, the active ticket, the relevant artifacts, and minimized test
evidence. Return:
- promised capability;
- observed result and authoritative readback;
- resource and maintenance cost;
- restore or rollback evidence;
- unresolved risk;
- owner acceptance still required;
- promotion decision: PASS, HOLD, or ROLLBACK;
- one next action.

Do not convert an untested backup into a proven restore. Do not convert a
healthy process into a verified user outcome. Save the reviewed result as the
stage promotion record and update HANDOVER.md.
```

When the answer is `HOLD`, the system is still doing its job: it has made the
gap visible before the next layer compounds it.
