# Part VI - Durable Agents and MCP

## 60. Give the Agent a Durable Workspace

> **Chapter handle:** `AGT-01`.

Conversation history is not a reliable project database. Use one canonical control workspace and keep implementation repositories separate.

```text
AI-GROWTH-WORKSPACE/
├── AGENTS.md
├── STATUS.md
├── DECISIONS.md
├── SYSTEM-MAP.md
├── MEMORY.md
├── HANDOVER.md
├── BUGS.md
├── BACKLOG.md
├── artifacts/
├── evidence/
├── tickets/
│   ├── open/
│   ├── in-progress/
│   ├── completed/
│   ├── failed/
│   ├── blocked/
│   └── skipped/
└── README.md

../example-mcp-source/
├── README.md
├── docs/
├── src/
├── tests/
├── compose.yml
└── .env.example
```

This creates two roots:

- **`AI-GROWTH-WORKSPACE`:** control files, customer-created artifacts, minimized evidence, tickets, and handovers.
- **Source repository:** implementation, product documentation, tests, and deployment templates.

`SYSTEM-MAP.md` connects them. Record each source repository's resolved path, purpose, owner, current stage, and allowed access without storing credentials. This gives agents one authoritative map while keeping source history and control history clean.

### What each file does

- `AGENTS.md`: purpose, sources of truth, scope, checks, and safety rules.
- `STATUS.md`: current stage, evidence, blocker, and one next action.
- `DECISIONS.md`: accepted choices, reasons, and reconsideration triggers.
- `SYSTEM-MAP.md`: authoritative system, repository, owner, and path map.
- `MEMORY.md`: durable decisions, conventions, dependencies, and constraints.
- `HANDOVER.md`: verified change, open work, and restart point.
- `BUGS.md`: confirmed defects, impact, evidence, and disposition.
- `BACKLOG.md`: worthwhile ideas deferred beyond the active stage.
- `artifacts/`: customer worksheets, matrices, plans, and deliverables.
- `evidence/`: minimized, redacted, access-controlled proof with a retention period.
- `tickets/`: work in `open`, `in-progress`, `completed`, `failed`, `blocked`, or `skipped`.

### Memory rules that prevent drift

1. Current files and readback outrank remembered claims.
2. Instructions govern work; memory stores facts; handover stores current state.
3. Secrets never belong in control files.
4. Share only reviewed artifacts and evidence.
5. Specialists read only assignment context and leave a handover when unfinished.

### Exercise: Create the project brain

1. Create the canonical `AI-GROWTH-WORKSPACE` tree above.
2. Write a one-page `AGENTS.md` with purpose, allowed root, prohibited actions, and required checks.
3. Create the source repository outside the control workspace.
4. Record its resolved path and responsibility in `SYSTEM-MAP.md`.
5. Add five durable facts to `MEMORY.md`.
6. Add the current objective and next action to `HANDOVER.md`.
7. Create all ticket states plus `artifacts/` and access-controlled `evidence/`.
8. Add a placeholder-only `.env.example` to source.
9. Ask a fresh session to explain the project from these files and correct any gap.

**Produced artifacts:** `AI-GROWTH-WORKSPACE`, `SYSTEM-MAP.md`, the separate source repository, standing instructions, durable memory, active handover, artifact/evidence directories, six ticket states, and a placeholder-only environment template.

### Agent checkpoint prompt

```text
Inspect this project read-only and design the canonical AI-GROWTH-WORKSPACE.
Keep source repositories separate and reference each resolved path from
SYSTEM-MAP.md. Draft AGENTS.md, SYSTEM-MAP.md, MEMORY.md, HANDOVER.md, BUGS.md,
artifacts/, access-controlled evidence/, all six ticket-state folders, and a
placeholder-only .env.example in the source repository. Explain ownership,
retention, and access for each location. Wait for my approval before moving or
editing files.
```

### Done when

- A fresh agent can state the purpose, current goal, and next action.
- `SYSTEM-MAP.md` resolves the separate source repository and its responsibility.
- No secret value is stored in instructions, memory, tickets, or examples.
- Evidence is minimized, redacted, access-controlled, and retained intentionally.
- The handover reflects current state rather than historical storytelling.
- Reviewed artifacts can be shared without carrying unrelated operating context.


## 61. Define Owner, Coordinator, Specialists, and Control Plane

> **Chapter handle:** `AGT-02`.

Multi-agent systems work when roles reduce ambiguity. More agents do not automatically create more intelligence. Start with the minimum set of roles that makes ownership clear.

### Owner

The owner defines intent, budget, legal and ethical limits, risk, and authorization.

### Coordinator

