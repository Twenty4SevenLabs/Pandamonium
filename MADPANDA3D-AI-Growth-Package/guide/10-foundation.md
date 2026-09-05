# Part I - Requirements Before Tools

## 4. Inventory the People, Systems, Data, and Workflows

> **Chapter handle:** `FND-01`.

Inventory the current environment before shopping, migrating, or connecting tools.

### Step 1: Record the people and operating reality

Record who uses and maintains the system, who approves purchases and external actions, available maintenance time, who else can recover it, and what happens when the primary operator is unavailable.

A solo operator can choose differently from a team needing simple recovery.

### Step 2: Inventory hardware

For each computer, server, storage device, and important network device, record:

- role, CPU, memory, accelerator, storage, and network capacity;
- operating system or platform;
- age, warranty status, and known reliability issues;
- power, heat, and noise impact when known; and
- whether it can be unavailable for maintenance.

Capture enough detail to test whether an existing device can run the first workload.

### Step 3: Inventory services and data

Record each important service or data collection:

- business job;
- current location;
- approximate size and growth;
- sensitivity;
- owner;
- current backup;
- last restore test;
- external dependencies;
- acceptable outage;
- current pain point.

### Step 4: Inventory access and exposure

Describe how you reach the systems:

- local network only;
- private remote-access network;
- public domain or public address;
- vendor-hosted login;
- mobile device;
- shared account;
- individual account with roles.

Mark public entry points and anything that depends on a single device, person, subscription, or credential.

### Step 5: Inventory business workflows

List the work you expect AI or automation to improve. Examples:

- researching prospects and preparing a review;
- drafting CRM follow-up after owner approval;
- answering support questions from approved documentation;
- turning meeting notes into tasks;
- checking websites or services and opening a ticket when evidence shows a problem;
- producing a weekly operating report;
- organizing owned knowledge for later retrieval.

For each workflow, name its trigger, owner, tools, output, frequency, recurring failure, and proof of completion.

### Compact example

```text
Device: Primary workstation
Observed: 12 CPU cores, 64 GB memory, 12 GB GPU memory, 2 TB free
Constraint: daily work; unavailable for reboots during client calls
Candidate first-stage role: document retrieval and one local background worker
Unknown: sustained thermal behavior under a two-hour workload

Workflow: Weekly client reporting
Trigger: Friday morning
Inputs: task system, analytics export, delivery notes
Desired result: evidence-linked draft reviewed by the account owner
```

### Current-state inventory prompt

```text
Help me build artifacts/CURRENT-STATE-INVENTORY.md.

Interview me in this order:
1. people, ownership, and maintenance capacity;
2. computers, servers, storage, and network equipment;
3. services, subscriptions, and important data;
4. access paths and public exposure;
5. current AI tools and integrations;
6. business workflows I want to improve;
7. known failures, single points of failure, and missing evidence.

Ask one question at a time. Do not recommend purchases yet. Mark each statement
OBSERVED, OWNER-STATED, RESEARCHED, ASSUMPTION, or UNKNOWN. When the interview is complete,
produce:
- a concise asset inventory;
- a service and data inventory;
- a workflow inventory;
- existing strengths worth reusing;
- immediate risks that need confirmation;
- questions that must be answered before architecture selection.

End with a proposed update to STATUS.md. Wait for my corrections before marking
the inventory complete.
```

**Produced artifact:** `artifacts/CURRENT-STATE-INVENTORY.md`.

**Completion check**

- Every candidate device has enough capacity information for an initial fit decision.
- Important data has an owner, location, sensitivity, backup status, and recovery unknowns.
- Public and private access paths are distinguishable.
- At least one business workflow is defined from trigger to proof of completion.
- Unknowns are explicit rather than filled with guesses.

**Next step:** convert goals into measurable workloads and ownership constraints.

---


## 5. Turn Outcomes Into Workloads and Constraints

> **Chapter handle:** `FND-02`.

Start with outcomes. “Run AI locally” is a preference; “search approved project
knowledge locally” is an outcome. “Prepare a daily lead queue for owner review”
is testable.

### Step 1: Rank three outcomes

For each outcome, write:

- who benefits and what changes;
- frequency and success evidence;
- value of success and cost of error; and
- whether a human approves the final action.

Limit the first plan to three ranked outcomes. Everything else belongs in `BACKLOG.md`.

