# Part VII - Apply It to the Business

## 70. Start With One Closed, Measured Loop

> **Chapter handle:** `BUS-01`.

A business partner does not merely create output. It helps a piece of work move
from trigger to verified result.

Use this loop:

```text
trigger
  -> collect approved context
  -> decide or recommend
  -> prepare the action
  -> obtain approval when required
  -> execute
  -> read back the result
  -> record evidence
  -> update durable state
  -> schedule the next review
```

If the workflow stops at "draft created," it is a drafting workflow. That can
still be valuable, but name it honestly. If it stops at "command returned zero,"
it is a command workflow, not a verified operating cycle. The final state should
be observable in the system that owns the truth.

### Choose the first cycle

List ten repeated tasks from the last two weeks. Score each from 1 to 5:

| Factor | 1 | 5 |
| --- | --- | --- |
| Frequency | Rare | Daily or near-daily |
| Time cost | A few minutes | Hours |
| Input clarity | Different every time | Predictable inputs |
| Result visibility | Hard to verify | Easy readback |
| Reversibility | Costly or public | Local or easily reversed |
| Business value | Convenience | Revenue, retention, or risk reduction |

The best first workflow is frequent, clear, valuable, easy to verify, and
reversible. Avoid beginning with legal decisions, mass outreach, billing
changes, credential rotation, public publishing, or deletion. Those are later
workflows after the operating system has earned trust.

### Example: inbound lead ownership

Weak automation:

```text
New form submission -> AI writes a reply.
```

Closed operating cycle:

```text
New form submission
  -> search for the CRM contact using approved identifiers
  -> check duplicate contact and opportunity state
  -> propose contact creation only when no match exists and policy permits it
  -> identify the source and requested service
  -> assign an owner
  -> draft the next message
  -> show the exact recipient, final content, channel, cost, and intended effect
  -> request per-action approval if the message will be sent
  -> send through the approved channel
  -> read back delivery status
  -> create the next task
  -> update the lead record and evidence receipt
```

The second design is not valuable because it uses more tools. It is valuable
because it preserves ownership, avoids duplicates, verifies delivery, and
leaves the next step visible.

### Build exercise

Create `28-FIRST-CYCLE.md`:

```text
Cycle name:
Business outcome:
Trigger:
Frequency:
Current owner:
Current source of truth:
Required context:
Decision:
Read-only tools:
Write tools:
Approval boundary:
Expected result:
Authoritative readback:
Evidence saved:
Failure path:
Next scheduled review:
```

### Agent checkpoint prompt

```text
Help me choose the first business cycle for my agentic system.

Ask me for ten repeated tasks from the last two weeks. Score them for frequency,
time cost, input clarity, result visibility, reversibility, and business value.
Recommend the smallest high-value cycle with a reliable readback. Map it as:

trigger -> context -> decision -> action -> approval -> result -> evidence ->
durable state -> next review

Distinguish drafting from execution and execution from verified completion.
Save the final map as 28-FIRST-CYCLE.md. Do not connect or mutate any service
yet.
```

Done when:

- the cycle has one owner and one source of truth;
- success can be read back;
- the first version has a narrow boundary;
- the approval point is explicit; and
- failure leaves a visible task instead of disappearing.


## 71. Build Skills, Plays, and Playbooks

> **Chapter handle:** `BUS-02`.

These three artifacts solve different problems.

### Skill: reusable knowledge

A skill tells an agent how to perform or evaluate a class of work. It contains
the operating method, boundaries, inputs, expected output, and checks.

Examples:

- qualify an inbound service lead;
- audit an MCP tool contract;
- prepare a weekly operations review;
- assess a product image for publishing rights;
- diagnose a failed service without changing it.

A skill should not silently grant authority. Knowing how to publish does not
mean the agent may publish.

### Play: one bounded move

A play is one repeatable action with a clear beginning and end.

Examples:

- retrieve an open lead and its latest activity;
- draft a reply for owner review;
- run a read-only service health check;
- prepare a restore drill record;
- compare the live tool catalog with the release manifest.

A useful play states:

```text
name
purpose
trigger
required inputs
allowed tools
authority
ordered steps
output
readback
failure state
```

### Playbook: an ordered operating cycle

A playbook combines plays and ends with an audit loop. The same play may appear
in several playbooks. A "retrieve contact" play can support lead response,
client onboarding, support, and reporting.