The coordinator selects the next ticket, checks dependencies, assigns a specialist, and reconciles results without inheriting every tool permission.

### Specialists

A specialist owns one bounded domain and receives only its required context and tools. It reports evidence and blockers without changing the objective.

### Verifier and approved runner

A verifier reviews minimized evidence and prepares, but never executes, publish, send, spend, or delete actions. Under a narrow standing policy, a distinct runner may restart one service, smoke it, and set terminal state.

### Control plane

The control plane holds assignments, ticket and deduplication state, approvals, health, work limits, locks, and evidence pointers.

It may begin as structured files plus a coordinator prompt. Add a database or broker only when concurrency, multiple users, or remote services require one.

### Sample authority matrix

| Action | Owner | Coordinator | Specialist | Verifier/runner |
|---|---:|---:|---:|---:|
| Set business objective | Approve | Propose | Advise | Observe |
| Read project state | Yes | Yes | Scoped | Scoped |
| Create work package | Yes | Yes | Propose | No |
| Edit implementation | Approve policy | No | Scoped | No |
| Change secrets or auth | Approve separately | No | No | No |
| Restart one assigned service | Approve policy | Schedule | No | Scoped runner only |
| Publish, send, spend, or delete | Approve and execute or delegate separately | Prepare only | No | Prepare/verify only |
| Verify health and tests | Review | Reconcile | Run focused checks | Final gate |
| Close ticket | Override | Recommend | Recommend | After evidence |

### Exercise: Design the smallest team

1. Write the owner’s decisions that cannot be delegated.
2. Define one coordinator.
3. Add one specialist for the first vertical slice.
4. List the specialist’s readable and editable paths.
5. List actions reserved for owner approval.
6. Choose who verifies completion.
7. Set a concurrency limit of one until parallel work is proven necessary.

**Produced artifact:** `19-AGENT-AUTHORITY-MATRIX.md`, including roles, readable scope, editable scope, allowed actions, approval-required actions, and forbidden actions.

### Agent checkpoint prompt

```text
Design the smallest role model for my chosen workflow. Define the owner,
coordinator, one bounded specialist, and an optional verifier/runner. Produce
an authority matrix covering reads, edits, credentials, restarts, publishing,
sending, spending, deletion, verification, and ticket closure. Keep the
verifier prepare-only for consequential actions. Capability must not imply
authority. Recommend a file-based control plane unless a current concurrency or
multi-user requirement justifies more.
```

### Done when

- Every action has one accountable role.
- The coordinator can delegate without holding universal credentials.
- The specialist has a bounded root and a forbidden-operation list.
- The completion gate is separate from “the agent says it worked.”
- Increasing the number of agents is a deliberate decision, not a default.


## 62. Use Tickets as Durable Work Packages

> **Chapter handle:** `AGT-03`.

A ticket is more than a reminder. It is the contract that lets a coordinator, specialist, verifier, and future session agree on what is happening.

Use a small lifecycle:

```text
open → in-progress → completed
                   ↘ failed
                   ↘ blocked
                   ↘ skipped
```

`completed` passed acceptance. `failed` ended unsuccessfully. `blocked` needs authority, information, or external change. `skipped` was locked, obsolete, or missing a precondition.

### A useful ticket template

```markdown
# TICKET-0042  -  Add read-only customer summary tool

Status: open
Owner: business-owner
Coordinator: operations-coordinator
Specialist: crm-specialist
Service: crm-mcp
Risk: read-only
Deduplication key: crm-mcp:customer-summary:v1

## Objective
Return a bounded summary for one authorized customer record.

## Scope
- Add one tool and its tests.
- Update tool inventory and usage guidance.

## Out of scope
- Editing the customer record.
- Bulk export.
- Credential or deployment changes.

## Acceptance
- Missing authentication fails before provider access.
- One authorized read returns the documented fields.
- Output excludes secrets and unnecessary personal data.
- Tool count and documentation agree.

## Evidence references
- Redacted test summary and result
- Minimized health/tool discovery readback
- Focused smoke summary
- Access-controlled evidence location and retention date

## Rollback
Restore the prior service image and rerun discovery plus the focused read.
```

### Work-package rules

- Keep one objective and one affected service whenever possible.
- State out-of-scope work and freeze acceptance before implementation.
- Collect only acceptance evidence, redact it before storage, restrict access, and record retention.
- Preparation does not authorize a risky action.
- Keep at most one in-progress ticket per specialist or service until concurrency is designed.

### Deduplication

Retries, restarts, and monitors can create duplicate work. Use a deterministic key based on service, operation, target, and version or time window.

Examples:

```text
crm-mcp:customer-summary:v1
website:weekly-health:2026-W31
content:article:agentic-infrastructure:draft
```

Before creating or claiming a ticket:

1. Search nonterminal tickets for the key.
2. If one exists, link new minimized evidence and skip.
3. Preserve existing approval and terminal outcomes.
4. Lock concurrent claims and record duplicates as `skipped`.

### Handovers

A handover is required when work stops before terminal completion. Include:

- ticket, state, inspected or changed scope;
- completed verification and evidence pointer;
- affected files or services;
- blocker, next step, and recovery status.

The next worker needs an accurate restart point, not a conversation transcript.

### Exercise: Run one ticket manually

1. Create a ticket with a deduplication key and move it to `in-progress`.
2. Perform read-only discovery and correct false assumptions.
3. Complete the smallest approved change.
4. Have the verifier run acceptance.
5. Move the ticket to one terminal directory.
6. Confirm a fresh session understands the outcome from ticket and handover.

**Produced artifacts:** one complete ticket, minimized and redacted evidence with controlled access, a handover if required, and a truthful terminal state.

### Agent checkpoint prompt

```text
Convert this objective into one durable work package. Include owner,
coordinator, specialist, affected service, risk class, deterministic
deduplication key, objective, scope, out-of-scope items, frozen acceptance
criteria, safe evidence requirements, and rollback. Check existing nonterminal
work for duplicates before proposing a new ticket. Minimize, redact,
access-control, and time-bound retained evidence. Do not execute the ticket.
```

### Done when

- A different specialist could execute the ticket without hidden instructions.
- A repeated scheduler run would detect the same work.
- The ticket distinguishes preparation from authorization.
- Terminal state depends on acceptance evidence.
- Evidence contains only what acceptance requires and has an access/retention rule.
- Unfinished work has a precise handover.

### Apply the accepted OS evidence

Use OS-08 and OS-09 for shared-state, fencing, wait-graph, liveness, and fairness controls. A ticket is an operating analogy, not an OS process; this chapter applies the controls to agent work packages.


## 63. Turn the Communication Contract Into Operating Rules

> **Chapter handle:** `AGT-04`.

### Objective

Convert one accepted communication contract into enforceable agent operating
rules with inputs, state, output checks, escalation, and feedback ownership.
Keep response behavior separate from tool authority and implementation state.

### Required Inputs

- accepted `COM-01` communication contract and relevant `COM-02` through
  `COM-10` artifacts;
- `AGT-01` durable workspace and `AGT-02` role and authority map;
- one workflow and consequence from the foundation build brief;
- the current tool and channel boundary; and
- an owner for behavior, safety, accessibility, privacy, and escalation.

Missing communication evidence blocks the affected rule. It does not grant an
agent discretion to infer a person's identity, emotion, preference, consent,
or approval.

### Rule Model

Create versioned `OPR-##` rows:

| Field | Purpose |
| --- | --- |
| Trigger and workflow state | Defines when the rule applies |
| Goal and audience evidence | Binds the response to accepted context |
| Required behavior | Names one observable output behavior |
| Protected facts | Prevents tone or format changes from altering truth |
| Required check | Defines clarification, citation, approval, or review |
| Prohibited behavior | Blocks inference, concealment, false certainty, or action |
| Tool and channel boundary | Separates response drafting from system capability |
| Escalation route | Names the human owner and evidence packet |
| Test cases and rubric | Makes the rule measurable before promotion |
| Feedback and expiry | Defines review, repair, retirement, and stale behavior |

Write rules as observable contracts. "Be empathetic" is not testable. "When a
person explicitly states frustration, acknowledge the stated concern once,
preserve the facts and options, avoid claiming an emotion, and offer the
approved next step" can be scored.

### Precedence and Conflict

Apply rules in this order:

1. safety, law, privacy, rights, and explicit owner authority;
2. current workflow facts and system-of-record evidence;
3. the accepted communication contract;
4. user-stated channel and accessibility preferences;
5. style, tone, and optional personalization.

A lower rule cannot override a higher one. When two applicable rules conflict,
record the exact conflict, preserve both sources, stop the affected output,
and assign the decision to the named owner. Do not silently select the rule
that produces the smoother answer.

### Feedback Loop

Feedback is evidence only when its source and scope are visible. Record:

- exact case and response version;
- person-stated feedback or reviewer score;
- affected `OPR-##` rule;
- observed behavior gap, not a guessed motive;
- immediate repair, if authorized;
- proposed rule change and regression cases;
- owner decision, version, effective date, and rollback; and
- whether earlier outputs need requalification.