### Step 2: Translate outcomes into workloads

Break each outcome into units the infrastructure must support:

- interactive or background operation;
- retrieval sources and local or hosted model calls;
- media type, data size, frequency, and duration;
- concurrent users and workers;
- integrations and data changes; and
- expected 12-month growth.

Separate steady workloads from occasional bursts.

### Step 3: Classify privacy and action risk

Use four practical levels:

1. **Open**  -  intended for public use.
2. **Project-private**  -  business material limited to approved users, accounts, and systems.
3. **Confidential**  -  customer, financial, operational, or personal data requiring restricted access and careful logging.
4. **Restricted action**  -  an operation that can send, publish, purchase, delete, change access, move money, or materially affect another person or system.

A workflow may read project-private data but end with a restricted action. Classify the data and action separately.

### Step 4: Define uptime and recovery

For each outcome, decide:

- **availability window**  -  when it needs to work;
- **maximum tolerable outage**  -  how long the business can operate without it;
- **recovery time objective**  -  how quickly you aim to restore the service;
- **recovery point objective**  -  how much recent data could be recreated or lost;
- **manual fallback**  -  how the work continues while the system is down.

Match availability to business need instead of doubling noncritical complexity.

### Step 5: Set the true budget

Record:

- initial purchase and monthly service ceilings;
- electricity, backup, API, and software allowances;
- replacement and repair reserve;
- value of maintenance time; and
- a reserve for compatibility surprises.

Existing equipment still has power, heat, wear, and availability costs.

### Step 6: Set physical and maintenance limits

Decide:

- acceptable noise, continuous power, heat, ventilation, and space;
- tolerance for used hardware and replacement lead time;
- restart, maintenance, and patch windows; and
- maximum troubleshooting time before using the fallback.

### Compact example

```text
Outcome 1: Produce a reviewed daily support queue from approved documents.
Frequency: weekdays by 8:00 a.m.
Workload: retrieve from up to 20,000 text pages; draft 5-20 responses; no sending.
Data: project-private plus confidential customer messages.
Proof: queue contains source links and is approved by the support owner.
Outage tolerance: one business day.
Fallback: search documents manually and respond in the existing inbox.
Budget: use current workstation first; up to $40/month for approved services.
Physical limit: no always-on high-noise server in the office.
```

### Needs-assessment prompt

```text
Help me create artifacts/AI-SYSTEM-NEEDS-BRIEF.md from
artifacts/CURRENT-STATE-INVENTORY.md.

First, help me choose and rank no more than three outcomes. For each outcome,
translate the desired result into workload, frequency, concurrency, data,
integrations, writes, success evidence, failure cost, and approval needs.

Then interview me about:
- privacy level and restricted actions;
- availability, recovery time, recovery point, and manual fallback;
- initial, monthly, energy, replacement, and maintenance budgets;
- power, heat, noise, space, and maintenance constraints;
- expected 12-month growth.

Do not recommend products yet. Challenge vague goals and unnecessary uptime.
Show conflicts explicitly, such as a low budget combined with high availability
or a quiet office combined with sustained high-power compute. Finish with:
1. ranked outcomes;
2. workload profiles;
3. hard constraints;
4. preferences;
5. disqualifying conditions;
6. unresolved questions;
7. acceptance tests for the first stage.

Wait for my approval before updating STATUS.md.
```

**Produced artifact:** `artifacts/AI-SYSTEM-NEEDS-BRIEF.md`.

**Completion check**

- No more than three outcomes define the first plan.
- Each outcome has a workload, owner, evidence source, and failure cost.
- Data sensitivity and action authority are classified separately.
- Recovery needs and a manual fallback are written.
- Initial, monthly, physical, and maintenance limits are explicit.
- Conflicts and unknowns are visible.

**Next step:** score the current infrastructure and agent operating model independently.

---


## 6. Score Infrastructure and Agent Readiness

> **Chapter handle:** `FND-03`.

Infrastructure and agent maturity are separate. Powerful hardware can still host
an unreliable workflow.

Score each track from 0 to 5. Choose the lowest description that is consistently true.

### Infrastructure track