Example:

```text
Playbook: Inbound Lead Ownership

1. Read and classify the submission.
2. Locate or create the contact under the approved CRM rules.
3. Confirm owner and opportunity state.
4. Draft the reply.
5. Request approval.
6. Send after approval.
7. Read back delivery.
8. Create the next task.
9. Record evidence and update the weekly metric.
```

### The playbook acceptance rule

Every playbook needs:

- a stable run or task identifier;
- an idempotency or duplicate-control rule;
- an approval boundary;
- a terminal result;
- authoritative readback;
- a manual fallback;
- a recovery path; and
- a metric tied to the business outcome.

Do not measure only prompts, tokens, runs, or messages. Those measure activity.
For lead ownership, measure response time, percentage with a clear owner,
delivery success, overdue next tasks, qualified handoffs, and conversion by
source. For support, measure time to acknowledgment, time to resolution,
reopened issues, and unresolved blockers. For content, measure approved pieces,
publication accuracy, qualified traffic, and useful business actions.

### Build exercise

Create three files:

1. `29-FIRST-SKILL.md`
2. `29-FIRST-PLAY.md`
3. `29-FIRST-PLAYBOOK.md`

Use the smallest cycle from the previous chapter. Keep each play short enough
that a human can inspect it in a minute.

### Agent checkpoint prompt

```text
Using 28-FIRST-CYCLE.md, create:

1. a reusable skill containing the method and boundaries;
2. the smallest read-only or reversible play;
3. a playbook that closes the complete cycle.

For each artifact, state inputs, authority, allowed tools, ordered actions,
output, readback, failure state, and manual fallback. Add a stable task identity
and duplicate-control rule. End the playbook with a business outcome metric.

Save the files as 29-FIRST-SKILL.md, 29-FIRST-PLAY.md, and
29-FIRST-PLAYBOOK.md. Do not execute the playbook.
```

Done when the owner can read the three files and explain the difference between
knowledge, one action, and a complete operating cycle.


## 72. Apply Four Useful Business Patterns

> **Chapter handle:** `BUS-03`.

Use these as reference patterns, not mandatory integrations.

### Pattern A: website, lead capture, CRM, and follow-up

Outcome: every qualified inquiry has a source, owner, status, next action, and
verified response.

Minimum capability set:

- read the submitted form or inbox item;
- find a matching contact;
- inspect opportunity and task state;
- draft a reply;
- create a task;
- send only through an approved action;
- read back delivery and CRM state.

Common failure modes:

- duplicate contacts or opportunities;
- a reply with no assigned owner;
- a sent message recorded only by the agent, not the provider;
- a follow-up scheduled in two systems;
- sensitive context copied into the wrong contact;
- the agent guessing the customer's intent.

First useful version:

1. Read new inquiries.
2. Classify service, urgency, and missing information.
3. Draft the response.
4. Show the owner the exact recipient, final content, channel, cost if any, and
   intended effect.
5. Send only after per-action approval.
6. Verify delivery.
7. Create one next task in the CRM.

### Pattern B: content research, production, approval, and rights

Outcome: approved content moves from a documented source to a published asset
with traceable rights and claims.

Minimum state:

- source URL or owned-source path;
- author and retrieval date;
- content brief;
- asset ownership or license;
- factual claims requiring verification;
- draft status;
- reviewer;
- publication target;
- approval and publication evidence.

The agent can automate research organization, outlining, drafting, metadata,
and preflight review before it earns publication authority. Keep the original
source and the created asset linked through a production ledger.

First useful version:

1. Collect approved sources.
2. Build a brief with audience, query, claim, proof, and CTA.
3. Draft one asset.
4. Run a claims and rights review.
5. Produce a publication-ready package.
6. Stop for owner approval.
7. After an approved publication, read back the live URL and metadata.

### Pattern C: support and maintenance

Outcome: every issue becomes a reproducible ticket with a truthful terminal
state.

Minimum ticket:

```text
reported behavior
expected behavior
affected service
time window
safe reproduction
current evidence
severity
authority
editable boundary
acceptance checks
rollback path
state
owner
```

Start with read-only triage. The agent should identify the smallest affected
component and separate a user symptom from the technical cause. A successful
command is not resolution; the customer-visible path and the service readback
must agree.

### Pattern D: client onboarding and reporting