One complaint does not prove a general model defect. One high score does not
prove universal quality. Repeated evidence can justify a rule revision or a
new `COM-10` adaptation test, but it does not authorize fine-tuning by default.

### Example: Draft Versus Send

Harborlight's support agent may draft a response from an approved case packet.
`OPR-07` requires a concise issue summary, facts separated from unknowns, one
bounded next step, and an explicit no-send state. The communication contract
sets a direct, calm tone. The authority map says only the support owner can
approve external delivery.

The draft passes its response rubric. That result proves the draft meets the
declared behavior checks. It does not change the tool permission, send the
message, update the case, or prove customer satisfaction. A missing recipient
or approval keeps delivery blocked while the draft evidence remains valid.

### Agent Checkpoint Prompt

```text
Act as an agent operating-rule editor for one approved workflow. Read only the
supplied communication contract, relevant COM artifacts, durable-workspace
rules, authority matrix, and workflow brief.

Produce a versioned AGENT-OPERATING-CONTRACT with OPR rows containing trigger,
state, audience evidence, required behavior, protected facts, required check,
prohibited behavior, tool and channel boundary, escalation owner, test cases,
rubric reference, feedback owner, expiry, and status.

Apply precedence in the stated order. At the first consequential conflict or
unknown, stop the affected output, preserve independent evidence, and assign
one owner task. Do not infer identity or emotion, change permissions, operate a
tool, send, deploy, train, or treat a passing response review as approval.
Show the contract and wait.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/AGENT-OPERATING-CONTRACT.md`

### Pass Criteria

- Every rule is observable, scoped, versioned, and testable.
- Facts, communication behavior, tool authority, and delivery approval remain
  separate.
- Precedence, conflict, escalation, feedback, expiry, and rollback are clear.
- At least one normal, ambiguous, blocked, and escalation case is scored.
- A passing review authorizes no live external action.

### Stop Conditions

Stop for missing owner authority, absent audience or privacy evidence,
conflicting rules, unsupported personal inference, missing safety or escalation
route, an unscored consequential behavior change, or a request to alter tools,
permissions, model behavior, records, or outbound delivery without its own
approved process.

### Next Step

Use the operating contract when designing tool descriptions and MCP workflows.
The contract governs response behavior; the next chapters separately prove
capability, permission, execution, and recovery.


## 64. Understand Hosts, Clients, Servers, and Capability

> **Chapter handle:** `MCP-01`.

MCP standardizes tool discovery and calls:

- **Host:** the application in which the model operates.
- **Client:** the connection inside the host that speaks MCP.
- **Server:** the service that publishes tools, resources, or prompts and performs bounded work.

The client connects directly or through an authorized control plane; the contract stays predictable.

```text
Human intent
    ↓
Agent host
    ↓
MCP client
    ↓
Authentication and policy gate
    ↓
MCP server tool
    ↓
Provider or local system
    ↓
Bounded result and next-action hint
```

Reject invalid access before provider contact and return only next-step data.

### Capability is not authority

Discovery shows capability, not caller authority.

Evaluate authority across four gates:

1. **Identity:** who is calling?
2. **Configuration:** which account, project, or tenant is in scope?
3. **Policy:** is this caller allowed to perform this operation?
4. **Intent:** has the required ticket, confirmation, or approval been supplied?

A server may expose `publish_campaign` while a specialist may call only `prepare_campaign`; make that distinction visible.

### Exercise: Trace one request

1. Draw one tool's host, client, server, provider, and result path.
2. Mark identity, account scope, authorization, and confirmation.
3. Mark sensitive-data locations.
4. Define the smallest useful result.

**Produced artifact:** `21-MCP-REQUEST-FLOW.md`, including trust boundaries and failure points.

### Agent checkpoint prompt

```text
Map my selected workflow as an MCP request path. Identify the host, client,
server, provider or local target, authentication gate, account-scope gate,
policy gate, intent/approval gate, and bounded result. Separate what the server
can do from what this caller may do. Flag any point where the design relies on
capability as if it were authorization.
```

### Done when

- You can explain the request path without saying “the AI just handles it.”
- Identity, scope, policy, and intent are separate gates.
- Provider access cannot occur before required authentication.
- The output supports a specific next step.
- Tool discovery does not grant write authority.


## 65. Design Tool Contracts Humans and Agents Can Read

> **Chapter handle:** `MCP-02`.

An MCP tool explains selection, changes, contacted system, configuration, and result.

Weak description:

```text
Create report.
```

Useful description:

```text
Use this to create a draft weekly pipeline summary for the configured sales
workspace. This reads opportunity and activity data but does not contact leads
or publish the report. Returns the draft text, covered date range, record count,
and any missing-configuration warnings.
```