| Stage | Description | Exit evidence |
| --- | --- | --- |
| 0  -  Ad hoc | Work runs only on a daily-use device with no inventory or recovery plan | Current-state inventory exists |
| 1  -  Stable base | One known runtime has measured capacity, persistent storage, and documented access | Representative workload runs repeatedly |
| 2  -  Recoverable | Important data is backed up independently and a restore has been tested | Dated restore evidence exists |
| 3  -  Observable | Health, capacity, freshness, failures, and dependencies can be inspected | A failure can be diagnosed from current evidence |
| 4  -  Separated | Critical roles are isolated where failure, performance, or maintenance justifies it | One role can change without taking down the whole workflow |
| 5  -  Operated | Change control, recovery, ownership, capacity review, and lifecycle replacement are routine | Monthly review and recovery records exist |

### Agent track

| Stage | Description | Exit evidence |
| --- | --- | --- |
| 0  -  Chat | Context and progress live only in the conversation | A workspace and status file exist |
| 1  -  Grounded assistant | The agent uses approved sources, instructions, and durable status | It resumes without inventing prior decisions |
| 2  -  Tool operator | Tools are inventoried and read actions are separated from writes | One tool workflow has permission and readback rules |
| 3  -  Durable worker | Tasks have stable identity, states, evidence, resume, cancel, and duplicate controls | An interrupted task can resume or fail honestly |
| 4  -  Coordinator | Bounded specialist work is delegated and independently reconciled | Duplicate external actions are prevented |
| 5  -  Business partner | Measured operating cycles run with owner approvals and exception handling | Business outcomes are reviewed against evidence |

### Scoring rule

Do not average away a missing foundation. Record:

- current infrastructure stage;
- current agent stage;
- evidence for each;
- the next exit test for each;
- which next stage most directly supports the top-ranked outcome.

Advance one stage at a time. Durable agent context may beat another machine.

### Maturity prompt

```text
Using artifacts/CURRENT-STATE-INVENTORY.md and
artifacts/AI-SYSTEM-NEEDS-BRIEF.md, score my
infrastructure and agent operating model separately from 0 to 5.

For each score:
- quote the evidence that supports it;
- identify any claimed capability that lacks evidence;
- name the next exit test;
- propose the smallest action that would pass that test;
- explain how it supports my highest-ranked outcome.

Do not average the scores. Do not advance a stage based only on hardware owned,
software installed, or tools connected. Produce artifacts/MATURITY-ASSESSMENT.md with a
recommended next stage and the reason other upgrades are deferred.
```

**Produced artifact:** `artifacts/MATURITY-ASSESSMENT.md`.

**Completion check**

- Both tracks have evidence-backed scores.
- The next exit test can be passed in a bounded project.
- The chosen next stage supports a ranked outcome.
- Deferred upgrades are recorded rather than silently discarded.

**Next step:** turn the needs brief into an architecture of responsibilities and flows.

---

### Progression evidence

The maturity score and the following progression share one owner. Do not create a second ladder.

An agent becomes more capable in stages. Each stage supplies the continuity and measurement needed by the next.

### Stage 0: Chat

The model handles questions, drafts, and exploration inside one conversation; the user supplies context each time.

### Stage 1: Grounded assistant

The model reads workspace instructions, system map, state, problems, and handover before acting.

### Stage 2: Tool operator

The model uses narrow tools with explicit prerequisites, side effects, authority, and outputs.

### Stage 3: Durable worker

The model works from a ticket, records minimized evidence, leaves a handover, and resumes after interruption.

### Stage 4: Coordinated specialist team

A coordinator routes bounded work packages to specialists with distinct context and authority. Completion requires independent readback.

### Stage 5: Measured business partner

The system monitors defined conditions, performs approved low-risk work, escalates consequential decisions, and measures outcomes. The owner defines intent, authority, and success.

Build upward from the stage that solves the current workflow. Additional autonomy is earned through reliable state, bounded authority, and measured results.

### Exercise: Choose your first progression

1. List five weekly tasks and classify each as `answer`, `prepare`, `read`, `write`, `publish`, `spend`, or `delete`.
2. Circle one that is frequent, reversible, and easy to verify.
3. Define its completion evidence.
4. Choose the lowest maturity stage that can complete it safely.

Your first target should usually be Stage 1 or Stage 2. For example, “prepare a weekly lead summary from the CRM and save a draft” is a better first slice than “automatically contact every lead.”