Outcome: the promised scope becomes owned tasks, verified delivery, and a
reviewable report.

Minimum sequence:

1. Capture the signed or approved scope.
2. Convert deliverables into tasks with owners and acceptance criteria.
3. Record dependencies and customer-required inputs.
4. Track evidence during delivery.
5. Build the report from source systems.
6. Review claims and unresolved items.
7. Deliver through the agreed channel.
8. Verify access or receipt.
9. Create the next review task.

Avoid a report that measures only what the agent did. Report what changed for
the client, what evidence supports it, what remains blocked, and what happens
next.

### Pattern-selection prompt

```text
Compare my first cycle with these four patterns:

- lead ownership;
- content and rights;
- support and maintenance;
- onboarding and reporting.

Identify the closest pattern, the source of truth, the minimum capability set,
the approval boundary, and the authoritative readback. Remove any tool or step
that is not required for the first vertical slice. Update 29-FIRST-PLAYBOOK.md
with the clearer design.
```


## 73. Apply Communication Quality to Leads, Content, Support, and Clients

> **Chapter handle:** `BUS-04`.

### Objective

Apply the accepted communication system to one business interaction without
turning a good draft into unauthorized contact. Score response quality and
task outcome separately, then repair the earliest supported failure layer.

### Choose One Interaction

Use one bounded case from these patterns:

| Pattern | Communication decision | Consequential boundary |
| --- | --- | --- |
| Lead response | What the person asked, what is known, and the next useful question | Contact, claims, pricing, scheduling, and CRM writes |
| Content review | Audience, claim support, rights, format, and approval | Publication, attribution, promotion, and brand commitment |
| Support | Issue, impact, evidence, ownership, and next update | Account changes, refunds, liability, access, and promises |
| Onboarding | Scope, prerequisites, roles, decisions, and missing inputs | Contract interpretation, credentials, migration, and delivery dates |
| Client reporting | Period, source-of-truth results, limits, decisions, and actions | Performance claims, commitments, billing, and public disclosure |

Do not combine patterns in the first exercise. One case makes failure and
authority visible.

### Business Conversation Record

Create one `BCR-##` record with:

- workflow, trigger, recipient role, consequence, and accountable owner;
- accepted communication contract and operating-rule versions;
- supplied case facts, owner statements, researched facts, inferences,
  assumptions, recommendations, and unknowns;
- privacy, rights, accessibility, channel, retention, and prohibited-use rules;
- required clarification and exact approval point;
- draft response and source references;
- independent reviewer scores using the accepted response rubric;
- task outcome state and evidence, kept separate from response quality;
- first supported failure layer, repair candidate, and regression case; and
- delivery state: `NOT REQUESTED`, `DRAFT ONLY`, `PENDING EXACT APPROVAL`,
  `AUTHORIZED BY SUPPLIED RECEIPT`, or `BLOCKED`.

An agent may record a supplied approval receipt. It may not manufacture one or
interpret general enthusiasm as approval of exact copy, recipient, channel,
time, or action.

### Score the Draft and the Outcome Separately

Use the `COM-09` rubric for observable response behavior: goal and audience
fit, fact control, context, clarity, tone, emotional calibration, repair,
accessibility, privacy, and safety. Then score the business outcome with its
own evidence: qualified reply, approved publication, resolved case, completed
onboarding input, or accepted report decision.

A high-quality draft can have no task outcome because it was never authorized
for delivery. A reply can arrive after a weak message. Preserve both truths.
Do not train on engagement, opens, or sentiment as if they were complete
quality labels.

### Repair the Earliest Supported Layer

When the case fails, use the accepted order:

1. repair the goal, case facts, or success criteria;
2. repair the communication or operating rule;
3. repair source context or retrieval;
4. repair a tool contract when current state or action is missing;
5. repair workflow ownership, approval, channel, or handoff;
6. repair evaluation anchors or reviewer guidance; and
7. consider a model adaptation only after `COM-10` supports it.

Change one variable in the regression case. A repaired draft remains a draft
until the exact outbound or public action is separately approved.

### Example: Support Update With No Send Authority

Harborlight supplies a fictional delayed-order case. The record contains the
order state, last update time, known carrier status, an unknown delivery date,
and a support owner. The agent drafts a response that states the delay, avoids
inventing a date, offers the approved tracking step, and routes a refund
question to the owner.