### Contract worksheet

For every tool, record:

| Field | Question |
|---|---|
| Name | Is the action obvious and unambiguous? |
| Use when | What user intent should select this tool? |
| Do not use when | What common misuse should be prevented? |
| Inputs | Are every parameter, enum, format, and scope described? |
| Prerequisites | What configuration or prior resource is required? |
| Side effect | What external or local state changes? |
| Risk | Is it read-only, write, destructive, paid, or open-world? |
| Idempotence | What happens if the call repeats? |
| Output | What stable identifiers, status, and next-step data are returned? |
| Failure | Can the agent distinguish setup, authorization, provider, and validation errors? |

### Navigation tools

Add a read-only navigation layer:

- `check_configuration`: reports readiness and missing setup without values;
- `list_capabilities`: groups tools by workflow and risk;
- `get_endpoint_coverage`: explains supported provider operations and exclusions;
- `get_tool_usage`: explains one tool’s parameters, side effects, and follow-up actions.

They also provide side-effect-free discovery smokes.

### Behavioral annotations

Declare behavior accurately:

- `readOnlyHint`: the call does not mutate state;
- `destructiveHint`: it can delete, overwrite, revoke, spend, publish, or create similarly consequential impact;
- `openWorldHint`: it interacts with an external system;
- `idempotentHint`: repeating the same call has the same practical effect.

Annotations are hints to the model and host, not substitutes for server-side authorization.

### Endpoint coverage for the first workflow

Account completely for the first workflow's provider area without implying whole-API coverage.

| Provider area | Method/path or operation | Tool | Auth | Risk | Pagination/job notes | Test status | Exclusion reason |
|---|---|---|---|---|---|---|---|
| Accounts | List accounts | `list_accounts` | User token | Read | Cursor | Unit + smoke |  -  |
| Campaigns | Publish campaign |  -  | Elevated | Destructive | Async |  -  | Requires reviewed approval model |

Record current official documentation and retrieval date. Map or exclude every stable in-scope operation; expand only for a later workflow.

### Exercise: Specify four tools before coding

1. Define the four navigation tools.
2. Specify one domain read tool.
3. Complete the contract worksheet.
4. Add behavioral annotations.
5. Define the first-workflow provider-area boundary and complete its coverage matrix.
6. Write one happy-path and one failure-path acceptance example.
7. Ask another agent to select the correct tool from three sample user requests.

**Produced artifacts:** `22-TOOL-CONTRACTS.md`, `docs/22-endpoint-coverage.md`, and tool-selection examples.

### Agent checkpoint prompt

```text
Design the agent-facing contract for this MCP before implementation. Include
four read-only navigation tools, one domain tool, complete parameter
descriptions, prerequisites, side effects, output shape, failure classes, and
read-only/destructive/open-world/idempotent annotations. Define the provider
area required by the first workflow and build its coverage table from current
official documentation. Do not claim whole-provider coverage.
```

### Done when

- A model can choose the correct tool without owner explanation.
- Similar tools explain their differences.
- Every parameter has a documented meaning and scope.
- Output includes stable next-step data instead of a raw provider dump.
- Runtime inventory, defined provider-area matrix, health count, and documentation agree.


## 66. Separate Secrets, Permissions, and Configuration

> **Chapter handle:** `MCP-03`.

Treat service access, provider credentials, account scope, and action approval as separate concerns.

Separate client authentication, provider access, account scope, and risky-action intent.

### Secret-handling rules

- Store values in a secret manager, protected runtime, or ignored local file.
- Keep `.env.example` to names, purpose, and blank placeholders.
- Keep keys out of prompts, source, tickets, screenshots, logs, and output.
- Prefer request-scoped provider credentials for multi-user systems.
- Use least-privilege provider scopes.
- Redact before persistence and return useful setup errors.
- Reject invalid service access before provider forwarding.
- Rotate through an owner-approved procedure.

### Sample permission matrix

| Tool group | Coordinator | Read specialist | Write specialist | Required approval |
|---|---:|---:|---:|---|
| Configuration check | Call | Call | Call | None |
| Account discovery | Call | Call | Call | None |
| Draft preparation | Assign | Call | Call | Standing policy |
| Record update | Assign | No | Call | Approved ticket |
| Publish/send | Prepare only | No | No | Per action |
| Delete/revoke/spend | No | No | No | Owner plus confirmation |

### Exercise: Build the trust worksheet

1. List every credential the workflow appears to need.
2. Remove credentials that are not required for the first vertical slice.
3. Record owner, storage location, scope, lifetime, rotation path, and consuming component.
4. Draw the credential flow without values.
5. Complete the permission matrix for every tool group.
6. Test missing, incorrect, and insufficient authorization.
7. Confirm failures occur before provider calls.