**Produced artifact:** `17-FIRST-VERTICAL-SLICE.md`, containing the task, trigger, required context, tools, approval boundary, expected output, and verification evidence.

### Agent checkpoint prompt

```text
Act as my agentic-systems architect. Interview me about five repeated business
tasks, then classify each task by read, prepare, write, publish, spend, or
delete risk. Recommend one small reversible vertical slice. Do not propose a
swarm or full automation. Return the trigger, required context, tools,
approval boundary, expected output, verification evidence, and the lowest
agent maturity stage that can complete it.
```

### Done when

- You can name the first workflow in one sentence.
- Its completion evidence is objective.
- Its risk class is explicit.
- You know what the agent may prepare and what still requires approval.
- You have deliberately excluded at least one unnecessary automation.

### Operating-system readiness handoff

Use OS-01 to map present, available, and proven host resources plus configured, allocated, and pressured facets. Use OS-20 for scoped host acceptance. This foundation chapter owns the readiness stage; the OS track supplies its host evidence.


## 7. Convert Needs Into Roles, Flows, and Boundaries

> **Chapter handle:** `FND-04`.

Architecture is the assignment of responsibilities, data, access, and recovery. Hardware comes after those decisions.

### Step 1: Draw the workflow flow

For each ranked outcome, write:

`trigger -> input -> processing -> review or approval -> external action -> readback -> record`

Example:

```text
Weekday schedule
-> approved support inbox and knowledge sources
-> retrieve relevant passages and draft queue
-> support owner reviews
-> owner sends through existing inbox
-> inbox confirms sent state
-> ticket and weekly metric are updated
```

### Step 2: Assign system roles

Use only the roles the workload requires:

- **Access edge**  -  private or public entry point and identity check.
- **Agent control**  -  task state, routing, permissions, approvals, and coordination.
- **Compute**  -  model inference or other CPU/GPU processing.
- **Knowledge and state**  -  documents, indexes, databases, working files, and backups.
- **Integration services**  -  bounded connections to business tools and providers.
- **Observability**  -  health, capacity, freshness, errors, and evidence.
- **Operator workstation**  -  owner review, development, and manual fallback.

Roles can share one machine until availability, performance, maintenance, or recovery justifies separation.

Implementation source remains in a separate repository. Record its location,
current branch or release, and permitted change boundary in `SYSTEM-MAP.md`.

### Step 3: Place data deliberately

For each data set, decide:

- authoritative source and any working copy or index;
- permitted readers and writers;
- retention, backup, and restore order; and
- deletion responsibility and evidence required after a change.

An index used for retrieval is not automatically the authoritative document store. A snapshot on the same storage is not automatically an independent backup.

### Step 4: Define trust and approval boundaries

Mark where identity is checked, where credentials are used, where restricted data enters, where an external action can occur, and where a human approval is required.

Design the first stage so the agent can prepare useful work before it gains authority to send, publish, delete, purchase, or change access.

### Step 5: Define failure boundaries

Ask:

- What happens if compute or one integration is unavailable?
- Can authoritative data still be reached and work continue manually?
- Is state preserved across restart?
- What is restored first, and what proves recovery?

### Step 6: Size from measured demand

Map the workload to:

- CPU, accelerator, memory, and video-memory demand;
- working storage, growth, and backup capacity;
- network and concurrency needs;
- continuous versus burst operation; and
- API rate and spending limits.

Use ranges until a benchmark or current provider specification supports a precise number.

### Step 7: Define the first deployment slice

The first slice should prove one complete path. For example:

1. ingest a small approved document set;
2. retrieve sources and draft one output;
3. require owner review and record evidence;
4. restart the service; and
5. confirm state and retrieval still work.

Do not replace an accepted path until an independent backup is identified, a
restore drill passes, and rollback or forward recovery is documented.

### Architecture prompt

```text
Turn my approved needs brief into artifacts/TARGET-ARCHITECTURE.md.

For each ranked outcome:
1. draw the trigger-to-readback flow;
2. assign only the required access, control, compute, knowledge/state,
   integration, observability, and workstation roles;
3. identify authoritative data, working copies, readers, writers, retention,
   backup, and restore order;
4. mark identity, credential, approval, and external-action boundaries;
5. describe failure behavior and manual fallback;
6. estimate capacity as ranges tied to workload evidence;
7. define the smallest end-to-end deployment slice and its acceptance test.

Allow multiple roles on one machine when that is sufficient. Recommend
separation only with a stated reason and promotion trigger. Label unknowns and
show me the architecture before making product or parts recommendations.
```