Two reviewers score the response. The quality gate passes, but delivery stays
`PENDING EXACT APPROVAL` because the recipient, final copy, and channel require
owner confirmation. This is a complete exercise: it proves the communication
and review method without contacting anyone.

### Agent Checkpoint Prompt

```text
Act as a business-conversation evaluator for one supplied case. Read only the
accepted communication contract, agent operating contract, workflow record,
rubric, and supplied evidence. Do not contact a person or inspect an external
system.

Create one BUSINESS-CONVERSATION-RECORD with case scope, evidence classes,
privacy and rights boundary, clarification, exact approval point, draft,
independent scores, disagreement disposition, task-outcome evidence, first
supported failure layer, one-variable repair test, delivery state, first
blocker, one owner task, and deferred items.

Never invent a recipient, fact, source, result, approval, send receipt, or
customer reaction. A passing draft review does not authorize delivery. Show
the complete record and wait.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/BUSINESS-CONVERSATION-RECORD.md`

### Pass Criteria

- One business interaction, consequence, owner, and authority boundary are
  explicit.
- Evidence classes and decision-changing unknowns remain visible.
- Response quality and task outcome have separate evidence and states.
- Two independent reviews and any material disagreement are preserved.
- The first supported repair changes one variable.
- Delivery state follows an exact supplied authorization record.

### Stop Conditions

Stop for private or unnecessary data, unsupported claims, missing rights or
recipient basis, unowned high-stakes decisions, ambiguous approval, missing
escalation, material reviewer disagreement without disposition, or any request
to send, publish, schedule, update a record, promise, refund, or disclose
without the exact required authority.

### Next Step

Carry the accepted pattern, conversation evidence, and failure-layer result
into the weekly operator review. Reuse the method across other interactions
only after each new workflow defines its own consequence and approval gate.


## 74. Activate the Digital-Product Launch System

> **Chapter handle:** `BUS-05`.

### Objective

Activate the included digital-product launch module only when that is the
approved business workflow. Keep the module complete and selectively loaded;
do not flatten it into the main guide or treat its presence as authority to
publish, price, sell, message, or change a live product.

### Activation Contract

Create one `MOD-##` record:

| Field | Required evidence |
| --- | --- |
| Business outcome | Approved digital-product result and owner |
| Module identity | Included module name, version, and integrity reference |
| Required inputs | Current product, audience, rights, offer, channel, and support facts |
| Permitted workspace | Buyer-owned output directory and source boundary |
| Allowed actions | Read, draft, research, test, or another explicit scope |
| Approval gates | Exact owner decisions for price, copy, files, publication, delivery, and outreach |
| Live-system boundary | Accounts and records the module must not change |
| Completion evidence | Reviewed artifacts and system-of-record receipts where authorized |
| Stop and resume | First blocker, owner task, deferred items, and next safe step |

Module activation is a routing decision. It gives the working agent the
module's instructions and required inputs, not the entire package and not
general permission.

### Selective Loading Sequence

1. Confirm the approved outcome and accountable owner.
2. Verify the packaged module identity and required files against the package
   manifest.
3. Read the module quick start and its own instruction contract.
4. Supply only the accepted artifacts and redacted evidence needed for the
   current phase.
5. Set the output workspace, live-system boundary, and exact approval gates.
6. Run one bounded module phase.
7. Review the produced artifact and update durable status before continuing.

If a required module file is missing, changed, or fails integrity review,
record `MODULE BLOCKED`. Do not download a replacement, reconstruct a hidden
file, or substitute remembered instructions.

### Authority Does Not Travel With the Module

A module can draft launch copy, build a research record, prepare a package,
and define a verification plan when those actions are in scope. Consequential
steps retain their own authority:

- product identity, price, promise, refund terms, and support terms need owner
  approval;
- third-party material needs a recorded rights basis;
- public copy, email, SMS, social posts, and listings need exact final approval;
- live account, checkout, delivery, DNS, analytics, and entitlement changes
  need explicit implementation authority and readback; and
- release completion needs matching files, hashes, manifests, delivery, and
  system-of-record evidence.

An authoring session is not a release session.

### Agent Checkpoint Prompt