**Produced artifacts:** `23-CREDENTIAL-FLOW.md`, `23-PERMISSIONS.md`, and a placeholder-only environment template.

### Agent checkpoint prompt

```text
Create a no-value credential and permission design for this workflow. Separate
service authentication, provider credentials, account scope, and action
approval. For each credential, document owner, secure storage class, least
privilege scope, lifetime, rotation path, and consuming component. Produce a
tool-group permission matrix and missing/invalid/insufficient-auth tests. Never
ask me to paste a secret into chat.
```

### Done when

- No single credential silently grants every layer of authority.
- Every secret has an owner, scope, storage class, and rotation path.
- Unauthorized requests fail before provider activity.
- Tool output and health responses contain no credential values.
- Publish, spend, delete, and revoke actions have explicit approval rules.


## 67. Deploy One Service With Observable Health

> **Chapter handle:** `MCP-04`.

When a networked MCP uses containers, pin the base image and dependencies, build a non-root candidate, record its verified digest, and run it with least privilege. Containerization improves repeatability, but the digest and recovery evidence establish the exact runtime.

```yaml
services:
  example-mcp:
    image: registry.example/example-mcp@${EXAMPLE_MCP_IMAGE_DIGEST:?set a verified sha256 digest}
    user: "10001:10001"
    init: true
    restart: unless-stopped
    env_file:
      - .env
    read_only: true
    tmpfs:
      - /tmp:size=64m,noexec,nosuid,nodev
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    pids_limit: 256
    mem_limit: 512m
    cpus: "1.0"
    networks:
      - agent-tools

networks:
  agent-tools:
    internal: true
```

Replace the digest with the verified candidate image, not a floating tag. Pin the Dockerfile base image and lock dependencies at build time. Adjust limits after measurement and expose only the network surface the workflow requires.

### Health is a contract

Expose a compact `/health` response such as:

```json
{
  "status": "ok",
  "configuration_ready": true,
  "tool_count": 9,
  "version": "1.2.0"
}
```

Derive `tool_count` from the same live inventory used by tool discovery. Health must not expose credentials, headers, provider payloads, customer data, or verbose exceptions.

Use a smoke matrix:

| Layer | Check |
|---|---|
| Local | Unit and protocol tests |
| Container | Process starts as non-root and health responds |
| Network | Intended route reaches the correct container |
| Authentication | Missing and invalid access fail closed |
| Discovery | Tool list matches documented count |
| Navigation | One read-only navigation tool succeeds |
| Domain | One approved representative call behaves as documented |

Observe status codes, counts, durations, build identities, and fixed reason categories without logging sensitive request bodies.

### Exercise: Create a service readiness card

1. Pin the base image and dependency set.
2. Add `.env.example`; keep `.env` ignored and permission-restricted.
3. Run tests without live provider calls.
4. Build the candidate, scan it, record its digest, and reference that digest from Compose.
5. Check health locally and through its intended route.
6. Verify missing authentication fails.
7. Compare health count with tool discovery.
8. Call one navigation tool.
9. Record the exact version or image identity for rollback.

**Produced artifacts:** container definition, Compose file, health endpoint, smoke matrix, and `24-SERVICE-READINESS.md`.

### Agent checkpoint prompt

```text
Prepare a minimal least-privilege deployment plan for this MCP. Pin the base
image, dependencies, and verified candidate digest. Use a stable service,
non-root UID, read-only filesystem where compatible, bounded temporary storage,
dropped capabilities, bounded resources, minimal network exposure, a
placeholder-only environment template, and compact no-secret health. Define
local, container, network, missing-auth, discovery, navigation, and
representative-call smoke checks. Include the exact prior artifact that would
be restored on failure.
```

### Done when

- The service can be reproduced from pinned inputs and identified by verified digest.
- Health reports readiness and the live tool count without sensitive data.
- Missing authentication fails closed.
- Discovery and documentation agree.
- One failed service can be restored without recreating unrelated services.

### Apply the accepted OS evidence

Use OS-15 and OS-16 for process lifecycle, termination, isolation, and effective limits. This chapter owns MCP-specific discovery, health, tool identity, and vertical-slice readiness.


## 68. Choose Direct, Brokered, Managed, or No Connection

> **Chapter handle:** `MCP-05`.

There is no universal best deployment path.

| Path | Best fit | You operate | Main tradeoff |
|---|---|---|---|
| Direct MCP | One user, few services, simple environment | Each server and client configuration | Lowest complexity, repeated configuration |
| Self-hosted broker | Multiple services, agents, users, or centralized policy | Broker, identity, routing, services, observability | More control, more operational responsibility |
| Managed platform | You want unified setup, catalog, support, and maintenance | Your accounts, policies, and provider access | Less infrastructure work, platform dependency |