**Produced artifact:** `artifacts/TARGET-ARCHITECTURE.md`.

**Completion check**

- Every component supports a ranked outcome.
- Every important flow ends with readback and a record.
- Authoritative data and working copies are distinguishable.
- Restricted actions have an owner and approval point.
- Failure behavior and manual fallback are described.
- The first deployment slice is smaller than the full target.

**Next step:** choose the smallest reference pattern that can host the first slice.

---


## 8. Compare Workstation, Single-Node, and Hybrid Patterns

> **Chapter handle:** `FND-05`.

These patterns describe role placement, not brands. Adapt one.

### Pattern A: Workstation-first

**Best fit:** one operator, early workloads, limited always-on needs, or
benchmarking before purchase.

```text
Operator
   |
Primary workstation
   |- agent workspace and control
   |- approved knowledge/index
   |- local or hosted-model client
   |- one bounded integration worker
   `- local observability
          |
   independent backup target
```

**Implementation sequence**

1. Measure free memory, storage, thermals, and current workload impact.
2. Create the workspace and a dedicated data directory.
3. Run one representative workflow and record resource use and quality.
4. Add an independent backup, then test restart and restore.
5. Decide whether the workstation can support the desired schedule.

**Strengths:** low cost, fast learning, maximum reuse.

**Tradeoffs:** daily work competes with background tasks; reboots interrupt service.

**Promotion triggers:** sustained resource contention, need for unattended schedules, unacceptable workstation downtime, storage growth, or a second user who depends on the service.

**Compact example:** a consultant uses an existing workstation for document retrieval and scheduled report drafting. Sending remains manual. Measurements later justify moving only retrieval to an always-on node.

### Pattern B: Starter single-node

**Best fit:** a few always-on services, one or two users, moderate storage, and
separation from daily work.

```text
Operator devices
      |
private access
      |
single service node
   |- agent control
   |- application services
   |- compute within measured limits
   |- working data and indexes
   `- monitoring
      |
independent backup destination
```

**Implementation sequence**

1. Define the node’s service and maintenance window.
2. Install a stable host platform and persistent storage.
3. Deploy one service with persistent state and health checks.
4. Configure private access and individual identity.
5. Back up configuration, workspace, and data independently.
6. Run restore and restart acceptance, then add one service at a time.

**Strengths:** simple operation, low idle complexity, free daily workstation.

**Tradeoffs:** maintenance affects all roles; compute and storage share one failure domain.

**Promotion triggers:** storage and compute compete, one service needs a different maintenance schedule, restore time grows beyond the requirement, or a failure takes down multiple important workflows.

**Compact example:** a small business runs retrieval, dashboards, tickets, and two workers on one quiet node. Media backs up separately; heavy generation stays on the workstation or an approved hosted model.

### Pattern C: Separated or hybrid

**Best fit:** important always-on services, growing storage, heavier compute,
remote users, or combined local and hosted capacity.

```text
Operator devices
      |
private access / controlled edge
      |
agent control and service layer
   |          |             |
compute    knowledge      integrations
node       and state      / providers
   \          |             /
      observability and evidence
               |
       independent backup
```

**Implementation sequence**

1. Start from a proven workstation or single-node workflow.
2. Identify the exact bottleneck or failure boundary that justifies separation.
3. Move one role while preserving the known-good path.
4. Define identity, flow, health, cost, data handling, and rollback.
5. Verify an end-to-end workflow and test that role’s failure.
6. Review capacity and provider dependence monthly.

**Strengths:** roles scale independently; storage and compute can specialize.

**Tradeoffs:** more dependencies, identity, observability, recovery work, and provider cost.

**Promotion rule:** do not choose this pattern for appearance or future possibilities. Choose it because current evidence shows a role needs independent capacity, availability, maintenance, data control, or failure isolation.

**Compact example:** an agency keeps documents and task state on controlled storage, runs coordination on an always-on node, uses separate local compute for scheduled inference, and an approved hosted model for peaks.

### Pattern-selection prompt