```text
Act as a module activation controller. Use the supplied package manifest,
digital-product module quick start, current workspace status, approved outcome,
and authority statement. Do not load unrelated modules.

Return one MODULE-ACTIVATION-RECORD with module identity and integrity,
required inputs, accepted references, working directory, allowed actions,
prohibited live systems, exact approval gates, current phase, output artifact,
completion evidence, first blocker, one owner task, deferred items, and state:
MODULE READY, MODULE BLOCKED, or PHASE COMPLETE.

Do not publish, send, price, purchase, connect, upload, deploy, change a live
record, or claim release completion. Show the activation record and wait.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/MODULE-ACTIVATION-RECORD.md`

### Pass Criteria

- The module, version, integrity reference, outcome, and owner are explicit.
- Only the current module phase and required artifacts are loaded.
- Output and live-system boundaries are separate.
- Every consequential action has an exact approval and evidence gate.
- A blocked module has one truthful owner task and resume point.

### Stop Conditions

Stop for a missing or changed module file, unclear product authority, absent
rights evidence, private data outside the approved boundary, an unspecified
output location, a request to mutate a live commercial system, or any attempt
to call prepared artifacts a released product without system-of-record proof.

### Next Step

Continue one module phase at a time. Return to the main guide with the reviewed
artifact and durable status, not the module's entire working context.


## 75. Run the Weekly Operator Review

> **Chapter handle:** `BUS-06`.

Automation drifts when nobody compares the workflow with reality. Use a weekly
review to keep tools, memory, permissions, and business outcomes aligned.

### Review inputs

- open and recently closed tickets;
- failed, blocked, canceled, and retried runs;
- approval requests;
- external actions and readbacks;
- stale knowledge or credentials;
- service health;
- capacity and cost;
- the business metric for the first playbook;
- operator notes and customer feedback.

### Review sequence

1. Reconcile unresolved external actions.
2. Review failures before successes.
3. Confirm duplicate suppression and task ownership.
4. Check that live tools match documented capabilities.
5. Review credentials by health and scope without exposing values.
6. Identify stale memory and sources.
7. Compare the workflow metric with the previous period.
8. Choose one improvement or one deliberate no-change decision.
9. Update the handover and backlog.

### Weekly scorecard

```text
Week ending:
Primary business cycle:
Runs started:
Verified completions:
Failed:
Blocked:
Ambiguous:
Manual interventions:
Duplicate actions prevented:
Average cycle time:
Business outcome metric:
Tool or provider cost:
Top failure:
One improvement:
Owner decision:
```

### Agent checkpoint prompt

```text
Create my first weekly operator review.

Use tickets, status, evidence receipts, service health, costs, and the business
metric from 29-FIRST-PLAYBOOK.md. Review failures and ambiguous actions first.
Do not treat agent output as proof; identify the authoritative readback for each
consequential result.

Produce:
- a one-page scorecard;
- unresolved reconciliations;
- stale knowledge or capability findings;
- one recommended improvement;
- one item that should remain unchanged;
- the exact next ticket.

Save it as 31-WEEKLY-OPERATOR-REVIEW.md.
```

Done when the review can be completed without reconstructing the week from chat
history.


## 76. Build the 30/60/90-Day Roadmap and Defer Sprawl

> **Chapter handle:** `BUS-07`.

The roadmap deliberately adds one layer of capability at a time. Move faster
only when the exit checks pass.

### Days 1-30: establish the truthful baseline

Week 1:

- interview the owner;
- inventory hardware, services, data, and repeated workflows;
- create the project workspace;
- define the first business cycle;
- record budget, privacy, availability, and support constraints.

Week 2:

- choose the smallest architecture;
- establish private authenticated access;
- identify authoritative state;
- write the backup and restore plan;
- preserve the current working baseline.

Week 3:

- create the agent operating contract;
- add durable status, handover, decisions, and ticket folders;
- ground the agent in a small approved knowledge set;
- run known-answer retrieval tests.

Week 4:

- add one read-only capability;
- build one provider-free or synthetic smoke test;
- create the first skill and play;
- run the weekly review manually.

Day-30 exit checks:

- the agent resumes from files rather than chat memory;
- private access is verified;
- a restore path exists and has at least been rehearsed safely;
- one useful read-only capability works;
- the first business cycle is mapped;
- no purchase is justified only by enthusiasm.

### Days 31-60: close one useful loop

Week 5:

- define the first tool or MCP contract;
- write the capability and endpoint coverage;
- classify read, write, destructive, cost, and open-world behavior.

Week 6:

- deploy an isolated candidate;
- add health, discovery, rejection, and representative read tests;
- preserve the prior runtime.

Week 7:

- add the first approval-gated write only if the workflow requires it;
- add idempotency or duplicate control;
- add authoritative readback and evidence receipts.

Week 8:

- run the first playbook with the owner present;
- review failures and manual work;
- measure the business outcome;
- decide whether the workflow has earned continued use.

Day-60 exit checks:

- the capability contract matches the runtime;
- missing authorization fails closed;
- the first playbook completes with readback;
- an ambiguous action stops for reconciliation;
- the previous accepted path remains recoverable;
- the outcome is more valuable than the operating burden.

### Days 61-90: add durability, not sprawl

Week 9:

- add observability and stale-state behavior;
- create incident dedupe and terminal states;
- practice one recovery card.

Week 10:

- add a specialist only if one service needs separate tools, memory, or tests;
- delegate one bounded work package;
- reconcile the result independently.

Week 11:

- add a second business cycle only if the first is stable;
- reuse an existing skill or play where possible;
- compare marginal value with cost and complexity.

Week 12:

- run a restore or rollback drill;
- complete a full operator review;
- archive obsolete assumptions;
- set the next maturity gate.

Day-90 exit checks:

- incidents, tickets, and tasks preserve truthful state;
- one specialist can fail without erasing the coordinator's state;
- recovery is documented and exercised;
- at least one business cycle has a useful trend;
- permissions remain narrower than capability;
- the next purchase or integration has an evidence-based reason.

### Roadmap prompt

```text
Using every artifact created so far, build my 30/60/90-day roadmap.

Constraints:
- one active implementation ticket at a time;
- one useful vertical slice before platform expansion;
- every phase begins read-only;
- every new write has approval, duplicate control, readback, and recovery;
- preserve the last accepted runtime;
- defer purchases until a measured constraint justifies them.

For each week include: outcome, owner, prerequisite, task, artifact, verification,
rollback, budget, and go/no-go gate. Save as 32-ROADMAP.md and update STATUS.md
with the first ticket only.
```

### Defer sprawl with reopen evidence

Defer a purchase or integration when:

- no named workload requires it;
- utilization has not been measured;
- the current bottleneck is unclear;
- the software baseline is unstable;
- restore and rollback are untested;
- the provider's automation rights are unknown;
- the workflow lacks an owner or source of truth;
- the tool duplicates an existing capability;
- the system cannot verify the tool's result;
- a lower-risk manual step is still faster; or
- maintenance cost exceeds the current business value.

Typical examples:

- a larger GPU before model fit and latency are measured;
- a rack server before noise, power, and space are accepted;
- a cluster before one node is operationally boring;
- a second vector database before retrieval tests show a need;
- a broker before more than one connection requires shared policy;
- a second agent before one specialist has a distinct job;
- a public endpoint before private access is insufficient;
- an automation subscription before a workflow is stable manually.

Create `33-DEFERRED-PURCHASES.md`:

```text
Item:
Problem it would solve:
Current evidence:
Measurement still needed:
Alternative already available:
Purchase trigger:
Budget:
Owner decision:
Review date:
```

This keeps money and attention focused on the constraint that currently
matters.


## 77. Final Capstone: Choose the Next Evidence-Earning Move

> **Chapter handle:** `BUS-08`.

1. Create the project workspace.
2. Run the owner interview.
3. Inventory current hardware, services, data, and workflows.
4. Choose the smallest target architecture.
5. Write the agent operating contract.
6. Select one read-only capability.
7. Map one closed business cycle.
8. Create the first skill, play, and playbook.
9. Build the 30/60/90-day roadmap.
10. Put only the first approved ticket in progress.

If your package version includes the digital-product launch module, use it to
turn owned expertise into a packaged offer after the operating foundation is
clear. It is a separate revenue workflow and does not need to block the
infrastructure build.

### Access-path decision

```text
Compare direct, self-hosted, brokered, and managed paths for my first playbook.

Score each for:
- setup effort;
- monthly cost;
- credential ownership;
- customization;
- maintenance;
- capability coverage;
- approval and audit needs;
- recovery burden;
- support.

Recommend the simplest path that closes my first business cycle. Do not add a
broker or managed platform unless it solves a demonstrated requirement. Save
the decision as 34-OPERATING-PATH.md.
```