Start direct when it meets the requirement. Introduce a broker when you need centralized identity, service selection, user-scoped configuration, audit policy, or many clients. Choose a managed platform when maintaining that control plane is not where you want to spend time.

If the self-hosted broker path wins, compare the direct Hostinger affiliate carts for [KVM 1](https://www.hostinger.com/cart?product=vps%3Avps_kvm_1&period=12&referral_type=cart_link&REFERRALCODE=ZUWMADPANOFE&referral_id=0199a491-d783-7057-85d2-27de6e01e2c5), [KVM 2](https://www.hostinger.com/cart?product=vps%3Avps_kvm_2&period=12&referral_type=cart_link&REFERRALCODE=ZUWMADPANOFE&referral_id=0199a492-26cf-7333-b6d7-692e17bf8ce1), [KVM 4](https://www.hostinger.com/cart?product=vps%3Avps_kvm_4&period=12&referral_type=cart_link&REFERRALCODE=ZUWMADPANOFE&referral_id=0199a492-531e-70d3-83f5-e28eb919466d), and [KVM 8](https://www.hostinger.com/cart?product=vps%3Avps_kvm_8&period=12&referral_type=cart_link&REFERRALCODE=ZUWMADPANOFE&referral_id=0199a492-7ce9-70fb-b96c-2184abc56764) against the capacity, region, backup, network, and recovery requirements in your access-path decision. A VPS is only the runtime; you still own identity, patching, monitoring, and restore.

### Managed Portal and published open-source MCPs

These can be complementary paths when they are included in the current offer:

- A **managed Portal plan** may provide supported-service discovery, centralized configuration, connection diagnostics, versioned skills or playbooks, support workflows, and brokered access. Exact services, storage behavior, support, limits, and features depend on the current plan and documentation.
- An **individually published open-source MCP repository** can be inspected, self-hosted, and modified according to its repository license. Availability, maintenance status, provider terms, and permitted use must be checked per repository; a published server does not mean every managed or internal component is open source.

A purchaser can use a currently supported managed service, deploy a suitably licensed published MCP, or connect a published MCP to another compatible control plane. Verify the current catalog, plan terms, repository visibility, license, and provider requirements before choosing.

### Exercise: Make the path decision

1. Count current users, agents, and services.
2. List identity and audit requirements.
3. Estimate who will patch, monitor, back up, and recover the control plane.
4. Review the managed plan's current terms and each candidate repository's current license.
5. Compare direct, brokered, and managed paths for the next twelve months.
6. Choose today’s simplest fit and record the condition that would trigger migration.

**Produced artifact:** `25-ACCESS-PATH-DECISION.md`, including current choice, alternatives, operating owner, costs, and migration trigger.

### Agent checkpoint prompt

```text
Compare direct MCP access, a self-hosted broker, and a managed platform for my
current users, services, compliance needs, budget, and maintenance capacity.
Use only the current managed-plan documentation and the current repository
visibility and license for open-source claims. Recommend the simplest fit
today. State who operates identity, routing, secrets, updates, observability,
backups, support, and recovery under each option. Include a measurable trigger
for moving to a more complex path.
```

### Done when

- The selected path solves a current requirement.
- Someone is explicitly responsible for maintenance and recovery.
- The choice can evolve without rewriting every tool contract.
- Managed and open-source options are evaluated from current plan, repository, license, and operating facts.
- No broker is added merely because it sounds more agentic.

### Include the no-connection decision

A capable integration may still be the wrong current path. Record NO CONNECTION when ownership, authority, support, recovery, or evidence does not justify a connection, and name the evidence that could reopen it.


## 69. Rehearse, Recover, and Prove One Vertical Slice

> **Chapter handle:** `MCP-06`.

A staged rollout reduces risk by preserving the working path while the candidate is evaluated. It cannot guarantee that provider-side effects are reversible, so every cutover still requires a scoped owner decision.

### Phase 0: Discovery and boundary lock

Inventory source, runtime, routes, data classes, integrations, jobs, repository state, and known irreversible external effects. Lock scope, stop conditions, and acceptance criteria.

### Phase 1: Isolated candidate

Build on separate nonproduction state and configuration with mutating schedulers disabled. Pass tests, scans, container validation, health, auth rejection, discovery, and provider-free smokes without stopping the working system.

### Phase 2: Controlled rehearsal

Prefer synthetic data. If a rehearsal genuinely requires production-derived data, use a separately approved minimization, access, encryption, retention, and deletion plan. Validate configuration, catalog, and restoration behavior without treating rehearsal success as live authorization.

### Phase 3: One integration at a time

Test each provider or client separately and record rollback limits. A passed staging check is necessary but not sufficient; move an integration only through its separately approved change.

### Phase 4: Acceptance and observation

Apply the smallest approved change, obtain human acceptance where automation is insufficient, and observe health, authentication, tool traffic, scheduled work, and support signals through a defined window.

### Phase 5: Cleanup

Retire the prior path only after the owner confirms acceptance and rollback windows close. Remove obsolete components in a separate reviewed change.

### Recovery card

Before deployment, record:

- current service or image identity;
- source/build version;
- tool/catalog count;
- health and authentication results;
- data backup or snapshot identity where relevant;
- provider-side effects that rollback cannot undo and their reconciliation path;
- exact component allowed to change.

On failure:

1. Stop further calls.
2. Do not retry paid, destructive, or outcome-ambiguous work.
3. Restore only the affected component when the recovery procedure has been tested and remains safe.
4. Rerun health, missing-auth rejection, discovery, and the focused regression.
5. Reconcile any external side effect the component rollback cannot undo.
6. Record candidate failure and rollback result truthfully.
7. Keep the ticket blocked if healthy recovery cannot be proven.

### Exercise: Run a no-impact game day

1. Choose an isolated nonproduction service with synthetic data and no real provider write.
2. Record the readiness card.
3. Start a digest-pinned candidate with a harmless visible version change.
4. Intentionally fail one acceptance check.
5. Execute the recovery card.
6. Confirm the prior version, health, authentication rejection, discovery, and focused call.
7. Time the recovery.
8. Update the runbook where a hidden dependency or ambiguous instruction slowed you down.

**Produced artifacts:** `26-ROLLOUT-PLAN.md`, `26-RECOVERY-CARD.md`, acceptance evidence, and a game-day report.

### Agent checkpoint prompt

```text
Create a staged rollout and recovery plan for this service. Use discovery and
boundary lock, isolated candidate, controlled rehearsal, one integration at a
time, human acceptance, observation, and separately reviewed cleanup. Record
the current artifact, build identity, tool count, health, authentication
result, data protection, irreversible provider-side effects, reconciliation,
and the exact component allowed to change. Prefer synthetic rehearsal data,
require separate owner authority for each live cutover, define stop conditions,
and prohibit retries of non-idempotent or outcome-ambiguous work.
```

### Done when

- The candidate can fail without taking the working path with it.
- Every cutover has an exact recovery record with rollback limits.
- Recovery restores only the affected component.
- External effects that cannot be rolled back have a reconciliation path.
- Human acceptance covers behavior automation cannot prove.
- Cleanup occurs after observation, not during the initial change.

### Vertical-slice capstone

Build in this order:

1. Select one repeated, reversible workflow.
2. Create `AI-GROWTH-WORKSPACE` and a separate source repository referenced from `SYSTEM-MAP.md`.
3. Define the owner, coordinator, specialist, verifier, and authority matrix.
4. Run one manual ticket from open to a truthful terminal state.
5. Map the MCP request and trust boundaries.
6. Specify navigation tools and one domain tool before coding.
7. Complete endpoint coverage for the first workflow's provider area.
8. Define credential flow and permission gates.
9. Deploy one container with health and smoke checks.
10. Choose direct, brokered, or managed access.
11. Run an isolated rollout and recovery drill.
12. Automate only the parts that have become boring, stable, and measurable.

The result is a measured business system in which agents understand the work, use well-defined capabilities, operate inside known authority, preserve context, recover from failure, and earn additional autonomy through outcomes.

### Final agent checkpoint prompt

```text
Review my agentic operating system against this chapter. Score durable context,
role clarity, ticket integrity, deduplication, handovers, MCP request boundaries,
capability-versus-authority separation, tool contracts, endpoint coverage,
secret handling, permissions, deployment, health, access path, rollout, and
recovery. Cite evidence for each score. Recommend only the next smallest
improvement, create one proposed work package, and wait for my approval. Treat
AI-GROWTH-WORKSPACE and SYSTEM-MAP.md as the canonical control context.
```

### Final done-when check

- A new agent session can resume without a long verbal briefing.
- One coordinator and one specialist can complete a ticket without scope drift.
- Tool descriptions guide correct selection and disclose side effects.
- Permissions are enforced by the system, not merely requested in a prompt.
- Health, discovery, documentation, and runtime identity agree.
- The working path remains recoverable during change.
- You know exactly what outcomes would justify the next maturity stage.