```text
Compare the workstation-first, starter single-node, and separated/hybrid
patterns against artifacts/CURRENT-STATE-INVENTORY.md,
artifacts/AI-SYSTEM-NEEDS-BRIEF.md, artifacts/MATURITY-ASSESSMENT.md, and
artifacts/TARGET-ARCHITECTURE.md.

For each pattern, evaluate:
- fit for the first deployment slice;
- equipment I can reuse;
- missing capacity;
- availability and recovery fit;
- power, noise, space, and maintenance fit;
- initial and monthly cost;
- failure concentration;
- complexity added;
- evidence that would trigger promotion.

Recommend the smallest pattern that passes the current acceptance tests. Show a
role-placement diagram and a phased implementation sequence. Put unneeded
future roles in BACKLOG.md. Save the reviewed decision as
artifacts/REFERENCE-PATTERN-DECISION.md and update DECISIONS.md with the reason.
```

**Produced artifact:** `artifacts/REFERENCE-PATTERN-DECISION.md`.

**Completion check**

- The selected pattern can run the first end-to-end deployment slice.
- Existing equipment is reused where it meets the requirement.
- Every planned purchase or subscription maps to a measured gap.
- Backup and recovery do not depend entirely on the same failure domain.
- Promotion triggers are evidence-based.
- Future complexity is deferred in `BACKLOG.md`.

**Next step:** use the approved pattern and needs brief to research current parts, platforms, and implementation options without changing the architecture to fit a tempting product.

---

## Foundation Complete

Before continuing, your workspace should contain:

- root controls: `AGENTS.md`, `STATUS.md`, `DECISIONS.md`, `SYSTEM-MAP.md`,
  `MEMORY.md`, `BUGS.md`, `HANDOVER.md`, and `BACKLOG.md`;
- `artifacts/CURRENT-STATE-INVENTORY.md`;
- `artifacts/AI-SYSTEM-NEEDS-BRIEF.md`;
- `artifacts/MATURITY-ASSESSMENT.md`;
- `artifacts/TARGET-ARCHITECTURE.md`; and
- `artifacts/REFERENCE-PATTERN-DECISION.md`.

If one of these is incomplete, keep the status honest and continue from that section. If all are reviewed, you now have enough information to source infrastructure from real needs and build the first verified stage without buying for an imagined future.

### Foundation handoff

Before researching products or opening implementation tickets, ask a fresh
session to review the foundation packet. A fresh review is useful because it
tests whether the artifacts carry the project without relying on the chat that
created them.

The reviewer should be able to answer:

- What outcome is ranked first, and what evidence would prove it?
- Which facts are observed, owner-stated, researched, assumed, or unknown?
- What equipment and services can be reused?
- Which pattern was selected, and why is it the smallest fit?
- What data, approval, uptime, recovery, power, noise, and maintenance limits
  shape the design?
- Which purchase or integration ideas remain deferred?
- What is the single next stage, and what would stop it?

Use this handoff prompt:

```text
Review my foundation packet as a skeptical implementation partner. Read
STATUS.md, DECISIONS.md, SYSTEM-MAP.md, BACKLOG.md, and the five foundation
artifacts. Do not redesign the system yet.

Return:
1. the first outcome and its acceptance evidence;
2. the selected reference pattern and why it fits;
3. reusable equipment and current constraints;
4. assumptions or unknowns that could change the design;
5. recovery or authority gaps that block implementation;
6. deferred purchases that should stay deferred; and
7. the smallest next-stage ticket.

Cite the artifact supporting each statement. If the files conflict, stop and
show the conflict instead of choosing silently.
```

The foundation is ready when that fresh session reaches the same design
boundary without needing the original conversation.


## 9. Foundation Capstone: Write the Build Brief

> **Chapter handle:** `FND-06`.

### Objective

Turn the accepted inventory, outcome, readiness, architecture, and pattern
decisions into one build brief for the first evidence-earning vertical slice.
The brief authorizes planning and review only. It does not authorize a
purchase, connection, deployment, data transfer, or external action.

### Required Inputs

- `FND-01` current-state inventory;
- `FND-02` ranked outcome and workload constraints;
- `FND-03` readiness score and next safe stage;
- `FND-04` roles, flows, data placement, boundaries, and failure ownership;
- `FND-05` selected starting pattern and rejected alternatives; and
- the current `ORI-02` learning-depth decision.

If one input is missing or its decision-changing fields are `UNKNOWN`, create
a blocked build brief with the first evidence task and stop. Do not fill gaps
with a preferred product or an imagined capability.

### Build Brief Contract

Use one `BLD-##` record with these sections:

1. **Outcome.** Name one user, trigger, useful result, owner, and proof.
2. **Starting state.** Reference accepted equipment, services, data, access,
   skills, and constraints. Keep evidence labels attached.
3. **First slice.** Define the smallest end-to-end path that can prove or
   disprove the architecture without depending on later features.
4. **Roles and boundaries.** Assign operator, service, model, retrieval, tool,
   state, review, and recovery roles only when required by the slice.
5. **Data and authority.** Record permitted data class, retention, owner,
   approved reads, prohibited actions, exact approval points, and safe test
   boundary.
6. **Dependencies and failure.** Name the minimum required network, identity,
   compute, storage, provider, observability, and recovery dependencies.
7. **Acceptance.** Predeclare task success, evidence references, critical
   safety gates, rollback proof, owner review, and the maximum supported
   conclusion.
8. **Deferred work.** Move attractive tools, purchases, integrations, and
   automation outside the first slice with evidence-based reopen triggers.

The first slice should cross the system once. A useful example is a fictional
or isolated request entering an approved interface, reaching one agent role,
using a bounded source or tool, producing a reviewed result, and leaving a
traceable receipt. It is not a miniature production platform.

### Promotion Gate

Assign the lowest stage that the evidence supports:

| State | Meaning | Allowed next move |
| --- | --- | --- |
| `BRIEF BLOCKED` | A required input, owner, boundary, or proof is missing | Complete the first evidence task |
| `LAB READY` | The method can be tested with fictional data or isolation | Run only the declared lab |
| `CANDIDATE READY` | A reversible candidate has complete prerequisites and review | Prepare an implementation decision |
| `IMPLEMENTATION PENDING APPROVAL` | Exact consequential changes are known but not authorized | Present the change and wait |

No foundation artifact can set `IMPLEMENTED`, `DEPLOYED`, or `PRODUCTION
READY`. Those states require downstream receipts and owner acceptance.

### Example: Harborlight Intake Slice

Harborlight wants a support-draft assistant. Its accepted inventory shows an
operator workstation, a private document set, and no approved external send.
The build brief selects a `LAB` slice: one fictional request, one approved
document excerpt, one local or isolated response candidate, two human reviews,
and no CRM write or customer contact.

The evidence goal is narrow: prove that the request, source reference,
response, score, and reviewer decision can be preserved as one packet. Network
exposure, production retrieval, customer data, automation, and outbound
delivery stay deferred. Passing the lab supports only the architecture and
evaluation method for that case.

### Agent Checkpoint Prompt

```text
Act as a build-brief editor. Read only the accepted ORI-02 and FND-01 through
FND-05 artifacts supplied for one outcome. Preserve every evidence label and
conflict. Do not research products, inspect systems, or perform an action.

Create one BUILD-BRIEF with outcome, starting state, smallest vertical slice,
roles, data boundary, authority boundary, dependencies, failure owners,
acceptance evidence, rollback requirement, deferred work, reopen triggers,
first blocker, one owner task, and state: BRIEF BLOCKED, LAB READY, CANDIDATE
READY, or IMPLEMENTATION PENDING APPROVAL.

Use UNKNOWN for missing decision-changing facts. Do not invent capacity,
compatibility, price, access, approval, privacy status, security, health, or
success. Show the complete brief and wait.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/FOUNDATION-BUILD-BRIEF.md`

### Pass Criteria

- All five foundation inputs and the route record are referenced.
- The first slice is end to end, bounded, reversible, and smaller than the
  target platform.
- Data, authority, dependencies, failure owners, acceptance, and rollback are
  explicit.
- One truthful readiness state follows from the evidence.
- Deferred work has review triggers rather than vague someday language.

### Stop Conditions

Stop for a missing outcome or owner; unresolved critical inventory conflict;
unsupported product, cost, capacity, privacy, security, access, or recovery
claim; a request to purchase, connect, deploy, migrate, send, or expose; or an
acceptance rule that cannot distinguish a passing slice from a failed one.

### Next Step

Use the build brief as the common input to networking, infrastructure,
communication, and agent chapters. Each track may deepen its own boundary, but
none may silently widen the outcome or authority.
