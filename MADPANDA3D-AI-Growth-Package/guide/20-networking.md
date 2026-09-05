# Part II - Networking for Private AI Systems

## 10. Start With Network Requirements and Assets

> **Chapter handle:** `NET-01`.

### Objective

Define the requirements, assets, owners, constraints, and unknowns for one
approved AI workflow before drawing a topology or changing a device.

### Required Inputs

- one approved business or operator outcome from `FND-02`;
- the current-state inventory from `FND-01`;
- the owner of the workflow and the person responsible for the network;
- the approved read-only inspection boundary;
- the private evidence location; and
- known production, test, lab, and external-provider boundaries.

Stop with an intake task when the outcome, owner, target environment, or
inspection authority is unclear. Do not turn an unapproved discovery exercise
into a scan.

### Why This Matters

Starting with a device, port, or published service can produce a detailed map
of the wrong system. Record the outcome, users, data, availability,
dependencies, and recovery owner first.

An AI path can include an operator device, entrypoint, name and time services,
orchestrator, model, retrieval, state, tools, monitoring, and providers. Roles
may share hardware. Inventory records responsibility; later chapters prove
reachability, security, capacity, and authority.

### Core Model

Use one outcome and two artifacts:

| Stage | Output |
| --- | --- |
| Approved outcome | The user, trigger, successful result, owner, and proof |
| Requirements and inventory | What the workflow needs, what exists, and what is unknown |
| `NET-02` traffic map | How one approved request actually moves |

Every material field carries one evidence label:

- **OBSERVED** - directly inspected now or confirmed by system-of-record
  readback;
- **OWNER-STATED** - supplied and accepted by the accountable owner;
- **RESEARCHED** - supported by a dated source;
- **ASSUMPTION** - useful for planning but not verified; or
- **UNKNOWN** - required information that has not been established.

`RECOMMENDATION` is a proposal, not evidence. An old diagram or remembered
address remains an assumption until current inspection supports it.

### Ordered Method

**Step 1 - Name one outcome.** Record user, trigger, result, owner, and proof.
If it contains independent jobs, select the first useful one.

**Step 2 - Define the boundary.** Mark production, test, lab,
operator-controlled, vendor-controlled, and out-of-scope areas. Record where
raw evidence may be stored and what must be redacted from shareable artifacts.

**Step 3 - Write requirements before assets.** Record users, usage, data,
delay, outage and recovery needs, remote access, provider limits, budget,
maintenance, and growth triggers. Use ranges or `UNKNOWN`.

**Step 4 - Inventory the relevant path.** Record endpoints, network devices,
links, names, services, external providers, monitoring, and recovery roles.

**Step 5 - Separate role from implementation.** Record `retrieval service` and
its verified product or host separately so the inventory survives a move.

**Step 6 - Attach ownership and evidence.** Every item needs an accountable
owner, current state, evidence label, checked date, and private evidence
reference. Record sensitive values only in the approved private location.

**Step 7 - Mark constraints and unknowns.** Identify single-owner, single-link,
single-device, public-exposure, maintenance, and vendor dependencies. Do not
diagnose or redesign them yet.

**Step 8 - Gate the handoff.** Proceed to `NET-02` only when the team can
select one path and distinguish verified facts from unknowns. Otherwise open
the smallest read-only evidence task.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
| --- | --- | --- |
| Quick | You need to decide whether networking is material to the outcome. | Name the user, start point, destination role, external dependency, and largest unknown. |
| Operator | You run an existing workflow. | Complete both artifacts for the current path and assign every unknown an owner. |
| Builder | You are preparing a small implementation. | Add verified service roles, environment boundaries, evidence locations, and measurable availability/performance needs. |
| Architect | You are comparing placements or failure domains. | Add dependency criticality, growth triggers, recovery owners, and constraints without choosing a topology yet. |
| Lab | You need a safe discovery rehearsal. | Inventory a fictional or isolated path, record evidence labels, and explain which production facts remain unavailable. |

### Fictional Example

> **Fictional scenario.** Harborlight Workshop wants an internal assistant to
> answer staff questions from approved operating documents. Staff use managed
> laptops. The orchestrator and retrieval service are intended to remain on a
> private service network; a hosted model may be used for nonrestricted
> prompts. No production network values are shown.

The brief records five users, approved document scope, private model and
retrieval roles, and a two-hour recovery target. Hosted-model retention and the
recovery owner are `UNKNOWN`, so two evidence tasks - not a firewall change -
come next.

### Exercise or Test

Create `NETWORK-REQUIREMENTS-BRIEF.md` and `NETWORK-INVENTORY.csv` from the
provided schemas.

- Select one outcome from the needs brief.
- Complete every required field or mark it `UNKNOWN`.
- Remove secrets, addresses, tokens, customer records, and raw configuration
  from the shareable versions.
- Review the brief with the workflow owner and the inventory with the network
  owner.
- Open one bounded evidence task for each unknown that blocks `NET-02`.

The test passes when a reviewer can name the first request path, its owners,
its required environments, its material constraints, and its unresolved facts
without guessing.

### Exact Agent Checkpoint Prompt

**Test state:** `PASS - CLEAN SESSION, 2026-08-19`

```text
Act as my read-only network requirements and asset interviewer.

Use the approved outcome and proof, user and trigger, FND-01 inventory, target
environment, workflow and network owners, inspection boundary and approving
authority, opaque private evidence reference, and known requirements I provide.
Treat omitted requirements as UNKNOWN. Ask one question at a time only when
the answer changes scope, authority, data handling, availability, cost,
readiness for NET-02, or the next chapter.

Create:
1. AI-GROWTH-WORKSPACE/artifacts/NETWORK-REQUIREMENTS-BRIEF.md
2. AI-GROWTH-WORKSPACE/artifacts/NETWORK-INVENTORY.csv

Use the supplied schemas. If filesystem writing is unavailable or not
authorized, do not claim the files were created. Render both complete artifacts
inline under their exact filenames.

Label every material field OBSERVED, OWNER-STATED, RESEARCHED, ASSUMPTION, or
UNKNOWN. Keep RECOMMENDATION separate. Record roles separately from products
or hosts. Do not scan, connect to, configure, expose, purchase, deploy, or
change anything. Do not request or include credentials, tokens, private
addresses, raw configuration, customer payloads, or secret evidence.
Private evidence references must be opaque IDs, never paths, URLs, addresses,
or secrets.

When a read-only check is needed, state the exact target, owner, reason,
authority required, sensitive-output risk, and expected evidence. Stop if the
outcome, environment, owner, or inspection authority is unclear. If stopped,
render both artifacts as DRAFT with UNKNOWN fields, list each blocker and
owner, ask only the next decision-relevant question, and wait. Otherwise,
present both artifacts and the blocking-unknown register in this interaction
for review, followed by `READY FOR NET-02: YES/NO`, completion evidence,
blockers, and next action. Do not contact, send to, or share with anyone.
```

### Produced Artifact

- `AI-GROWTH-WORKSPACE/artifacts/NETWORK-REQUIREMENTS-BRIEF.md`
- `AI-GROWTH-WORKSPACE/artifacts/NETWORK-INVENTORY.csv`

The buyer owns both files. The brief contains the approved outcome and network
constraints. The inventory contains only the roles and assets relevant to that
outcome. Raw evidence remains private. `NET-02` consumes both files.

### Pass Criteria

- One outcome, workflow owner, network owner, and target environment are named.
- Users, data, access, availability, recovery, maintenance, and external
  dependencies are complete or explicitly `UNKNOWN`.
- Relevant asset roles have state, owner, evidence label, checked date, and
  private evidence reference.
- Shareable files contain no secret or environment-specific sensitive value.
- Every blocking unknown has a register ID, owner, approved read-only evidence
  task, expected evidence, and state; inventory rows reference that ID.
- The selected path is narrow enough to map in `NET-02`.

### Stop Conditions

- The request expands into an unapproved network-wide scan.
- Production, test, lab, and external-provider targets cannot be separated.
- A credential, private payload, or sensitive configuration would be exposed.
- A material owner or authority boundary is missing.
- An unknown changes data handling, public exposure, cost, or recovery design.
- The next step would modify rather than observe the environment.

### Sources and Limits

- Michael G. Solomon and David Kim, Fundamentals of Communications and
  Networking, 3rd ed., Jones & Bartlett Learning, 2022. Used for the broad
  relationship among organizational needs, communications, processes, and IT
  choices. It does not prescribe this artifact, an AI architecture, or a
  current production configuration.
- MADPANDA3D AI Growth Package V2.0.0, Chapters 2, 3, and 8. Reused for the
  evidence vocabulary, inventory-first operating method, and asset-role
  boundary. The next-edition artifact and handoff are original expansions.

### Next Step

Continue to **NET-02 - Map the Agent Traffic Path** using the approved brief
and inventory. Do not proceed while the target environment or inspection
authority remains unclear.


## 11. Map the Agent Traffic Path

> **Chapter handle:** `NET-02`.

### Objective

Map one useful agent request end to end. For each directed connection, record
the services, port, protocol, dependency, data, trust boundary, and read-only
proof.

The result is a working connection map that answers:

- Who initiates and receives each connection?
- How does the caller find the receiver, and which port and protocol carry it?
- What data, dependency, and trust boundary does it cross?
- What small check proves it works, and where should diagnosis begin if it does not?

### Required Inputs

- one approved operator outcome and its current owner;
- the current architecture or service inventory, even if incomplete;
- the authoritative location for service names, listeners, and health checks;
- the permitted read-only inspection boundary;
- current data classifications and trust zones when known; and
- an evidence directory that does not expose secrets or production payloads.

Stop with an intake task when production, test, and lab targets cannot be
distinguished or when the inspection boundary is unclear.

### Why This Matters

An agent system can look like one application while depending on separate
connections among an entrypoint, orchestrator, model, retrieval service, state
database, tool broker, and external providers. One answer may cross local,
private, container, overlay, and public networks before it returns.

When that path is undocumented, every failure becomes vague. “The AI is down”
could mean the operator cannot reach the gateway, the gateway cannot resolve the
orchestrator, the orchestrator cannot reach retrieval, the model is listening
on a different port, or an external HTTPS dependency is unavailable. Guessing
encourages broad changes. A connection map turns the same failure into a finite
sequence of edges that can be checked in order.

This chapter explains connectivity, not agent authority. The operating contract
still decides who may request an action, what requires approval, and which tools
are allowed. A reachable port is a path, not permission.

[RFC 1918](https://www.rfc-editor.org/rfc/rfc1918) defines IPv4 address space
reserved for private internets; a private address does not prove caller
identity. NIST’s [Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
similarly rejects implicit trust based only on network location. Record the
path and identity check at each important boundary.

This chapter uses four common abbreviations:

- **DNS**  -  Domain Name System, used to resolve a service name;
- **TCP**  -  Transmission Control Protocol, a transport used by the examples;
- **HTTPS**  -  Hypertext Transfer Protocol Secure, HTTP protected with TLS; and
- **TLS**  -  Transport Layer Security, which protects a connection in transit.

### The Connection-Mapping Method

Start with one outcome, not the whole lab:

> From my approved operator interface, ask a question about an approved
> document, retrieve supporting context, generate an answer, and return it to
> the same interface.

Write the flow as a simple sentence first:

```text
operator → access edge → orchestrator → retrieval → orchestrator
         → model → orchestrator → access edge → operator
```

Convert every arrow into one connection record. Components are nouns;
connections are directed actions. One orchestrator therefore creates separate
records for its retrieval, model, state, and tool calls.

### 1. Name the service by role

Record the role before the product: operator interface, gateway, orchestrator,
model, retrieval, state, tool broker, or monitoring. Keep the verified product
or host in a separate field so the map survives implementation changes.

### 2. Record the initiator and receiver

Connections are directional. Replace “gateway and orchestrator communicate”
with “gateway initiates HTTPS request to orchestrator.” Return traffic belongs
to that connection unless the receiver opens another one. This matters because
a receiver does not automatically need permission to initiate toward its caller.

### 3. Record name, address scope, port, and protocol

Record how the caller finds the receiver: service name, loopback, private
subnet, overlay, or public hostname. Do not publish internal values. Record the
receiving port, transport and application protocols, and TLS termination.
`443 / TCP / HTTPS` is more useful than “web connection.” Write `UNKNOWN`
instead of relying on a remembered default.

### 4. Classify the dependency

Mark the receiver as:

- **Hard dependency**  -  this outcome cannot finish without it.
- **Soft dependency**  -  the outcome can continue in a reduced mode.
- **Optional dependency**  -  the connection serves an enhancement outside the
  minimum path.

Record visible failure behavior. A hard model failure stops the answer; a soft
monitoring failure should report stale telemetry without blocking it. This
prevents optional features from becoming hidden single points of failure.

### 5. Classify the data

Name the data category, direction, and minimum content: request, retrieved
passage, document ID, model prompt, answer, tool arguments, health result, or
audit event. Describe categories without pasting payloads, secrets, customer
records, internal addresses, or tokens.

### 6. Mark the trust crossing

Use a small set of zones that match the current system:

- operator device;
- controlled access edge;
- private service network;
- restricted data network;
- approved external provider.

Record where identity is checked and encryption begins and ends. The permission
matrix remains the source of truth for authorization.

### 7. Attach one proof to every edge

Attach one non-mutating proof: name resolution, a documented health endpoint,
the expected listener, or a successful request trace. Keep raw output private;
the shareable map records only the result and evidence location.

### Fictional Agent Topology

The ports and names below are fictional examples, not product defaults or a
deployment prescription.

```text
OPERATOR ZONE       CONTROLLED EDGE          PRIVATE SERVICE ZONE
[Operator] ─ C-01 → [Access gateway] ─ C-02 → [Orchestrator]

RESTRICTED DATA ZONE
[Orchestrator] ─ C-03 → [Retrieval / index]
[Orchestrator] ─ C-04 → [Model]
[Orchestrator] ─ C-05 → [Durable state]

PRIVATE INTEGRATION ZONE                 APPROVED EXTERNAL PROVIDER
[Orchestrator] ─ C-06 → [Tool broker] ─ C-07 HTTPS / 443 → [Provider API]

RESTRICTED DATA ZONE: retrieval/index, model when local, and durable state.
Each C-03 through C-05 connection has its own name, listener, identity check,
data class, and proof even when the services share one host.
```

The boxes are responsibilities, not required machines. Co-located services
still need separate connection records, listeners, and evidence.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
|---|---|---|
| **Quick** | You need orientation before making a design decision. | Read the written C-01 through C-07 sequence, restate the path in text, and name the first hard dependency. |
| **Operator** | You run an existing system and need an honest map. | Fill every worksheet row for one current outcome and mark each unknown. |
| **Builder** | You are assembling the first working slice. | Verify names, listeners, health checks, and one full request without changing network policy. |
| **Architect** | You are deciding where to split roles or failure domains. | Add trust zones, hard/soft dependencies, failure behavior, capacity assumptions, and promotion triggers. |
| **Lab** | You learn by observing a controlled failure. | Run the troubleshooting exercise in a disposable or explicitly approved environment and preserve the evidence. |

Routes are cumulative. Architect does not skip Operator evidence, and Builder
does not replace unknowns with preferred design values.

### Connection Worksheet

Use one connection ID across the two tables. The split keeps the printed and
screen-reading order usable.

### Endpoint and dependency table

| ID | Initiator -> receiver | Role | Name scope | Port / transport / application | Dependency |
| --- | --- | --- | --- | --- | --- |
| C-01 | Operator -> gateway | Controlled entrypoint | Private overlay name | 443 / TCP / HTTPS | Hard |
| C-02 | Gateway -> orchestrator | Request coordination | Private service name | 8443 / TCP / HTTPS, fictional | Hard |
| C-03 | Orchestrator -> retrieval | Approved-context lookup | Internal service name | Record verified value | Hard for grounded answer |
| C-04 | Orchestrator -> model | Generation | Internal or approved external name | Record verified value | Hard |
| C-05 | Orchestrator -> state | Durable task/session state | Restricted internal name | Record verified value | Hard |
| C-06 | Orchestrator -> broker | Tool connection | Internal service name | Record verified value | Optional here |
| C-07 | Broker -> provider | Approved external API | Public provider hostname | 443 / TCP / HTTPS | Optional here |

### Data, trust, and evidence table

| ID | Minimum data crossing | Trust crossing and identity check | Read-only proof and evidence state |
| --- | --- | --- | --- |
| C-01 | Request and returned answer | Operator to access edge; user and device identity checked | Approved route returns expected health; label the readback `OBSERVED` |
| C-02 | Request, session ID, response | Edge to service zone; gateway identity checked | Health plus one correlated request ID; `OBSERVED` or `UNKNOWN` |
| C-03 | Query, document IDs, bounded passages | Service to restricted data zone; workload identity checked | Known query returns expected source IDs; `OBSERVED` or `UNKNOWN` |
| C-04 | Bounded prompt and generated response | Private-to-model boundary; service identity checked | Non-sensitive test returns within target time; `OBSERVED` or `UNKNOWN` |
| C-05 | Task state and evidence references | Service to restricted data zone; workload identity checked | Read-only state check shows current schema/version; `OBSERVED` or `UNKNOWN` |
| C-06 | Tool name and bounded arguments | Service to integration zone; workload identity checked | Discovery works without provider action; `OBSERVED` or `UNKNOWN` |
| C-07 | Minimum provider request and response | Integration zone to provider; both identities checked | Approved read endpoint succeeds; `OBSERVED` or `UNKNOWN` |

Add these fields when relevant:

- implementation and source of truth;
- latency or timeout expectation;
- receiver owner and fallback;
- evidence location and verification date;
- implementation state: `WORKING`, `DEGRADED`, `BLOCKED`, `NOT YET BUILT`, or
  `UNKNOWN`.

Implementation state is not an evidence label. Support it with the canonical
`OBSERVED`, `OWNER-STATED`, `RESEARCHED`, `INFERENCE`, `ASSUMPTION`, or
`UNKNOWN` label. `RECOMMENDATION` remains separate from evidence. Only current
`OBSERVED` readback can establish `WORKING` for acceptance.

### Troubleshooting Exercise: The Interface Loads but Answers Fail

Use a disposable or explicitly approved environment. Do not scan public
addresses, alter production routing, or paste credentials into commands.

**Symptom:** The operator interface loads normally. Submitting a grounded
question waits for 20 seconds and then returns an error.

**Known evidence:**

- C-01 succeeds: the operator reaches the gateway.
- C-02 succeeds: the gateway health check reaches the orchestrator.
- The orchestrator records a timeout while starting C-03.
- The retrieval service is expected to be a hard dependency for this outcome.

Work from the last proven edge toward the first failing edge:

1. Mark C-01 and C-02 `WORKING` with `OBSERVED` evidence for this incident; do not retest healthy edges repeatedly unless evidence changes.
2. Resolve the approved C-03 service name from the orchestrator’s network context; record whether resolution succeeds and whether the address scope is expected.
3. Check the route to the resolved private address.
4. Use a documented health endpoint; do not improvise a privileged API call.
5. Confirm that the receiver listens on the expected port and interface.
6. Compare the observed name, address, port, and protocol with the C-03 row.
7. Record the first mismatch. Stop before changing DNS, firewall, container,
   proxy, or service configuration.

Representative read-only commands may include the following. Replace every
`REPLACE_...` value inside the quotes before running anything. Run name,
route, and HTTP checks from the orchestrator's actual network context. Run
`ss` only on the receiver host or network namespace that you are authorized to
inspect.

```bash
approved_service_name='REPLACE_WITH_APPROVED_SERVICE_NAME'
approved_private_address='REPLACE_WITH_APPROVED_PRIVATE_ADDRESS'
documented_health_url='REPLACE_WITH_DOCUMENTED_HEALTH_URL'

getent ahosts "$approved_service_name"
ip route get "$approved_private_address"
curl --fail --show-error --connect-timeout 3 "$documented_health_url"
ss -lnt
```

The exercise passes when evidence identifies the first failing connection or
one precise owner-held unknown; repair is not required. If the name resolves to
an old address while the receiver listens on the documented new address, record
a C-03 naming-path mismatch. The next action is a reviewed discovery correction,
not a model reinstall or broad firewall rewrite.

### Agent Checkpoint Prompt

**Test state:** `PASS  -  CLEAN SESSION, 2026-08-03`

```text
Act as my read-only network path mapper. Use my approved architecture, current
service documentation, and read-only system evidence to create
AI-GROWTH-WORKSPACE/artifacts/NET-02-NETWORK-CONNECTION-MAP.md for one outcome.

Before mapping, confirm the single outcome, owner, exact production/test/lab
target, authoritative service documentation, permitted read-only inspection
boundary, private evidence directory, data classifications, trust zones, and
known service owners. Mark missing inputs UNKNOWN. If the target or authority
cannot be distinguished, stop before proposing a check.

Use only evidence I already provide. Do not run a command. Write the flow as
trigger → entrypoint → coordinator → dependencies → return path. Convert every
arrow into a stable connection ID. Present two linked tables: endpoint and
dependency first, then data, trust, evidence, and state. Record:
- connection ID;
- initiating service and receiving service;
- service role and current implementation, if verified;
- approved name or address scope without exposing private values in the
  shareable summary;
- receiving port, transport protocol, application protocol, and TLS
  termination;
- hard, soft, or optional dependency classification;
- minimum data category and direction;
- trust-zone crossing and identity-check location;
- expected success behavior;
- one read-only proof, evidence location, and verification date;
- implementation state: WORKING, DEGRADED, BLOCKED, NOT YET BUILT, or UNKNOWN;
- evidence basis: OBSERVED current readback, attributed OWNER-STATED input,
  dated RESEARCHED source, reasoned INFERENCE, unverified ASSUMPTION, or
  UNKNOWN. Keep RECOMMENDATION separate. Only current OBSERVED evidence can
  establish WORKING.

Do not infer ports from product defaults. Do not print or request secrets. Keep
raw addresses, hostnames, process details, and command output in the private
workspace and summarize only what the design needs. Explain connections but do
not rewrite my agent authorization policy. Use only systems I own or am
explicitly authorized to inspect. Do not scan, deploy, restart, or change DNS,
firewall, proxy, routing, containers, services, credentials, or provider state.
Stop if documentation conflicts with current evidence, a service is
unexpectedly public, a trust crossing lacks an owner or data class, or a check
would leave the approved target.

Finish with the first unproven edge, the smallest safe verification step, and
the exact condition that requires me or another service owner to take over.
Show me the completed map and wait for my review. Do not run a new command or
continue into NET-03 unless I approve the exact next read-only verification
step.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/NET-02-NETWORK-CONNECTION-MAP.md`

It contains one outcome flow, one row per connection, dependency, data and
trust crossings, evidence references, and unknowns. Raw evidence stays private.

### Pass Criteria

- One useful outcome is mapped end to end and back to the operator.
- Every arrow has a connection row with a clear initiator and receiver.
- Names, ports, protocols, and TLS termination are verified or honestly marked.
- Every receiver is classified as hard, soft, or optional for this outcome.
- Data categories and trust-zone crossings are visible without exposing values.
- Each important edge has one safe success proof and an evidence location.
- The first failure can be narrowed to a connection rather than a vague
  component complaint.
- The map does not treat private addressing or reachability as authorization.

### Stop Conditions

Stop and record the boundary when:

- the production, test, and lab targets cannot be distinguished;
- the check would touch a network, provider, or device you do not own or have
  explicit authority to inspect;
- completing the map requires printing a credential or sensitive payload;
- current documentation and runtime evidence disagree about the receiver;
- the only proposed next step is a firewall, DNS, proxy, routing, restart, or
  deployment change that has not been separately reviewed;
- a service is unexpectedly public or its exposure cannot be explained; or
- the data classification or service owner is unknown at a trust crossing.

An honest `UNKNOWN` is a valid result. It becomes a bounded verification task,
not permission to widen the investigation.

### Next Step

Continue to **NET-03: Draw Physical, Logical, and Data-Flow Topologies**. Use
the verified connection IDs to draw three separate views without changing the
network. Zone and exposure decisions come later in `NET-09`, after the current
path and topology are understood.

### Sources Note

This chapter uses original diagrams, examples, worksheet fields, and exercises.
It does not reproduce textbook figures, assessments, or policy templates.

- Solomon, Michael G., and David Kim. *Fundamentals of Communications and Networking*. 3rd ed., Jones & Bartlett Learning, 2022. Relevant foundations: Chapters 3-6 and 15. The source supports durable networking concepts, not the fictional topology, worksheet, commands, or current product defaults.
- National Institute of Standards and Technology. [*Zero Trust Architecture*, NIST SP 800-207](https://doi.org/10.6028/NIST.SP.800-207), 2020. Accessed August 3, 2026.
- Rekhter, Y., et al. [*Address Allocation for Private Internets*, RFC 1918](https://www.rfc-editor.org/rfc/rfc1918), Internet Engineering Task Force, 1996. Accessed August 3, 2026.


## 12. Draw Physical, Logical, and Data-Flow Topologies

> **Chapter handle:** `NET-03`.

### Objective

Draw three linked views of one approved AI workflow so a reviewer can see where
assets exist, how services connect, and what data moves without mistaking a
diagram for proof of reachability, security, or authority.

### Required Inputs

- the accepted `NET-01` requirements brief and network inventory;
- the accepted `NET-02` connection map for one outcome;
- stable asset, service, zone, and connection IDs;
- the owner of the workflow and the owner of the current network record;
- the approved read-only evidence boundary and opaque private evidence-reference
  convention; and
- the authoritative sources for physical placement, service configuration, and
  data handling.

Stop with a blocking-unknown record when the target environment, diagram owner,
or evidence authority is unclear. Do not discover missing topology through a
scan, a configuration change, or contact with an external party.

### Why This Matters

One diagram cannot answer every network question cleanly. A rack drawing can
show that two services share a host but hide which segments they use. A service
map can show a gateway calling an orchestrator but hide the switch, wireless
link, and physical failure domain beneath that call. A data-flow view can show
that a document passage reaches a model while hiding where either service runs.

Combining all three produces a crowded picture that encourages false
conclusions. Separating them makes disagreement useful. If the physical view
places a host in one site while its inventory record names another, that is a
bounded evidence task. It is not permission to choose whichever drawing looks
newest.

### Core Model

The three views share IDs but answer different questions:

| View | It shows | It deliberately leaves to another view |
| --- | --- | --- |
| **Physical** | Sites, rooms, operator endpoints, hosts, network devices, physical or wireless media, and owner-controlled boundaries | Service call order, application data, and authorization policy |
| **Logical** | Service roles, network or trust zones, declared segments, logical adjacencies, and connection IDs | Exact device placement, cabling, and payload sequence |
| **Data flow** | One outcome's trigger, directed data categories, transformations, storage points, external crossings, approval, readback, and record | General network layout and unrelated services |

Use one stable vocabulary across all three:

- asset IDs copied unchanged from the accepted `NET-01` inventory;
- `S-##` for logical services when the accepted inputs do not already assign a
  stable service ID;
- `Z-##` for declared network or trust zones;
- `C-##` for connections inherited from `NET-02`; and
- `D-##` for data categories defined in this artifact.

An ID is a join key, not proof. Every consequential element keeps an evidence
label, source, checked date, and owner. Use `OBSERVED`, `OWNER-STATED`,
`RESEARCHED`, `INFERENCE`, `ASSUMPTION`, or `UNKNOWN`. Keep
`RECOMMENDATION` separate.

Physical placement and logical role are not one-to-one. One host may run an
entrypoint, orchestrator, and retrieval service. One service may run on several
hosts. Draw what is supported now, then record proposed placement in a separate
recommendation section.

### Ordered Method

**Step 1 - Freeze one outcome and one environment.** Name the outcome, owner,
and exact production, test, or lab target. Copy the accepted asset and
connection IDs. Do not widen the map to every system.

**Step 2 - Draw the physical view.** Group owned assets by site or controlled
location. Show operator endpoints, access points, switches, routers, firewalls,
hosts, and the medium between them when known. Mark virtual, hosted, or
provider-controlled components as declared boundaries rather than inventing
their physical layout.

**Step 3 - Draw the logical view.** Place service roles and current
implementations inside their declared zones or segments. Add only the `C-##`
adjacencies required by the selected outcome. A line means a declared or
observed connection record exists; it does not mean the connection is allowed,
healthy, encrypted, or authenticated unless the linked record proves that.

**Step 4 - Draw the data-flow view.** Start at the approved trigger and end at
readback and record. Label each arrow with its `C-##` connection and minimum
`D-##` data category. Show where data is transformed, retained, approved,
redacted, or sent to an external provider. Do not paste payloads, credentials,
customer records, internal addresses, or raw configuration.

**Step 5 - Add text equivalents.** After each diagram, write the same nodes and
edges in reading order. The text must carry every decision encoded by position,
color, line style, or arrow direction.

**Step 6 - Reconcile the views.** Check that every diagram ID resolves to the
inventory or connection map, every connection has the same initiator and
receiver, each logical service resolves to a known placement or `UNKNOWN`, and
every data crossing has an owner and classification. Record conflicts in the
reconciliation register.

**Step 7 - Finish truthfully.** Mark the artifact `READY FOR NET-04: YES` only
when the three views agree on the selected path and all blocking conflicts are
resolved. Otherwise say `NO`, name the blocker, and assign the smallest
approved read-only evidence task.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
| --- | --- | --- |
| Quick | You need orientation. | Read the three text equivalents and name one fact visible only in each view. |
| Operator | You maintain the current workflow. | Draw all three views for one outcome, date the evidence, and reconcile every ID. |
| Builder | You are preparing a small implementation. | Add current and proposed views separately, with promotion triggers and no silent design assumptions. |
| Architect | You are evaluating placement or failure domains. | Record co-location, replicated roles, external ownership, single points, and trade-offs without changing the current map. |
| Lab | You need to practice the distinction. | Build the artifact from the fictional records, inject one mismatch, and produce the correct blocking-unknown task. |

### Fictional Example

> **Fictional scenario.** Harborlight Workshop maps only the internal document
> assistant from NET-01 and NET-02. The names and IDs below are invented. No
> address, port, provider, or product default is implied.

### Physical view

```text
STAFF AREA                         CONTROLLED EQUIPMENT AREA
[NET-A001 managed laptop]
          | wireless medium
        [NET-A002 access point] -- wired medium -- [NET-A003 edge device]
                                                   |
                                              wired medium
                                                   |
                                              [NET-A004 service host]

OUTSIDE OWNER-CONTROLLED PHYSICAL VIEW
[Approved hosted-model dependency - physical placement UNKNOWN and not drawn]
```

Text equivalent: NET-A001 uses a wireless link to NET-A002. NET-A002 uses a
wired link to NET-A003. NET-A003 uses a wired link to NET-A004 in the
controlled equipment area. The approved hosted-model dependency is named only
as an external ownership boundary; its physical placement is `UNKNOWN` and is
not drawn.

### Logical view

```text
Z-01 OPERATOR       Z-02 PRIVATE SERVICES          Z-03 RESTRICTED DATA
[NET-A001] -- C-01 → [S-01 gateway] -- C-02 → [S-02 orchestrator]
                                                  |-- C-03 → [S-03 retrieval]
                                                  `-- C-05 → [S-05 state]

Z-04 APPROVED EXTERNAL
[S-02 orchestrator] -- C-04 → [S-04 hosted model]
```

Text equivalent: NET-A001 initiates C-01 to S-01 in Z-02. S-01 initiates C-02 to
S-02. S-02 initiates C-03 to S-03 and C-05 to S-05 in Z-03. S-02 initiates
C-04 across the external boundary to S-04 in Z-04. The physical host for S-01,
S-02, S-03, and S-05 is currently NET-A004; their service roles remain
separate.

### Data-flow view

```text
D-01 approved question
NET-A001 -- C-01 / D-01 → S-01 -- C-02 / D-01 → S-02
S-02 -- C-03 / D-02 bounded query → S-03
S-03 -- C-03 / D-03 passage IDs + excerpts → S-02
S-02 -- C-04 / D-04 bounded prompt → S-04
S-04 -- C-04 / D-05 draft answer → S-02
S-02 -- C-05 / D-06 task record → S-05
S-02 -- C-02 / D-05 → S-01 -- C-01 / D-05 → NET-A001
```

Text equivalent: NET-A001 submits D-01 through C-01 and C-02. S-02 creates D-02
and sends it through C-03. S-03 returns D-03 on C-03. S-02 creates D-04 from
D-01 and approved D-03 content, then sends it through C-04. S-04 returns D-05
on C-04. S-02 writes the D-06 task record through C-05, returns D-05 through
C-02 to S-01, and returns D-05 through C-01 to NET-A001. The diagram does not
claim that raw source documents, credentials, or unrestricted history cross
C-04.

The reconciliation check finds one blocker: C-04 is owner-stated, but no
current evidence source confirms the external boundary or permitted D-04
content. The artifact ends `READY FOR NET-04: NO` and assigns the workflow
owner a review of the approved provider and data-handling record. It does not
test the provider or change egress.

### Exercise or Test

Create `NETWORK-TOPOLOGY-AND-FLOW.md` from the provided schema.

1. Select one accepted `NET-02` outcome and environment.
2. Draw the physical view using inventory IDs and current placement evidence.
3. Draw the logical view using service, zone, and connection IDs.
4. Draw the data-flow view using the same connection IDs and new data IDs.
5. Write a complete text equivalent beneath every diagram.
6. Reconcile every node and edge, then record each mismatch as a blocking or
   nonblocking issue with owner, evidence task, and expected proof.
7. Ask the workflow owner and network-record owner to review the shareable
   artifact without contacting any external party.

The exercise passes when another reviewer can trace one data category from
trigger to readback, locate the involved owned assets, identify each logical
service and boundary, and name every unresolved conflict without guessing.

### Exact Agent Checkpoint Prompt

**Test state:** `PASS - CLEAN SESSION, 2026-08-19`

```text
Act as my read-only topology reconciler for one approved AI workflow. Use the
accepted NET-01 requirements brief and inventory, the accepted NET-02
connection map, and only evidence I supply. Do not run commands, browse private
systems, scan, contact anyone, or change network, provider, service, or file
state outside the buyer workspace.

First confirm the single outcome, exact production/test/lab target, workflow
owner, network-record owner, stable asset and connection IDs, authoritative
placement/configuration/data-handling sources, permitted read-only evidence
boundary, and opaque private evidence-reference convention. Mark a missing
value UNKNOWN. If the
target, owner, authority, or connection map is missing, produce a blocked
artifact and stop before drawing unsupported topology.

Create AI-GROWTH-WORKSPACE/artifacts/NETWORK-TOPOLOGY-AND-FLOW.md. If you
cannot write the file, print the complete artifact inline using the same
headings and tables from the supplied NETWORK-TOPOLOGY-AND-FLOW template.
Include:
1. artifact scope, owners, target, evidence boundary, checked date, and legend;
2. a physical view of sites, owned endpoints, network devices, hosts, link
   media, and external ownership boundaries;
3. a logical view of services, declared zones/segments, and NET-02 connection
   IDs;
4. a data-flow view for one outcome with connection IDs, data-category IDs,
   direction, transformations, retention, approvals, external crossings,
   readback, and record;
5. a complete text equivalent directly below each diagram;
6. node and edge registers with source, owner, checked date, and evidence basis;
7. a reconciliation register with issue ID, affected views/IDs, conflict,
   blocking state, owner, approved read-only evidence task, expected evidence,
   and state; and
8. readiness, evidence summary, blockers, and the smallest next action.

Preserve every accepted NET-01 asset ID and NET-02 C-## connection ID exactly;
never rename them. Assign S-##, Z-##, and D-## only when the accepted inputs do
not already provide a stable ID for that item. Use
OBSERVED, OWNER-STATED, RESEARCHED, INFERENCE, ASSUMPTION, or UNKNOWN for
evidence basis; keep RECOMMENDATION separate. A line records a mapped
relationship, not proof of reachability, encryption, identity, authorization,
security, or health. Do not infer a host, segment, port, medium, zone, payload,
or provider location. Do not expose private addresses, hostnames, credentials,
customer data, payloads, or raw configuration in the shareable artifact.

Set READY FOR NET-04 to NO when any selected-path node lacks an inventory ID,
any connection direction conflicts with NET-02, a logical service has no
supported placement or explicit UNKNOWN, a data crossing lacks an owner or
classification, evidence is stale or conflicting, or review authority is
missing. Convert each blocker into one bounded read-only evidence task. Do not
propose scanning, deployment, restarts, firewall/DNS/routing/proxy changes,
provider tests, or external contact.

Finish with READY FOR NET-04: YES or NO, evidence used, unresolved blockers,
the smallest safe next action, and the owner who must review it. Show the full
artifact and wait. Do not continue into NET-04 or take any action.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/NETWORK-TOPOLOGY-AND-FLOW.md`

It contains three linked diagrams and text equivalents, node and edge
registers, a reconciliation register, readiness, and review ownership. Raw
evidence and sensitive network values stay outside the shareable artifact and
appear only through opaque references.

### Pass Criteria

- Exactly one outcome and one target environment are in scope.
- Physical, logical, and data-flow views are separate, preserve inherited asset
  and connection IDs, and use stable shared IDs.
- Every diagram has a complete text equivalent in the same reading order.
- Every node and edge resolves to an accepted input or is marked `UNKNOWN`.
- Each material element has an owner, evidence basis, source, and checked date.
- Every data crossing has direction, classification, and handling ownership.
- Cross-view conflicts are assigned, bounded, and never silently reconciled.
- The readiness result, evidence, blockers, and next action agree.
- The artifact exposes no secret, private network value, customer payload, or
  unsupported provider detail and causes no live or external action.

### Stop Conditions

Stop and record the boundary when:

- the outcome, environment, owner, authority, inventory, or connection map is
  missing;
- current evidence conflicts with a selected-path placement or direction;
- a logical service or data crossing has no accountable owner;
- the only way to complete a view is to guess, scan, expose a sensitive value,
  contact an external party, or change live state;
- a proposed target design is being presented as current topology; or
- the reviewer asks the diagram to prove authorization, security, health,
  capacity, or recovery that requires a separate test.

An incomplete diagram with explicit unknowns is safer than a complete-looking
fiction. Keep `READY FOR NET-04: NO` until the blocking evidence is reviewed.

### Sources and Limits

This chapter uses original diagrams, IDs, example data, worksheet fields,
exercise, and prompt. It does not reproduce a textbook figure, topology,
example, table, or assessment.

- Solomon, Michael G., and David Kim. *Fundamentals of Communications and Networking*. 3rd ed., Jones & Bartlett Learning, 2022. Relevant foundation: Chapter 3's distinction between physical and logical network views. The source does not prescribe the three-view artifact, AI-service data flow, Harborlight diagrams, evidence rules, or a current network design.
- MADPANDA3D. *AI Growth Package V2.0.0*. Relevant foundation: current-state evidence labels and the needs-to-architecture role-and-flow method. The V2 material does not prove a buyer's topology or authorize inspection or change.

### Next Step

Continue to **NET-04: Use Layers to Locate Failures** only when
`NETWORK-TOPOLOGY-AND-FLOW.md` says `READY FOR NET-04: YES`. Use the reconciled
nodes and connections as the system map; do not redesign the topology while
building the failure-location card.


## 13. Use Layers to Locate Failures

> **Chapter handle:** `NET-04`.

### Objective

Locate the first failed or unproven diagnostic band for one connection without
turning a symptom into a root-cause guess or changing the network.

### Required Inputs

- the accepted `NETWORK-TOPOLOGY-AND-FLOW.md` from `NET-03`;
- one symptom, timestamp, target environment, and affected outcome;
- the relevant asset, service, zone, data, and `C-##` connection IDs;
- current evidence already collected within the approved read-only boundary;
- the owner of each involved service or network boundary; and
- the opaque private evidence-reference convention.

Stop with an intake row when the environment, connection, symptom, owner, or
inspection authority is unclear. Do not test several paths at once or widen a
read-only diagnosis into a scan, restart, policy change, or deployment.

### Why This Matters

"The AI is down" is not a diagnosis. The operator interface may load while
retrieval fails. A service name may resolve while no process accepts the
connection. A port may accept a connection while the application rejects the
request. A valid response may still contain the wrong document or fail the
business outcome.

Layer models separate those responsibilities. They also limit conclusions.
An active cable does not prove a route. A route does not prove a listening
service. A successful transport exchange does not prove a correct application
response. A correct response does not prove the agent was authorized to act.

The goal is the first useful boundary: the lowest prerequisite already proven,
the next failed or unknown band, its owner, and the smallest safe evidence task.
Repair belongs to a separately reviewed change record.

### Core Model

The seven-layer Open Systems Interconnection model is useful when encoding,
sessions, frames, or physical signaling need separate attention. The Internet
protocol suite commonly groups responsibilities into application, transport,
internet, and link layers. For one AI workflow, use this five-band diagnostic
stack:

| Band | Bounded question | Components or evidence often involved |
| --- | --- | --- |
| **Outcome** | Did the approved user-visible result occur? | Trigger, approval, returned answer, source fidelity, readback, record; this is not a protocol layer |
| **Application** | Did the named service understand and correctly answer the request? | Service role, application protocol, name-resolution dependency, TLS handling, identity, request schema, health and error response |
| **Transport** | Could the endpoints exchange through the expected transport and receiving port? | TCP or UDP, listener, port, connection state, timeout, reset, datagram behavior |
| **Internet** | Could packets be addressed and routed toward the correct network destination? | Source and destination address scope, route, gateway, IP and control errors |
| **Link and media** | Could the local interface exchange on its current directly connected network? | Interface, local segment, switch or access point, virtual link, wired/wireless medium |

[RFC 1122](https://www.rfc-editor.org/info/rfc1122/) describes the Internet
architecture using application, transport, internet, and link layers. It has
updates, so use it here as architecture context rather than a current protocol
configuration guide. [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html)
is the current core TCP specification and identifies TCP as a transport-layer
protocol whose segments are carried in Internet datagrams.

Layer placement is a diagnosis aid, not a universal product diagram. TLS may
be implemented in an application, library, proxy, or service mesh. Virtual
switching may be software. DNS is an application-layer service whose own
request has transport, internet, and link prerequisites. Record the actual
component and avoid arguing about a label when the evidence boundary is clear.

### The Proof-Boundary Rule

Every result has a maximum conclusion:

| Result | It supports | It does not support |
| --- | --- | --- |
| Link evidence passes | The inspected local interface or segment worked in that context | Remote route, listener, service health, or authority |
| Internet evidence passes | The host had the recorded address/route result for that destination and time | End-to-end delivery, open port, or correct application |
| Transport evidence passes | The expected transport exchange reached the recorded endpoint in that context | Correct identity, valid request, useful answer, or permission |
| Application evidence passes | The named application returned the expected protocol and content result | Every dependency, future availability, or business completion |
| Outcome evidence passes | The selected test case reached readback and record | General security, capacity, recovery, or unrestricted authority |

Use `PASS`, `FAIL`, `UNKNOWN`, or `NOT RUN`. `PASS` needs current `OBSERVED`
evidence. `OWNER-STATED`, `RESEARCHED`, `INFERENCE`, and `ASSUMPTION` may guide
the next question but cannot silently establish a live pass. Keep
`RECOMMENDATION` separate.

Record Outcome as symptom context, not the diagnostic stop. Walk required
prerequisites bottom-up: Link and media, Internet, Transport, Application, then
Outcome. The first `FAIL` or consequential `UNKNOWN` is the boundary. Mark
dependent higher bands `NOT RUN` unless already supplied as symptom context.

### Ordered Method

**Step 1 - Freeze the incident.** Record one symptom, one outcome, one
environment, one time window, and the affected connection IDs. Separate
current failure evidence from an old incident or desired design.

**Step 2 - State the expected behavior.** Define what should happen at the
outcome and application bands. "Works" is too vague; name the expected
response, readback, and record.

**Step 3 - Preserve the last proof.** Copy only fresh, relevant evidence from
the accepted connection and topology artifacts. Do not retest a healthy band
merely to create activity.

**Step 4 - Walk upward from prerequisites.** Record the Outcome or Application
symptom, then evaluate only required bands from the lowest prerequisite upward.
Reuse current observed passes; do not rerun them.

**Step 5 - Bind each question to a component.** Name the `C-##`
connection, initiator, receiver, service, host, zone, and owner. A layer alone
cannot own a ticket.

**Step 6 - Stop at the bottom-up boundary.** The first required band that is
`FAIL` or consequentially `UNKNOWN` after lower prerequisites pass is the
boundary. Record what it proves, what it cannot prove, alternatives, and one
permitted evidence task. Do not jump from "transport timeout" to "firewall
blocked it." A receiver, route, listener, or policy cause may remain open.

**Step 7 - Review and hand off without repair.** Set `READY FOR NET-05: YES`
only when inputs are confirmed, the boundary or all-pass result is reproducible,
the owner and permitted task are named, and Diagnostic-method review and
Current-topology review are `PASS`. A localized failure may be ready without
repair. Set `NO` when a condition is absent, evidence is stale or conflicting,
or the next task exceeds authority.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
| --- | --- | --- |
| Quick | You need to translate a vague symptom. | Name the outcome, connection, suspected band, and one fact the current evidence cannot prove. |
| Operator | You own the running workflow. | Complete the card through the first failed or unknown band and assign its owner. |
| Builder | You are validating a new slice. | Add an expected result and evidence source for every band the slice depends on. |
| Architect | You are reviewing failure domains and handoffs. | Map shared components, cross-zone owners, ambiguous band boundaries, and promotion triggers. |
| Lab | You need a safe diagnosis rehearsal. | Use fictional or isolated evidence, inject one failure, locate it, and explain why repair was not yet authorized. |

### Fictional Example

> **Fictional scenario.** Harborlight Workshop's operator interface loads, but
> a grounded question times out. The accepted map shows retrieval on `C-03`.
> No live command or real address is used.

| Step | Band | Supplied evidence | Result | Maximum conclusion |
| --- | --- | --- | --- | --- |
| L-00 | Outcome context | No answer or source record returned for the test question | `FAIL` | The selected workflow outcome failed; this is symptom context, not the diagnostic stop |
| L-01 | Link and media | Initiator interface and local virtual link are observed up | `PASS` | The inspected local link is available; the remote path is not proven |
| L-02 | Internet | Initiator has a current route decision for the expected private address scope | `PASS` | Local route selection exists; end-to-end delivery is not proven |
| L-03 | Transport | Current fictional trace records a TCP connection timeout on `C-03` | `FAIL` | Expected transport exchange was not observed; cause remains open |
| L-04 | Application | Transport boundary prevents a supported application check | `NOT RUN` | Application success remains unproven |

The first failed band with bounded evidence is transport on `C-03`. The card
does not call the firewall, route, or retrieval process the root cause. The
next task belongs to the service and network owners: review the expected
listener and approved path evidence in the correct service context. No restart,
rule change, or broad port test is authorized.

### Decision path visual

```text
[Outcome symptom context + environment + C-##]
                         |
          [Lowest required prerequisite]
                         |
[Link proof?] -- fail/unknown → boundary; otherwise continue upward
                         |
[Internet proof?] -- fail/unknown → boundary; otherwise continue upward
                         |
[Transport proof?] -- fail/unknown → boundary; otherwise continue upward
                         |
[Application proof?] -- fail/unknown → boundary; otherwise check Outcome
                         |
     [All required bands pass in the bounded test]
```

Text equivalent: record the symptom and connection, then walk only its required
prerequisites from the lowest band upward. Stop at the first fail or
consequential unknown after lower passes. Record its component, owner, evidence
limit, and safe next task. Do not continue into repair.

### Exercise or Test

Create `LAYER-TO-COMPONENT-DIAGNOSIS-CARD.md` from the supplied template using
fictional evidence or evidence already collected inside an approved read-only
boundary. One row must state the expected result; each later row must name its
prerequisite, component, owner, evidence basis, result, maximum conclusion, and
next task.

The exercise passes when a second reviewer can identify the first failed or
unproven band, explain why lower passes do not prove higher success, and route
the next decision without a configuration change.

### Exact Agent Checkpoint Prompt

**Test state:** `PASS - NORMAL AND BLOCKED CLEAN-SESSION ROUTES, 2026-08-19`

```text
Act as my read-only layered failure locator for one mapped AI-workflow
connection. Use only the accepted NET-03 topology, symptom, and evidence I
provide. Do not run commands, browse private systems, scan, restart, deploy,
change DNS/firewall/routing/proxy/service/container/credential/provider state,
or contact anyone.

First confirm the outcome, exact production/test/lab target, symptom and time
window, affected C-## connection, initiator and receiver, service/asset/zone
IDs, expected application and outcome behavior, evidence freshness rule,
permitted read-only boundary, opaque evidence-reference convention, and owners.
Mark missing values UNKNOWN. If target, connection, owner, expected behavior,
or authority is unclear, produce a blocked card and stop.

Create AI-GROWTH-WORKSPACE/artifacts/LAYER-TO-COMPONENT-DIAGNOSIS-CARD.md from
the exact supplied template. If file writing is unavailable, print the complete
artifact inline and do not claim it was saved. Use the five diagnostic bands:
Outcome (not a protocol layer), Application, Transport, Internet, and Link and
media. For each needed row include step ID, band, C-## and component IDs,
bounded question, prerequisite, expected evidence, supplied actual evidence,
evidence basis and checked time, PASS/FAIL/UNKNOWN/NOT RUN result, maximum
supported conclusion, what remains unproven, owner, opaque evidence reference,
and smallest permitted next evidence task.

Only current OBSERVED evidence may establish PASS. Keep OWNER-STATED,
RESEARCHED, INFERENCE, ASSUMPTION, UNKNOWN, and RECOMMENDATION distinct. Record
Outcome as symptom context, then evaluate only the mapped connection's required
prerequisites from the lowest band upward: Link and media, Internet, Transport,
Application, then Outcome. Preserve fresh observed passes. Stop at the first
FAIL or consequential UNKNOWN in that bottom-up walk and mark dependent higher
bands NOT RUN unless already recorded as symptom context. A link pass does not
prove a route; a route result does not prove transport; transport does not
prove application behavior; application response does not prove the workflow
outcome or authorization.

Do not infer root cause from a timeout, refusal, name failure, or error string.
List bounded alternatives supported by the map. Do not request secrets, raw
customer data, private addresses, hostnames, or full configuration in the
shareable card. Do not propose a repair as evidence.

Finish with FIRST FAILED OR UNPROVEN BAND, evidence used, open alternatives,
owner, smallest safe evidence task, Diagnostic-method review, Current-topology
review, and READY FOR NET-05: YES or NO. READY is YES only when inputs are
confirmed, the bottom-up boundary or all-pass result is reproducible, the owner
and permitted task are named, and both reviews are PASS. A localized failure
may be ready without repair. Otherwise READY is NO. Show the complete card and
wait. Do not repair the incident or continue to NET-05.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/LAYER-TO-COMPONENT-DIAGNOSIS-CARD.md`

It contains incident scope, the five-band reference, diagnosis rows, evidence
limits, first failed or unproven band, owner handoff, and readiness. Sensitive
evidence stays outside the shareable artifact and appears only through opaque
references.

### Pass Criteria

- One symptom, environment, outcome, and connection are in scope.
- Outcome is clearly distinguished from protocol layers.
- Each needed band has an exact component, question, prerequisite, evidence,
  result, maximum conclusion, owner, and next task.
- Current observed evidence is required for `PASS`; unknowns remain explicit.
- The first failed or unproven band is named without an unsupported root cause.
- The boundary comes from the required bottom-up walk, not the Outcome symptom.
- Lower-layer passes are not presented as proof of higher-layer behavior.
- The card's evidence, alternatives, owner, next task, and readiness agree.
- Diagnostic-method and current-topology reviews are separately auditable.
- No secret, sensitive value, scan, contact, restart, deployment, or live
  change is requested or performed.

### Stop Conditions

Stop when the target, connection, expected behavior, authority, or owner is
missing; evidence belongs to another environment or time window; a check would
leave the approved boundary; the next step requires sensitive disclosure or
external contact; or the only available continuation is an unreviewed repair.

### Sources and Limits

- Solomon, Michael G., and David Kim. *Fundamentals of Communications and Networking*. 3rd ed., Jones & Bartlett Learning, 2022. Relevant foundation: Chapter 3 on OSI and TCP/IP reference models. The source does not prescribe the five-band card, Harborlight evidence, decision path, or current protocol implementation.
- Braden, R., ed. [Requirements for Internet Hosts - Communication Layers, RFC 1122 / STD 3](https://www.rfc-editor.org/info/rfc1122/), IETF, 1989. Status and updates checked August 19, 2026. Used for Internet-suite architecture context, not current TCP requirements or configuration defaults.
- Eddy, W., ed. [Transmission Control Protocol (TCP), RFC 9293 / STD 7](https://www.rfc-editor.org/rfc/rfc9293.html), IETF, 2022. Checked August 19, 2026. Supports TCP's current core transport specification and its relationship to Internet datagrams; it does not define this diagnosis method.

### Next Step

Continue to **NET-05: Plan Switching, Addressing, and Subnets** only after the
diagnosis card and topology are reviewed. Carry forward exact asset, zone, and
connection IDs; do not turn a failure hypothesis into an addressing change.


## 14. Plan Switching, Addressing, and Subnets

> **Chapter handle:** `NET-05`.

### Objective

Plan the link attachment, address scope, and subnet boundary for one mapped
AI-workflow connection without discovering devices or changing the network.

### Required Inputs

- the accepted `NET-03` topology and stable asset, service, zone, and `C-##` IDs;
- the accepted `NET-04` diagnosis card and proof boundaries;
- an approved environment and connection;
- supplied switch, virtual-network, or shared-host attachment evidence;
- endpoint count, growth horizon, availability need, and address family; and
- network owner, allocation authority, read-only inspection boundary, opaque
  evidence-reference convention, and private-value boundary.

Stop when environment, connection, attachment owner, or allocation authority is
missing. Do not scan, enumerate interfaces, inspect live tables, reserve
addresses, create a VLAN, change DHCP, or configure a host.

### Why This Matters

An IP address is not a network plan. Two services may share a host but use a
loopback or bridge; two switched hosts may occupy different logical segments.
Private IPv4 does not prove isolation. A prefix may overlap another environment,
hide a gateway dependency, or leave no governed growth room.

The artifact separates three questions:

1. What link or virtual attachment carries the connection?
2. What address family, prefix purpose, and scope should represent it?
3. Which routing, assignment, naming, and policy handoffs remain outside this
   chapter?

This plans one slice. `NET-06` owns naming, DHCP, and time; `NET-07`
owns routing, gateways, NAT, ports, and egress; `NET-09` owns VLAN and trust-zone
design. Record those handoffs without configuring them.

### Core Model

Use stable planning IDs in addition to inherited topology IDs:

- `BD-##` identifies one declared Layer 2 or virtual broadcast scope;
- `PFX-##` identifies one address prefix or subnet purpose; and
- `AH-##` identifies one allocation or gateway handoff.

These IDs describe the plan. They do not prove that a switch port, virtual
network, prefix, address, gateway, or policy exists.

| Boundary | Planning question | Do not infer |
| --- | --- | --- |
| Link attachment | Which physical switch, virtual bridge, wireless segment, shared host, or other link context carries `C-##`? | A switch attachment does not prove an IP route or trust boundary |
| Broadcast or multicast scope | Which endpoints receive link-local discovery or group traffic in this context? | A switch port, subnet, and security zone are not automatically one-to-one |
| IP prefix | Which IPv4 or IPv6 prefix identifies the intended network scope? | Prefix membership does not prove reachability, identity, or permission |
| Allocation handoff | Who assigns interface addresses and gateway information, by which approved method? | A planned pool does not authorize DHCP, static assignment, SLAAC, or deployment |
| Higher boundary | Which router, firewall, name, time, or egress dependency owns the next hop? | Do not solve later chapters by inserting assumed values here |

For IPv4, a prefix length `/p` leaves `32 - p` address bits, so a block contains
`2^(32-p)` addresses. Do not mechanically subtract two for every environment;
usable endpoint count depends on the specific network convention and platform.
For IPv6, do not use IPv4 host-count habits as the allocation method. Record
scope, prefix source, delegation, platform constraints, and the current owner.

### Address-scope controls

| Address class | Bounded use | Required warning |
| --- | --- | --- |
| RFC 1918 private IPv4 | Internal IPv4 planning under enterprise ownership | Private is not the same as segmented, encrypted, authenticated, or unreachable |
| IPv6 link-local | Communication on one link within its defined scope | It is not a substitute for a routed site or global plan |
| IPv6 unique local | Local IPv6 communication under an owned prefix plan | It is not IPv4 private space with identical behavior |
| IPv6 global unicast | Routable scope under assigned or provider policy | Global scope does not imply public service exposure or permission |
| Documentation space | Fictional examples and shareable training artifacts | Never assign documentation-only values to a production endpoint |

IPv6 has no broadcast address; multicast provides the one-to-many
mechanism. A worksheet that says "broadcast" for IPv6 without naming the actual
multicast or discovery dependency is incomplete. RFC 4291 has updates, so use
its architecture with current platform and provider guidance before deployment.

### Ordered Method

**Step 1 - Freeze one connection.** Record the outcome, environment, `C-##`,
initiator, receiver, service roles, physical placement, zones, and owner.

**Step 2 - Reconcile the attachment.** Use the accepted topology to determine
whether the path is physical switch, virtual bridge, same-host, wireless, or
unknown. Create a `BD-##` only for a declared scope. Never add a switch merely
because two nodes appear in a logical diagram.

**Step 3 - State the prefix purpose.** Create a `PFX-##` with address family,
scope, environment, workload purpose, endpoint classes, and isolation claim.
Use `UNKNOWN` when the real prefix or boundary is private or unverified.

**Step 4 - Size for the owned horizon.** Record current endpoint need, approved
growth horizon, reservations, infrastructure dependencies, and failure-domain
limits. Capacity is a planning estimate until an owner approves the allocation.

**Step 5 - Record assignment and gateway handoffs.** Create `AH-##` rows for
static, DHCP, SLAAC, provider, or other assignment ownership and the expected
gateway or no-gateway decision. Do not configure or test those mechanisms here.

**Step 6 - Check collisions and boundaries.** Review overlap with supplied
prefix records, address-family mismatch, duplicate purpose, public/private/local
scope, and connection-to-zone consistency. An overlap check is `UNKNOWN` when
the authoritative register is unavailable; do not scan to fill the gap.

**Step 7 - Split shareable plan from private values.** The shareable worksheet
contains purposes, capacities, states, owners, and documentation-only examples.
Real prefixes, interface addresses, switch ports, and gateway values remain in
the approved private register behind opaque references.

**Step 8 - Review readiness.** `YES` requires a confirmed connection; a current
`OBSERVED` or `OWNER-STATED` attachment; every `PFX-##` at readiness and overlap
`PASS`; explicit owned assignment and gateway decisions or later handoffs;
fresh evidence; a private-value boundary; and both reviews at `PASS`. Otherwise
set `READY FOR NET-06: NO`. Readiness is not deployment approval.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
| --- | --- | --- |
| Quick | Classify one connection. | Name attachment, family, purpose, owner, and unknown. |
| Operator | You maintain a small AI environment. | Complete `BD`, `PFX`, and `AH` rows for every endpoint on one approved connection. |
| Builder | You are preparing an isolated lab slice. | Use documentation-only examples, calculate bounded capacity, and prove no real assignment occurred. |
| Architect | You own several environments. | Reconcile overlap, delegation, growth, failure domains, and later routing or segmentation handoffs. |
| Lab | You need a safe subnet exercise. | Calculate with fictional prefixes, label every assumption, and compare the result with an independent review. |

### Fictional Example

> **Fictional scenario.** Harborlight Workshop plans retrieval on `C-03`, from
> `S-02` to `S-03`. Both are on `NET-A004`, but the topology does not prove a
> host, namespace, bridge, switch, or prefix. No live system is inspected.

| ID | Proposed record | Evidence state | Decision |
| --- | --- | --- | --- |
| `BD-01` | Attachment scope for `C-03` | `UNKNOWN`; same-host placement is known, but loopback, namespace, bridge, and switch behavior are not | Ask the environment owner to identify the approved attachment type through an opaque reference |
| `PFX-01` | Current prefix purpose and family | `UNKNOWN`; real values remain in the private register | Record purpose and owner before choosing any value |
| `LAB-PFX-01` | Fictional IPv4 training prefix | `RECOMMENDATION`; use only RFC 5737 documentation space | Label `DOCUMENTATION ONLY - NOT DEPLOYABLE` |
| `LAB-PFX-02` | Fictional IPv6 training prefix | `RECOMMENDATION`; use only current IPv6 documentation space | Label `DOCUMENTATION ONLY - NOT DEPLOYABLE` |
| `AH-01` | Address assignment and gateway ownership | `OWNER-STATED`; method and gateway choice are not approved | Hand the decision to `NET-06` and `NET-07` without configuring it |

The useful result is a bounded record showing that attachment and prefix remain
unknown, who owns those facts, and which fictional examples are safe.
`READY FOR NET-06` remains `NO` until the owner confirms attachment, purpose,
capacity basis, overlap authority, and the private-value boundary.

### Boundary visual

```text
[S-02 / NET-A004] -- C-03 -- [S-03 / NET-A004]
          |                         |
          +-- [BD-01 attachment UNKNOWN]
                         |
            [PFX-01 purpose + scope UNKNOWN]
                         |
      [AH-01 assignment and gateway owner review]
                         |
       [NET-06 names/DHCP/time] → [NET-07 route/egress]
```

Text equivalent: `C-03` connects `S-02` and `S-03`. Attachment and prefix remain
unknown. The allocation owner must review the method; `NET-06` owns naming,
DHCP, and time, while `NET-07` owns route, gateway, and egress.

### Exercise or Test

Create `ADDRESS-SUBNET-AND-BROADCAST-DOMAIN-WORKSHEET.md` from the supplied
template for one accepted `C-##` connection. Use only sanitized evidence and
documentation-only examples. Include one attachment row, one prefix-purpose
row, and one allocation or gateway handoff. If a real value is required to
complete a check, leave the shareable field `PRIVATE - SEE OPAQUE REFERENCE` or
`UNKNOWN`; do not copy the value into the worksheet.

The exercise passes when a reviewer can explain the declared link scope,
prefix purposes, capacity basis, allocation and overlap owners, and later
handoffs. It fails when a guessed address, port, gateway, VLAN, or route is
presented as observed fact.

### Exact Agent Checkpoint Prompt

**Test state:** `PASS - NORMAL AND BLOCKED CLEAN-SESSION ROUTES, 2026-08-19`

```text
Act as my read-only switching, addressing, and subnet planner for one accepted
AI-workflow connection. Use only the accepted NET-03 topology, accepted NET-04
diagnosis card, and sanitized evidence I supply. Do not run commands, browse,
scan, enumerate interfaces or devices, inspect live switch/neighbor/route/DHCP
tables, reserve addresses, or change host, switch, VLAN, DHCP, DNS, route,
gateway, firewall, provider, or deployment state.

First confirm the environment and outcome, exact C-## connection and endpoint
IDs, physical or virtual placement, supplied attachment evidence, address-family
need, endpoint demand and growth horizon, owner, allocation authority, evidence
freshness, opaque-reference convention, and private-value boundary. Mark missing
facts UNKNOWN. If the environment, connection, attachment owner, allocation
authority, or inspection boundary is unclear, produce a blocked worksheet and
stop.

Create AI-GROWTH-WORKSPACE/artifacts/ADDRESS-SUBNET-AND-BROADCAST-DOMAIN-WORKSHEET.md
from the exact supplied template. If file writing is unavailable, print the
complete artifact inline and do not claim it was saved. Create stable BD-##,
PFX-##, and AH-## rows. Each BD row must name its C-## connection, endpoints,
attachment type, broadcast or multicast scope, evidence state, owner, checked
time, opaque reference, and limit. Each PFX row must name family, purpose,
scope, demand, growth, reservations, prefix or UNKNOWN, capacity method,
overlap state, zone relationship, owner, and readiness. Each AH row must name
assignment method or UNKNOWN, owner, gateway or no-gateway decision, later
dependency, evidence reference, and next task.

Use only sanitized values already supplied. Never request or expose real
prefixes, interface addresses, hostnames, switch ports, gateways, neighbor
records, or full configurations in the shareable artifact. Use documentation
examples only when I supply them and confirm they are current documentation
space; label every such value DOCUMENTATION ONLY - NOT DEPLOYABLE. Treat RFC
1918 private IPv4 as an address scope, not proof of isolation, encryption,
identity, or permission. Do not use IPv4 broadcast language for IPv6 and do not
size IPv6 by copying an IPv4 host-count habit.

Finish with the overlap state, blockers, smallest owner-assigned evidence task,
Address-plan review, Private-value-boundary review, and READY FOR NET-06: YES or
NO. READY is YES only when the connection is confirmed; attachment is current
OBSERVED or OWNER-STATED with an owner; every PFX has purpose, family, capacity
basis, readiness PASS, and overlap PASS; every AH has a named owner plus an
explicit assignment and gateway decision or later-chapter handoff; evidence is
fresh; the private boundary is recorded; and both reviews are PASS. Any other
state makes READY NO; UNKNOWN or CONFLICT overlap also makes Address-plan review
REPAIR. Show the worksheet and wait. Do not configure or continue to NET-06.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/ADDRESS-SUBNET-AND-BROADCAST-DOMAIN-WORKSHEET.md`

The worksheet records scope, link behavior, prefix purpose and capacity,
allocation and gateway handoffs, overlap, reviews, and readiness. Real values
remain private behind opaque references.

### Pass Criteria

- One accepted environment, outcome, connection, and endpoint pair are in scope.
- Every `BD-##`, `PFX-##`, and `AH-##` row has an owner and evidence state.
- Attachment type is distinguished from prefix, route, zone, and permission.
- IPv4 broadcast scope and IPv6 multicast behavior are not conflated.
- Prefix purpose, family, capacity basis, and overlap are recorded without a
  deployable value.
- Every in-scope prefix overlap state is `PASS`; `UNKNOWN` or `CONFLICT` blocks
  readiness and makes Address-plan review `REPAIR`.
- Attachment is current `OBSERVED` or `OWNER-STATED`; each prefix readiness is
  `PASS`; and each allocation or gateway decision has an owned handoff.
- Private IPv4 is not proof of segmentation or authorization.
- Documentation-only examples are labeled and never treated as allocations.
- Address-plan and private-value-boundary reviews are auditable.
- `READY FOR NET-06` follows the stated rule and does not authorize deployment.
- No discovery, sensitive disclosure, reservation, configuration, or contact
  occurs.

### Stop Conditions

Stop when environment, connection, owner, authority, freshness, or the
private-value rule is missing; overlap is unknown or conflicting; attachment
would require discovery; or the next action would reserve, assign, configure,
route, segment, contact, or deploy. Record the blocker and owner task.

### Sources and Limits

- Solomon, Michael G., and David Kim. *Fundamentals of Communications and Networking*. 3rd ed., Jones & Bartlett Learning, 2022. Foundation: Chapters 3 and 5 on switching and addressing. It does not prescribe the worksheet.
- Rekhter, Y., et al. [Address Allocation for Private Internets, RFC 1918 / BCP 5](https://www.rfc-editor.org/info/rfc1918/), IETF, 1996. Status checked August 19, 2026. Used for private IPv4 scope; it does not establish isolation or permission and is updated by RFC 6761.
- Fuller, V., and T. Li. [Classless Inter-domain Routing (CIDR), RFC 4632 / BCP 122](https://www.rfc-editor.org/info/rfc4632/), IETF, 2006. Checked August 19, 2026. Used for prefix-length context, not local allocation approval.
- Hinden, R., and S. Deering. [IP Version 6 Addressing Architecture, RFC 4291](https://www.rfc-editor.org/info/rfc4291/), IETF, 2006; and Hinden, R., and B. Haberman. [Unique Local IPv6 Unicast Addresses, RFC 4193](https://www.rfc-editor.org/info/rfc4193/), IETF, 2005. Status and updates checked August 19, 2026. Used for IPv6 scope distinctions; current platform and provider guidance remains required.
- Arkko, J., et al. [IPv4 Address Blocks Reserved for Documentation, RFC 5737](https://www.rfc-editor.org/info/rfc5737/), IETF, 2010; Huston, G., et al. [IPv6 Address Prefix Reserved for Documentation, RFC 3849](https://www.rfc-editor.org/info/rfc3849/), IETF, 2004; and Huston, G., and N. Buraglio. [Expanding the IPv6 Documentation Space, RFC 9637](https://www.rfc-editor.org/info/rfc9637/), IETF, 2024. Checked August 19, 2026. Documentation space is for examples, not production assignment.

### Next Step

Continue to **NET-06: Map DNS, DHCP, Time, Names, and Dependencies** only after
the address worksheet has both reviews at `PASS` and `READY FOR NET-06: YES`.
Carry forward IDs, owners, states, and opaque references, not private values.


## 15. Stabilize DNS, DHCP, Time, Names, and Dependencies

> **Chapter handle:** `NET-06`.

### Objective

Map address configuration, name resolution, and time dependencies for one
AI-workflow connection without live queries or changes.

### Required Inputs

- the accepted `NET-03` topology and `NET-05` address worksheet;
- one outcome, environment, `C-##` connection, and endpoint/service IDs;
- supplied address-method, resolver, name-purpose, and time-source evidence;
- evidence freshness, opaque private-reference convention, and inspection
  boundary; and
- service and dependency owners.

If scope, owner, evidence time, or inspection authority is unclear, stop with
an intake map. Do not query DNS, leases, or clocks; expose names or addresses;
change configuration; or restart services.

### Why This Matters

An application can have an address but use the wrong resolver. A cached name
can resolve while the target is unavailable. A host can display expected time
while synchronization is unknown. Logs can then misorder one event.

These are separate dependencies, not one health signal. A DHCP lease does not
prove identity or permission; a DNS answer does not prove transport or
application success; a configured time source does not prove synchronization
quality or authenticated time.

This chapter records the first blocking dependency and owner.
It does not select servers, reveal real names, set tolerances, or repair a path.

### Core Model

Use `DEP-##` for one consumer-to-foundational-service dependency.

| Service area | Bounded question | Maximum supported conclusion |
| --- | --- | --- |
| Address configuration | Which approved method supplies the consumer's address, prefix, and related parameters? | Current supplied evidence supports that configuration state only, not identity, reachability, or authorization |
| Name resolution | Which name purpose, resolver path, query name, type, class, and view serve this consumer? | One fresh answer supports that query context only, not endpoint identity or application success |
| Time | Which source, synchronization method, tolerance owner, and authentication state support the consumer? | Current sync evidence supports the checked clock context only, not every dependent timestamp |

Separate display label, service role, alias, DNS name, and provider endpoint;
similar strings may have different owners and proof. Keep real values in the
private register behind opaque references.

Use `PASS`, `FAIL`, `UNKNOWN`, `NOT REQUIRED`, or `NOT RUN`. Only current
`OBSERVED` establishes `PASS`. `OWNER-STATED` records design, not live service.
`NOT REQUIRED` needs a reason and owner.

### Ordered Method

**Step 1 - Freeze one connection.** Record the outcome, environment, `C-##`,
consumer, target service, address family, owners, and evaluation order.

**Step 2 - List exact consumers.** Create one row per host, container, service,
agent, proxy, or managed boundary that directly consumes address, name, or time
behavior. Do not assume co-located services share the same configuration.

**Step 3 - Map address configuration.** Record static, DHCPv4, DHCPv6, provider,
or other approved method; configuration owner; supplied evidence; checked time;
downstream resolver or gateway handoff; and proof limit. Leave real values
private.

**Step 4 - Map each name purpose.** Record whether a name is for human display,
service lookup, certificate matching, provider routing, or another owned use.
Name the resolver owner, expected query type and class, consumer,
cache/freshness rule, and supplied result. Do not turn a match into identity.

**Step 5 - Map time consumers.** Record the approved source class, sync owner,
current evidence, checked time, workload tolerance owner, authentication state,
and dependent logs, tokens, certificates, schedulers, or records. Do not invent
a universal tolerance.

**Step 6 - Draw dependency edges.** Connect consumers, required services, and
owners. Declare the evaluation order. A circular, missing, stale, or
cross-environment edge is a blocker.

**Step 7 - Stop the affected branch.** Evaluate prerequisite branches in
workflow order. At a block, mark only its transitive dependents `NOT RUN`.
Preserve and evaluate independent supplied-evidence rows. Assign one task only
to the earliest required blocker; defer later blockers. Do not query or fix.

**Step 8 - Review readiness.** `READY FOR NET-07: YES` requires every required
`DEP-##` at `PASS`, justified `NOT REQUIRED` rows, current evidence, explicit
owners, proof limits, private values excluded, and both reviews at `PASS`. Any
required `FAIL`, `UNKNOWN`, or
`NOT RUN` row, stale evidence, or unjustified omission makes readiness `NO`.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
| --- | --- | --- |
| Quick | Classify one symptom. | Name its address, name, or time dependency, state, owner, and largest unknown. |
| Operator | Maintain one workflow. | Map every required foundational edge and first blocker. |
| Builder | Prepare a service handoff. | Add expected evidence, freshness, proof limits, and private references. |
| Architect | Govern several environments. | Reconcile split views, shared services, circular dependencies, owners, and failure domains. |
| Lab | Rehearse without live queries. | Use fictional records, make one dependency stale, and locate the first block. |

### Fictional Example

> **Fictional scenario.** Harborlight Workshop maps retrieval on `C-03`. The
> owner supplies sanitized evidence; no resolver, lease, or clock is queried.

| DEP-## | Consumer and dependency | Evidence state | Proof limit / decision |
| --- | --- | --- | --- |
| `DEP-01` | `S-02` requires approved address configuration | `OWNER-STATED`; method is named but current state is unobserved | `UNKNOWN`; configuration owner supplies a fresh opaque proof |
| `DEP-02` | `S-02` requires the approved resolver path for the `S-03` service role | `OBSERVED`; sanitized selection evidence is fresh | `PASS` for resolver selection only; no query or reachability proven |
| `DEP-03` | `S-02` requires a current service-name result | `NOT RUN` because `DEP-01` blocks the bounded sequence | No inference from an older cached answer |
| `DEP-04` | Both services require the owned time basis for record ordering | `OWNER-STATED`; synchronization quality is absent | `UNKNOWN`; later blocker deferred behind `DEP-01` |

Evaluation order is `DEP-01`, `DEP-02`, `DEP-03`, then `DEP-04`; `DEP-03`
requires both `DEP-01` and `DEP-02`. `READY FOR NET-07` is `NO`. The only next
task belongs to `DEP-01`; `DEP-04` is deferred. The map guesses no repair.

### Dependency visual

```text
[S-02 / C-03]
   |-- DEP-01 → [Address configuration owner] : UNKNOWN
   |-- DEP-02 → [Resolver selection owner]    : PASS, bounded
   |-- DEP-03 → [Service-name result owner]   : NOT RUN
   +-- DEP-04 → [Time owner]                  : UNKNOWN
```

Text equivalent: `S-02` depends on address configuration, resolver selection,
a service-name result, and time. Address and time are unknown; the name-result
check is not run; only resolver selection has a bounded pass.

### Exercise or Test

Create `FOUNDATIONAL-SERVICES-DEPENDENCY-MAP.md` for one accepted connection.
Use supplied sanitized evidence, stop only the affected branch, preserve
independent evidence, and assign only the earliest blocker task.

### Exact Agent Checkpoint Prompt

**Test state:** `PASS - NORMAL AND BLOCKED CLEAN-SESSION ROUTES, 2026-08-19`

```text
Act as my read-only foundational-services dependency mapper for one accepted
AI-workflow connection. Use only the accepted NET-03 topology, NET-05 address
worksheet, and sanitized evidence I provide. Do not run commands; query DNS;
read leases, resolver caches, or clocks; scan; expose real names or addresses;
contact anyone; restart; configure; or continue into routing changes.

Confirm the outcome, environment, C-##, consumers, target service, address
family, supplied address method, name purposes, resolver evidence, time-source
evidence, freshness rule, opaque-reference convention, inspection boundary,
and owners. Mark missing facts UNKNOWN. If connection, consumer, owner,
freshness, or authority is unclear, produce a blocked map and stop.

Create AI-GROWTH-WORKSPACE/artifacts/FOUNDATIONAL-SERVICES-DEPENDENCY-MAP.md
from the exact template. If writing is unavailable, print it and do not claim
it was saved. Create one DEP-## per consumer dependency. Record service area,
consumer, upstream owner, purpose, evaluation order, prerequisite DEP-## ID(s),
query type/class or N/A, expected evidence,
supplied evidence and class, checked time, PASS/FAIL/UNKNOWN/NOT REQUIRED/NOT RUN
state, maximum conclusion, still unproven, opaque reference, and task or defer reason.

Only current OBSERVED evidence establishes PASS. Keep real names, addresses,
leases, resolver endpoints, and time sources private. Distinguish display label,
service role, alias, DNS name, and provider endpoint. A lease does not prove
identity or authorization; a DNS answer does not prove transport, service
health, or identity; a configured clock source does not prove sync quality or
authenticated time. NOT REQUIRED needs a reason and owner.

Walk the selected workflow's prerequisite branches in order. On a required FAIL
or UNKNOWN, stop that branch, mark only transitive dependents NOT RUN, and
preserve and evaluate independent supplied-evidence rows. Give one task only to
the earliest required blocker and defer later blockers. Finish with first
blocker, owner task, both reviews, and READY FOR
NET-07: YES or NO. YES requires every required DEP PASS, justified NOT REQUIRED
rows, fresh evidence, owners, proof limits, private-value protection, and both
reviews PASS. Any failure, unknown, staleness, or unjustified omission makes
READY NO. Show the map and wait. Do not query, repair, or continue to NET-07.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/FOUNDATIONAL-SERVICES-DEPENDENCY-MAP.md`

### Pass Criteria

- One environment, outcome, connection, consumer set, and owner set are scoped.
- Address, name, and time dependencies remain separate and evidence-aware.
- Name purpose, query type/class, and proof limit prevent overclaims.
- Every required dependency is `PASS`; omissions are justified `NOT REQUIRED`.
- The first blocker has one owner task; later independent blockers are deferred.
- Both reviews pass; private values remain behind opaque references.
- Readiness authorizes no query, configuration, repair, or routing change.

### Stop Conditions

Stop the whole task for missing scope, owner, authority, or private boundary, or
an unsafe next step. For stale or cross-environment evidence, `FAIL`, or
`UNKNOWN`, stop only that branch, mark transitive dependents `NOT RUN`, and
preserve independent rows.

### Sources and Limits

- Solomon, Michael G., and David Kim. *Fundamentals of Communications and Networking*. 3rd ed., Jones & Bartlett Learning, 2022. Chapter 9 supports foundational service roles; it does not prescribe this AI dependency map.
- Droms, R. [Dynamic Host Configuration Protocol, RFC 2131](https://www.rfc-editor.org/info/rfc2131/), IETF, 1997; and Mrugalski, T., et al. [Dynamic Host Configuration Protocol for IPv6, RFC 9915 / STD 102](https://www.rfc-editor.org/info/rfc9915/), IETF, 2026. Status checked August 19, 2026. Used for address-configuration boundaries, not deployment defaults.
- Mockapetris, P. [Domain Names - Concepts and Facilities, RFC 1034](https://www.rfc-editor.org/info/rfc1034/) and [Domain Names - Implementation and Specification, RFC 1035](https://www.rfc-editor.org/info/rfc1035/), IETF, 1987. Status and updates checked August 19, 2026. Used for DNS foundations; current security and privacy behavior is outside this chapter.
- Mills, D., et al. [Network Time Protocol Version 4, RFC 5905](https://www.rfc-editor.org/info/rfc5905/), IETF, 2010; and Franke, D., et al. [Network Time Security for NTP, RFC 8915](https://www.rfc-editor.org/info/rfc8915/), IETF, 2020. Checked August 19, 2026. Used for time and authentication-state boundaries, not configuration.

### Next Step

Continue to **NET-07: Trace Routing, Gateways, NAT, Ports, and Egress** only
after both reviews pass and `READY FOR NET-07: YES`. Carry forward dependency
IDs, proof limits, owners, and opaque references, not private service values.


## 16. Trace Routing, Gateways, NAT, Ports, and Egress

> **Chapter handle:** `NET-07`.

### Objective

Map one approved outbound AI-workflow flow across owned network boundaries and
produce a reviewable egress allowlist without running a trace, scan, connection,
or configuration change.

### Required Inputs

- the accepted `NET-02` connection, `NET-03` topology, `NET-04` diagnosis card,
  `NET-05` address worksheet, and `NET-06` dependency map;
- one outcome, environment, `C-##` connection, source workload, destination
  service role, direction, and accountable owner;
- address family, controlled boundaries, supplied route or gateway evidence,
  return-path owner, and freshness rule;
- translation need, transport protocol, opaque port reference, application
  service, and current registry or protocol evidence;
- source and destination identity references, authentication and authorization
  authority, data class, minimum necessary data, retention, and expiry; and
- inspection authority, review owners, private-reference convention, and
  prohibited actions.

If the flow, owner, address family, boundary order, data class, identity,
authority, or evidence location is unclear, complete a blocked intake artifact
and stop. Do not browse, trace, ping, scan, connect, expose private values,
change a route or firewall, or create an allow rule to fill a gap.

### Why This Matters

A route can point toward a destination that an application cannot use. A later
policy can reject a gateway-accepted packet. Translation can preserve a flow
while hiding the original tuple. A registered port can lack a listener or serve
the wrong application.

These are different facts. A route is not end-to-end reachability. Translation
is not a firewall or an identity check. A reachable transport endpoint is not
proof of application identity, health, authentication, authorization, or safe
data handling. Network location alone must not create implicit trust.

This chapter records owned evidence. It does not prescribe NAT, enumerate
provider networks, choose a firewall, publish an address or
port, or authorize egress.

### Core Model

Use five stable row types:

- `BND-##` records one controlled, contracted, or required-review boundary;
- `RTE-##` records one forwarding decision at a controlled boundary;
- `XLT-##` records one translation-applicability decision;
- `FLW-##` records one transport endpoint and expected application service;
- `EGR-##` records one purpose-bound egress policy decision.

They answer different questions:

| Evidence layer | Bounded question | Maximum supported conclusion |
| --- | --- | --- |
| Route | Which route class and next controlled boundary apply to this destination class and address family? | The supplied evidence supports that forwarding decision at that boundary and time only |
| Translation | Is a tuple translated, in which direction, and under whose state? | The supplied record supports that translation state only, not security or stable identity |
| Transport | Which protocol and opaque port reference identify the intended transport endpoint? | Registry and endpoint evidence support a transport convention or observed endpoint only |
| Application service | Which service and service identity are expected beyond transport? | Current application evidence supports the checked service context only |
| Authentication | Which mechanism verifies the relevant workload or service identity? | The supplied result supports that authentication exchange only |
| Authorization | Which owner and policy permit this source, purpose, data, and action? | A current decision supports only the named scope and review period |
| Data handling | Which data class, minimum fields, encryption requirement, retention, and expiry apply? | The record supports the declared handling boundary, not legal compliance in every jurisdiction |

Keep route, reachability, listener, service identity, authentication,
authorization, and data-policy evidence separate. One successful layer never
upgrades another layer automatically.

Use `PASS`, `FAIL`, `UNKNOWN`, `NOT REQUIRED`, or `NOT RUN`. Only current
`OBSERVED` evidence that meets the declared proof rule establishes `PASS`.
`OWNER-STATED` records intended design; `RESEARCHED` can establish a public
registry convention; neither proves live behavior. `NOT REQUIRED` needs a
reason and owner. Provider-internal hops that the workflow neither controls nor
needs to inspect may be `NOT REQUIRED`; the provider ingress contract still
needs its own evidence.

### Ordered Method

**Step 1 - Freeze one outbound flow.** Record the outcome, environment,
`C-##`, source workload, destination service role, direction, address family,
data class, owners, authority, prohibited actions, and evaluation order. Do not
expand one approved flow into general network discovery.

**Step 2 - Declare controlled boundaries.** Create `BND-##` only where the
workflow controls, contracts with, or must verify a boundary. Record expected
and supplied evidence, class, checked time, opaque reference, owner, maximum
conclusion, unproven facts, and task or defer reason. Do not enumerate every
router inside an ISP, cloud fabric, or external provider.

**Step 3 - Record route decisions.** At each required boundary, create
`RTE-##` with source and destination classes, address family, route class,
selected next boundary or gateway reference, owner, checked time, and maximum
conclusion. Record connected, more-specific, default, policy-selected, or
provider-managed only when evidence supports the class. Track the return-path
owner separately; do not assume symmetry.

**Step 4 - Decide translation applicability.** Always create an `XLT-##`
decision row. When translation does not apply, use `NOT REQUIRED` with a reason
and owner. Otherwise keep pre- and post-translation values behind opaque
references and record direction, family, state owner, evidence, checked time,
expiry, return association, proof limit, unproven facts, and task. Do not infer
translation from private addressing or treat it as permission or protection.

**Step 5 - Separate transport from service.** Create `FLW-##` with transport,
opaque port, registry, listener, application, identity, authentication, and
authorization evidence. For each record the evidence class and checked time,
plus owner, state, maximum conclusion, unproven facts, and task or defer reason.
An IANA registration supports a convention; it does not prove a listener or the
software behind it. A transport exchange does not prove the expected
application, purpose, or permission.

**Step 6 - Build the egress decision.** Create `EGR-##` for one outbound
purpose. Link source and service identities; `BND/RTE/XLT/FLW` prerequisites;
data, authentication, authorization, encryption, retention, expiry, review,
and prohibited-use controls; and evidence, class, checked time, state, maximum
conclusion, unproven facts, and task. Default to blocked when a
decision-critical identity, purpose, policy, or data control is missing.

**Step 7 - Evaluate in declared order.** Stop only the dependent branch at the
first failed or unknown prerequisite. Mark its transitive dependents `NOT RUN`.
Continue evaluating independent supplied-evidence rows, retain their bounded
results, assign one owner task to the earliest required blocker, and defer
later blockers. Do not test or repair the path.

**Step 8 - Review readiness.** `READY FOR NET-08: YES` requires every required
`BND-##`, `RTE-##`, `XLT-##`, `FLW-##`, and `EGR-##` at `PASS`; justified
`NOT REQUIRED` rows; current evidence and owners; explicit return-path scope;
private values excluded; all required identity, authentication, authorization,
data, retention, expiry, and review controls complete; and both reviews
`PASS`. Any required `FAIL`, `UNKNOWN`, or `NOT RUN`, stale evidence,
unsupported conclusion, unresolved conflict, missing owner, or unjustified
omission makes readiness `NO`. Readiness permits continued design only.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
| --- | --- | --- |
| Quick | Classify one egress uncertainty. | Name its route, translation, transport, service, identity, or policy layer and the largest unknown. |
| Operator | Review one repeated outbound workflow. | Complete the boundary order, evidence chain, first blocker, and owner task. |
| Builder | Prepare a future implementation handoff. | Add exact opaque references, accepted evidence, proof limits, expiry, and test owner without writing policy. |
| Architect | Govern several environments or providers. | Separate controlled boundaries, provider contracts, identities, return paths, shared policy, data classes, and failure domains. |
| Lab | Rehearse without network activity. | Use fictional records, break one prerequisite, and prove dependent rows stop while independent evidence survives. |

### Fictional Example

> **Fictional scenario.** Harborlight Workshop reviews retrieval flow `C-03`
> from workload `S-02` to external service role `EXT-02`. The owner supplies
> sanitized route, contract, and identity records. No trace, scan, connection,
> or policy change is authorized.

| Row | Supplied state | Bounded result |
| --- | --- | --- |
| `BND-02` | Current observed contract-entry evidence identifies the controlled provider boundary | `PASS` for that boundary only; provider-internal hops and later path remain unproven |
| `RTE-01` | Current observed evidence selects `BND-02` for the destination class and address family | `PASS` for the local next-boundary decision after `BND-02`; return behavior remains unproven |
| `XLT-01` | Owner states `BND-02` performs translation, but no current state evidence is supplied | `UNKNOWN`; boundary owner must supply a fresh opaque translation-state proof |
| `FLW-01` | The intended transport convention has a current registry reference | `NOT RUN` for endpoint use because `XLT-01` blocks the dependent chain; the registry fact remains `RESEARCHED` only |
| `EGR-01` | Purpose and data class are owner-stated; current destination authentication evidence is independently absent | `NOT RUN` because `XLT-01` blocks this dependent decision; the separate evidence gap is preserved and deferred |

Evaluation order is `BND-02`, `RTE-01`, `XLT-01`, `FLW-01`, then `EGR-01`. The only next
task belongs to the `XLT-01` owner. `EGR-01` is `NOT RUN`; its independent
missing-authentication record remains visible and deferred.
`READY FOR NET-08` is `NO`. The record supports no claim that `EXT-02` is
reachable, authentic, authorized, healthy, or safe for data.

### Route-to-egress visual

```text
[S-02 / C-03]
       |
       v
[BND-02 controlled edge]: PASS, bounded
       |
       v
[RTE-01 next boundary] : PASS, bounded
       |
       v
[XLT-01 translation]   : UNKNOWN  ← first owner task
       |
       v
[FLW-01 endpoint]      : NOT RUN
       |
       v
[EGR-01 purpose/policy]: NOT RUN, gap preserved
```

Text equivalent: the controlled edge and local route decision have bounded evidence. The
required translation state is unknown, so dependent flow and policy decisions
are not run. A separate authentication gap is preserved for later review. Only the
first required blocker receives a task.

### Exercise or Test

Create `ROUTE-AND-EGRESS-ALLOWLIST.md` for one accepted `C-##`. Use supplied
sanitized evidence, include one translation-applicability decision row and one
decision-critical identity or authorization gap, stop the dependent chain,
preserve independent evidence, and assign only the earliest blocker task.

### Exact Agent Checkpoint Prompt

**Test state:** `PASS`.

```text
Act as my read-only route-and-egress recorder for one accepted outbound flow.
Use only the accepted NET-02 through NET-06 artifacts, approved workspace
state, official references I provide, and sanitized evidence I provide. Do not
browse, trace, ping, scan, connect, expose private values, edit routes or
firewalls, create an allow rule, restart anything, or perform an external
action.

Confirm the outcome, environment, C-##, source workload, destination service
role, direction, address family, data class, controlled boundary order,
return-path scope, row owners, Route-evidence and Egress-policy review owners,
evidence locations and freshness, authority, prohibited actions, retention,
expiry, review trigger, and opaque-reference
convention. Mark missing items UNKNOWN. If flow, owner, family, boundary order,
data class, identity, authority, or evidence location is unclear, still
complete the exact template as a blocked intake artifact, set affected rows
UNKNOWN or NOT RUN, set both reviews REPAIR, set READY FOR NET-08 NO, show the
artifact, and stop.

Create AI-GROWTH-WORKSPACE/artifacts/ROUTE-AND-EGRESS-ALLOWLIST.md from the
exact supplied template. If writing is unavailable, print it and do not claim
it was saved. Keep every real address, prefix, gateway, port, host name,
provider endpoint, account, token, certificate, and policy identifier behind
an opaque safe reference.

Create BND-## rows only for controlled, contracted, or required verification
boundaries. Record order, role, owner, expected and supplied evidence, class,
checked time, opaque reference, inspection boundary, state, maximum conclusion,
still-unproven facts, and task or defer reason. Do not enumerate
provider-internal hops outside the contract and inspection boundary.

Create RTE-## for every required forwarding decision. Record C-##, boundary,
source and destination classes, address family, route class, selected next
boundary or gateway reference, current evidence and class, checked time,
owner, return-path owner and evidence, prerequisites, state, maximum
conclusion, still-unproven facts, and task or defer reason. Do not assume path
symmetry or end-to-end reachability.

Always create an XLT-## translation-applicability decision. If translation does
not apply, use NOT REQUIRED with a reason and owner. Otherwise record direction,
family, opaque tuple references, type, state owner, evidence class and checked
time, expiry, return association, prerequisites, state, proof limit,
still-unproven facts, and task. Do not infer NAT or treat it as security.

Create FLW-## for the intended transport and application service. Record
transport protocol, opaque port reference, registry source and checked date,
source and destination identity references, listener, application, identity,
authentication, and authorization evidence with each class and checked time;
owner, prerequisites, state, maximum conclusion, unproven facts, and task. A
registry entry or reachable port is not proof of the expected application,
identity, health, security, or
permission.

Create EGR-## for the one outbound purpose. Link source workload identity,
destination service identity, BND/RTE/XLT/FLW prerequisites, data class, minimum
necessary fields, authentication mechanism, authorization owner and decision,
encryption requirement, retention, expiry, review trigger, prohibited uses,
evidence class and checked time, state, maximum conclusion, still-unproven
facts, blockers, and next owner task.

Use PASS, FAIL, UNKNOWN, NOT REQUIRED, or NOT RUN. Only current OBSERVED
evidence meeting the declared proof rule establishes PASS. NOT REQUIRED needs
a reason and owner. Evaluate rows in declared order. At the first failed or
unknown prerequisite, mark only transitive dependents NOT RUN. Preserve and
evaluate independent supplied-evidence rows. Assign one task to the earliest
required blocker and defer later blockers. Do not test or repair.

Finish with the first failed or unknown row, dependent NOT RUN rows,
independent evidence preserved, first owner task, deferred blockers,
Route-evidence review, Egress-policy review, and READY FOR NET-08 YES or NO.
YES requires every required BND, RTE, XLT, FLW, and EGR PASS; justified NOT REQUIRED
rows; current evidence and owners; explicit return-path scope; private values
excluded; identity, authentication, authorization, data, retention, expiry,
and review controls complete; and both reviews PASS. Any required FAIL,
UNKNOWN, or NOT RUN, stale evidence, unsupported conclusion, conflict, missing
owner, or unjustified omission makes READY NO. Show the artifact and wait. Do
not connect, implement policy, or continue to NET-08.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/ROUTE-AND-EGRESS-ALLOWLIST.md`

### Pass Criteria

- One approved flow, address family, boundary order, return-path scope, owner,
  evidence rule, and private-reference boundary are explicit.
- Route, translation, transport, application service, identity,
  authentication, authorization, and data handling remain separate.
- Every required row has current evidence, owner, checked time, state,
  maximum conclusion, unproven facts, and task or defer reason.
- Registry references never stand in for observed listeners or application
  identity, and translation never stands in for security or authorization.
- The first-blocker method preserves independent evidence, stops only
  dependents, assigns one task, and fails readiness closed.
- No live query, trace, scan, connection, disclosure, or configuration occurs.

### Stop Conditions

Stop for a missing flow, owner, address family, boundary order, evidence
location, return-path scope, data class, identity, authentication or
authorization authority, private-reference rule, or review owner; a stale or
conflicting required record; an unsupported external action; or a request to
expose private network values.

### Sources and Limits

- Solomon, Michael G., and David Kim. *Fundamentals of Communications and
  Networking*. 3rd ed., Jones & Bartlett Learning, 2022. Chapters 5-6 support
  bounded routing, NAT/PAT, transport, port, socket, and application-layer
  foundations; they do not define this artifact, current product behavior, or
  a secure AI egress policy.
- RFC 1812 describes IPv4 router requirements, including forwarding and default
  routes; RFC 8200 is the IPv6 base specification. Neither proves a deployment's
  current route, return path, policy, or provider-internal topology.
- RFC 2663 provides Informational NAT terminology. It is not a current
  implementation guarantee or a security-control specification.
- RFC 6335 / BCP 165, RFC 7605, RFC 9293 / STD 7, and the IANA Service Name and
  Transport Protocol Port Number Registry support current port and TCP
  boundaries. A registration does not prove a listener, application, identity,
  health state, or authorization.
- NIST SP 800-207 and SP 800-207A support resource-focused, identity-aware
  policy without implicit trust from network location. They do not prescribe a
  universal product, allowlist, or provider architecture.

### Next Step

Continue to **NET-08: Design Wireless and Remote Operator Access** only after
both reviews pass and `READY FOR NET-08: YES`. Carry forward the owned boundary
order, evidence limits, source and service identities, data controls, and
approved egress purpose, not a claim that the path was tested or implemented.


## 17. Design Wireless and Remote Operator Access

> **Chapter handle:** `NET-08`.

### Objective

Design the onsite wireless and remote private-access paths that let one approved
operator use one managed device for one named administrative action without
publishing an internal service or changing a network.

### Required Inputs

- the accepted `NET-02` connection, `NET-03` topology, `NET-05` address plan,
  `NET-06` dependency map, and `NET-07` route-and-egress record;
- one outcome, environment, operator identity reference, managed-device asset
  reference, target resource, allowed action, consequence, data class, and owner;
- required onsite and remote contexts, wireless purpose, opaque attachment and
  entrypoint references, expected segment, and destination classes;
- identity, device-enrollment, authentication, authorization, encryption,
  session, expiry, logging, update, and revocation authorities;
- supplied evidence, evidence class, checked time, freshness rule, recovery
  owner, and both review owners; and
- private-value convention, inspection boundary, and prohibited actions.

If global operator, device, resource, action, scope, inspection, or private-value
rules are unclear, complete a blocked intake artifact and stop. A gap limited to
one declared context blocks only that branch and its dependents. Do not scan,
associate, connect, expose, install, enroll, create, change, or configure
anything to fill a gap.

### Why This Matters

Wireless association is not identity, permission, coverage quality, or safe
application access. A strong signal does not prove usable capacity. An encrypted
tunnel protects a transport path under stated conditions; it does not prove the
device is managed, the operator is authorized, or every reachable resource is
allowed. A familiar home or office network does not create trust by location.

Remote entrypoints and administration tools are consequential access surfaces.
The plan must name who and what may enter, which resource and action are allowed,
how access expires or is revoked, what is logged, and how the path is disabled.
This chapter designs those controls. It does not select a universal product,
perform a radio survey, validate coverage, or authorize implementation.

### Core Model

Use three stable row types:

- `WLS-##` records one onsite wireless role and its attachment boundary;
- `ENT-##` records one local or remote private entry and enforcement point; and
- `OPA-##` records one context-specific operator, device, resource, and action
  decision for each required source context.

They answer different questions:

| Layer | Bounded question | Do not infer |
| --- | --- | --- |
| Wireless role | Which approved user and device roles may attach for which purpose and destination classes? | An SSID, credential, association, or signal does not prove identity, isolation, capacity, or application permission |
| Private entry | Which controlled entry pattern carries the session to a policy enforcement point? | A VPN, overlay, broker, or encrypted channel does not authorize every resource behind it |
| Operator action | Which operator and managed device may perform which action on which resource for how long? | Network reachability does not grant administrative authority or prove a safe device state |
| Recovery and disable | Who can revoke the user, device, session, and entrypoint, and what evidence proves the path can close? | A written recovery note does not prove revocation or recovery was tested |

Use `PASS`, `FAIL`, `UNKNOWN`, `NOT REQUIRED`, or `NOT RUN`. A row can pass a
design gate when current `OBSERVED` or accountable `OWNER-STATED` evidence meets
the declared design proof rule. `OWNER-STATED` never proves deployment or live
behavior. `RESEARCHED` supports a current capability or public standard only.
`NOT REQUIRED` needs a reason and owner. Keep design readiness separate from
implementation, connection, and security assurance.

### Ordered Method

**Step 1 - Freeze one administrative action.** Record the environment, outcome,
operator and managed-device references, target resource, exact action, data
class, consequence, owner, evidence boundary, and required onsite and remote
contexts. Do not turn one action into broad network administration.

**Step 2 - Classify each source context.** Name onsite managed wireless,
onsite guest wireless, wired recovery, remote untrusted attachment, or another
owned context. Treat a remote hotel, cellular, public, or home attachment as
untrusted input to the private-access decision. Do not inspect or make claims
about a third-party network. If wireless is not on a required path, create a
`WLS-##` decision at `NOT REQUIRED` with reason and owner.

**Step 3 - Design each required wireless role.** For `WLS-##`, record purpose,
user and device roles, opaque AP or SSID reference, intended segment or trust
role, allowed destination classes, authentication authority, security-mode
evidence, client or guest separation, coverage and capacity acceptance evidence,
owner, update owner, expiry, and disable path. A current product record supports capability;
only supplied configuration and acceptance evidence supports the deployed row.
Do not copy a legacy standard list into a recommendation.

**Step 4 - Choose the smallest private entry.** For `ENT-##`, record whether the
approved pattern is a local policy enforcement point, private overlay, remote
access VPN, identity-aware broker, or another reviewed pattern. Record opaque
entry and controller references, supported version, official evidence, patch
owner, control and data paths, encrypted transport requirement, failure mode,
allowed destination classes, and prohibited exposure. Do not publish raw model,
database, container-control, MCP-administration, or device-management services.

**Step 5 - Bind each context to identity, device, resource, and action.** Create
one `OPA-##` per required source context. Link its operator identity, explicit
device enrollment or posture evidence, context-specific `WLS/ENT` prerequisites,
target resource, action, consequence, authentication, multi-factor state for a
privileged action, authorization owner, session limit, data boundary, and proof
limit. A tunnel identity is not automatically a human identity or application
authorization.

**Step 6 - Design expiry, logging, recovery, and disable.** Record log owner and
retention, user and device revocation, session termination, entrypoint disable,
lost-device response, update responsibility, last-administrator protection,
review trigger, and a separately controlled recovery path. A recovery route
must not become an unlogged, permanent bypass. Mark test state honestly.

**Step 7 - Evaluate dependencies in order.** Declare the order. At the first
failed or unknown prerequisite, mark only transitive dependents `NOT RUN`.
Preserve independent supplied evidence, assign one task to the earliest required
blocker, and defer later blockers. Do not connect or repair the path.

**Step 8 - Review readiness.** `READY FOR NET-09: YES` requires every required
`WLS-##`, `ENT-##`, and context-specific `OPA-##` at design `PASS`; justified `NOT REQUIRED`
rows; current evidence, owners, and proof limits; no raw administrative service
exposure; complete identity, device, resource, authentication, authorization,
expiry, logging, recovery, and disable decisions; and both reviews `PASS`. Any
required `FAIL`, `UNKNOWN`, or `NOT RUN`, stale evidence, unsupported trust
claim, missing owner, unowned recovery path, or unjustified omission makes
readiness `NO`. Readiness permits continued design only.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
| --- | --- | --- |
| Quick | Classify one access uncertainty. | Name whether it belongs to wireless attachment, private entry, device identity, resource authorization, or recovery. |
| Operator | Review one repeated administrative action. | Complete the operator path, first blocker, expiry, log owner, and disable owner. |
| Builder | Prepare an implementation handoff. | Add official product references, version bounds, opaque configuration references, test owner, and rollback without changing anything. |
| Architect | Govern several sites or providers. | Separate user, device, entrypoint, resource, policy, control-plane, data-plane, recovery, and failure-domain ownership. |
| Lab | Rehearse safely. | Use fictional identities and endpoints, break revocation evidence, and prove dependent access remains `NOT RUN`. |

### Fictional Example

> **Fictional scenario.** Harborlight Workshop plans one approved maintenance
> action on resource `S-04` for operator `U-01` using managed device `A-07`.
> Onsite staff wireless and a remote private entry are required. Only sanitized
> records are supplied; no connection or configuration is authorized.

| Row | Supplied state | Bounded result |
| --- | --- | --- |
| `WLS-01` | Current observed configuration and acceptance records map managed device role `A-ROLE-02` to the staff wireless role and named destination classes | `PASS` for the declared onsite attachment design; live coverage, session health, and application access remain unproven |
| `OPA-01` | Onsite operator, managed-device posture, resource, action, consequence, multi-factor, and authorization records meet the design rule; prerequisite `WLS-01` passes | `PASS` for the onsite operator-action design; no live session or implementation is proven |
| `ENT-01` | Current product and controller records support the remote entry, but no current entrypoint revoke or disable proof is supplied | `UNKNOWN`; the entrypoint owner must provide one sanitized current record |
| `OPA-02` | Remote operator, device-posture, resource, action, consequence, multi-factor, and authorization evidence is preserved | `NOT RUN` because context-specific prerequisite `ENT-01` blocks only the remote branch |

Evaluation order is `WLS-01`, `OPA-01`, `ENT-01`, then `OPA-02`. The onsite
attachment and operator action pass independently. The only next task belongs
to the `ENT-01` entrypoint owner. `OPA-02` remains `NOT RUN`, so readiness is
`NO`.

### Operator-access visual

```text
[U-01 + A-07 + maintenance action]
             |
      +------+------+
      |             |
[WLS-01 onsite] [ENT-01 remote entry]
     PASS          UNKNOWN  (first task)
      |             |
      v             v
[OPA-01 onsite] [OPA-02 remote]
     PASS          NOT RUN
```

Text equivalent: current evidence supports the onsite wireless and operator
action designs. Missing remote entrypoint disable evidence blocks only the
remote action. Its independent evidence stays recorded, and the first blocker
alone receives a task.

### Exercise or Test

Create `WIRELESS-AND-PRIVATE-ACCESS-PLAN.md` for one approved operator action.
Include onsite wireless and private-entry decisions, one context-specific
operator-action row for each required context, recovery and disable paths, and
either current revocation evidence or a truthful blocker. Do not connect.

### Exact Agent Checkpoint Prompt

**Test state:** `PASS`, three routes.

```text
Act as my read-only wireless and private-access planner for one approved
administrative action. Use only the accepted NET-02, NET-03, and NET-05 through
NET-07 artifacts, approved workspace state, current official references I
provide, and sanitized evidence I provide. Do not browse, scan, associate,
connect, expose a service, install software, enroll a device, create an account,
change access, contact anyone, or configure wireless, firewall, overlay, VPN,
router, identity, or application settings.

Confirm the environment, outcome, operator identity reference, managed-device
asset reference, target resource, exact action, consequence, data class, owner, required
onsite and remote contexts, accepted NET-07 path, evidence locations and
freshness, identity/authentication/authorization authorities, review owners,
retention, expiry, inspection boundary, private-reference convention, update,
recovery, and disable owners, and prohibited actions. Mark missing items UNKNOWN.
If a global operator, managed-device state, resource, action, scope, inspection,
review owner, or private-value rule is unclear, or a privileged device is
unmanaged, complete the blocked template, set both reviews REPAIR, set READY FOR
NET-09 NO, show it, and stop. Treat a missing context, context authority,
supported-version or current evidence, update/recovery/disable owner, or
unreviewed public entrypoint as branch-local: mark that row UNKNOWN and only
its dependents NOT RUN while evaluating independent branches.

Create AI-GROWTH-WORKSPACE/artifacts/WIRELESS-AND-PRIVATE-ACCESS-PLAN.md from
the exact supplied template. If writing is unavailable, print it and do not
claim it was saved. Keep real SSIDs, APs, radio identifiers, addresses, ports,
host names, entrypoints, controllers, providers, accounts, users, devices,
certificates, keys, tokens, policies, and resource names behind opaque references.

Create WLS-## for each required onsite wireless role or one NOT REQUIRED
decision with reason and owner when wireless is absent. Record order, purpose,
user and device roles, opaque attachment reference, intended segment or trust
role, allowed destinations, authentication and security-mode evidence, coverage
and capacity evidence, guest or client separation, update owner, expiry, disable path,
prerequisites, evidence class and checked time, state, maximum conclusion,
still-unproven facts, and task or defer reason. Do not select a standard or infer
deployed security from an SSID, association, credential, or product capability.

Create ENT-## for each required local or remote private entry. Record pattern,
opaque entry and controller references, current supported version and official
evidence, patch owner, control and data paths, encryption requirement, operator
and device enrollment or posture evidence, allowed destination classes, failure
mode, logging, expiry, revocation and disable owners, prerequisites, evidence
class and checked time, state, maximum conclusion, still-unproven facts, and
task. Do not treat an encrypted tunnel as broad authorization or expose a raw
administrative service.

Create one OPA-## for each required source context. Record source context,
operator and device references, explicit device enrollment or posture evidence,
context-specific WLS/ENT prerequisites, target resource, action, consequence,
data class, authentication and multi-factor state, authorization decision and owner,
session limit, logging and retention, recovery path, expiry, review trigger,
state, maximum conclusion, unproven facts, and task. Record lost-device,
user-revocation, device-revocation, session-termination, entrypoint-disable,
last-administrator, and recovery controls without creating a permanent bypass.

Use PASS, FAIL, UNKNOWN, NOT REQUIRED, or NOT RUN. A design row may PASS when
current OBSERVED or accountable OWNER-STATED evidence meets its declared design
proof rule; label that conclusion as design-only. RESEARCHED supports current
capability only. NOT REQUIRED needs a reason and owner. Evaluate in declared
order. At the first failed or unknown prerequisite, mark only transitive
dependents NOT RUN, preserve independent supplied evidence, assign one task to
the earliest required blocker, and defer later blockers. Do not test or repair.

Finish with the first failed or unknown row, dependent NOT RUN rows, independent
evidence preserved, first owner task, deferred blockers, Wireless-design review,
Private-access review, and READY FOR NET-09 YES or NO. YES requires every
required WLS, ENT, and OPA at design PASS; justified NOT REQUIRED rows; current
evidence, owners, and proof limits; no raw administrative exposure; complete
identity, device, resource, context coverage, authentication, authorization, expiry, logging,
recovery, and disable decisions; and both reviews PASS. Any required FAIL,
UNKNOWN, or NOT RUN, stale evidence, unsupported trust claim, missing owner,
unowned recovery path, or omission makes READY NO. Show the artifact and wait.
Do not implement or continue to NET-09.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/WIRELESS-AND-PRIVATE-ACCESS-PLAN.md`

### Pass Criteria

- One operator, managed device, target resource, action, consequence, data class,
  owner, inspection boundary, and required contexts are explicit.
- Wireless attachment, private entry, operator identity, device state,
  authentication, authorization, and resource permission remain separate.
- Every required row has supported evidence, owner, checked time, state,
  maximum conclusion, unproven facts, and task or defer reason.
- No raw administrative service is published, and no local or familiar network
  creates implicit trust.
- Expiry, logging, user and device revocation, session termination, lost-device
  response, recovery, and entrypoint disable are owned and reviewable.
- Every required context has its own OPA decision and relevant prerequisites.
- First-blocker handling preserves independent evidence and fails readiness
  closed without a scan, connection, installation, enrollment, or change.

### Stop Conditions

Stop the whole artifact for a missing global operator, managed device, resource,
action, scope, inspection boundary, review owner, or private-reference rule; an
unmanaged privileged device; a credential request; or any requested change.
Fail only the affected branch for a missing context, context authority, evidence,
recovery or disable owner, supported-version record, current evidence, or an
unreviewed public entrypoint, then mark its dependents `NOT RUN`.

### Sources and Limits

- Solomon, Michael G., and David Kim. *Fundamentals of Communications and
  Networking*. 3rd ed., Jones & Bartlett Learning, 2022. Chapters 10-11 support
  wireless purpose, coverage, capacity, security, remote, WAN, and scenario
  foundations; they do not define this artifact, current wireless standards,
  private-overlay behavior, or secure product configuration.
- NIST SP 800-153 supports a lifecycle approach to WLAN component configuration,
  evaluation, maintenance, and monitoring. Published in 2012, it does not prove
  current product modes, certifications, defaults, or deployment security.
- NIST SP 800-207 supports resource-focused access with no implicit trust from
  network location and distinct user, device, authentication, and authorization
  decisions. It does not prescribe one VPN, overlay, broker, or product.
- CISA's TIC 3.0 Remote User Use Case v2.2 supports current remote-user design
  considerations for secure protocols, multi-factor authentication, endpoint
  compliance, authorized services, telemetry, and revocation. Its federal scope
  is guidance context, not a universal compliance requirement.
- The NSA and CISA remote-access VPN guidance supports treating exposed gateways
  as high-value entrypoints with current updates, strong authentication, and a
  reduced attack surface. Product selection and configuration still require
  current vendor evidence and an authorized implementation review.

### Next Step

Continue to **NET-09: Separate Trust Zones Without Breaking the Workflow** only
after both reviews pass and `READY FOR NET-09: YES`. Carry forward opaque path,
identity, device, entry, resource, action, recovery, and disable decisions, not
a claim that wireless coverage, remote access, or revocation was implemented.


## 18. Separate Trust Zones Without Breaking the Workflow

> **Chapter handle:** `NET-09`.

### Objective

Design the smallest network and workload boundaries for an AI workflow,
then prove each necessary crossing has an owned control decision
without treating a VLAN, subnet, location, or device as trusted by default.

### Required Inputs

- the accepted `NET-01` inventory and requirements, `NET-02` traffic path,
  `NET-03` topology and flow, `NET-05` address plan, `NET-06` dependency map,
  `NET-07` route and egress record, and `NET-08` access plan;
- workflow outcome, environment, architecture version, scope owner,
  consequence, availability need, and design-only authority;
- opaque references for users, devices, workloads, resources, data classes,
  source contexts, destinations, actions, and evidence;
- current supported boundary capabilities at the network, host, workload,
  application, database, or virtualization layer, with checked dates and owners;
- required forward, return, management, observability, recovery, update,
  and failover path, including external dependencies;
- identity, device-posture, workload-identity, authentication, authorization,
  policy, telemetry, failure-behavior, expiry, and disable evidence; and
- Workflow-continuity and Boundary-control review owners.

If the workflow, architecture, scope, owner, design authority,
privacy boundary, or opaque-reference convention is unclear, complete a
blocked artifact and stop. Do not discover devices, scan, connect, capture
traffic, assign VLANs, change ports, routes, firewall rules, host policy, cloud
policy, identities, or services to fill a gap.

### Why This Matters

A flat environment is easy to start and hard to reason about. A
device, runtime, retrieval store, management plane, and external provider may
become mutually reachable when the workflow needs narrow exchanges. One
compromised component may
have more visibility or movement than the job requires.

Segmentation can also break the system it is meant to protect. DNS, time,
identity, updates, logs, backups, health checks, return traffic, and recovery
access often cross the same boundaries as the main request. A diagram that
blocks the obvious application flow but omits these dependencies is not ready.
Availability and emergency recovery behavior must be chosen, not assumed.

A VLAN can define supported Layer 2 attachment and broadcast scope. It does not
prove identity, authorize an action, encrypt data, govern inter-zone routing,
enforce an application decision, or contain every path. Zero-trust guidance
shifts the decision toward the resource, subject, device, workload, request, and
policy. Modern microsegmentation may use
network controls, but it may also place enforcement in hosts, workloads,
applications, databases, operating systems, or virtualization platforms.

### Core Model

Use three stable row types:

- `ZON-##` defines one design grouping, boundary purpose, and proof limit;
- `FLW-##` defines one required or explicitly prohibited cross-zone workflow;
  and
- `CTL-##` defines one proposed permit, deny, or unresolved enforcement
  decision for a flow or unmapped class.

| Record | Bounded question | Must not become |
| --- | --- | --- |
| Zone | Which resources share a purpose and boundary, and on what current evidence? | A claim that members are trusted, identical, deployed, or isolated |
| Flow | Which exact subject or workload needs which action on which resource, with what return and dependency paths? | Broad reachability, an undocumented wildcard, or a live connection test |
| Control | Where can the decision be enforced and observed with supported policy evidence? | A deployable rule, product guarantee, or claim that a VLAN equals zero trust |

Use `PASS`, `FAIL`, `UNKNOWN`, `NOT REQUIRED`, or `NOT RUN`. A control decision
is `PERMIT`, `DENY`, or `UNKNOWN`; record every applicable condition in the
separate conditions field. It is not a live outcome.
`OWNER-STATED` design evidence does not prove current configuration.
`OBSERVED` requires supplied inspectable evidence. `RESEARCHED` supports a
capability, not its deployment. A zone name never proves trust.

### Ordered Method

**Step 1 - Freeze the design contract.** Record the workflow, environment,
architecture version, scope, owners, consequences, availability target,
privacy, safe-reference convention, evidence freshness, review owners, and
exact design authority. State that drafting, implementation, testing, and
approval are separate permissions.

**Step 2 - Define zones around resources and consequences.** Create `ZON-##`
for groups that need a distinct boundary because of resource purpose, data
sensitivity, exposure, administration, failure impact, or policy. Record
candidate Layer 2, Layer 3, host, workload, application, database, or
virtualization boundaries separately. Do not group components only because
they are nearby or owned by the same person.

**Step 3 - Enumerate workflow crossings.** Convert accepted traffic paths and
dependencies into atomic `FLW-##` rows. Name one source context, subject or
workload identity, destination resource, action, direction, return path,
protocol or service reference, data class, consequence, and owner. Include
management, identity, DNS, time, telemetry, update, backup, recovery, and
failover paths when the workflow requires them. Unmapped required traffic is a
blocker, not an invitation to permit everything.

**Step 4 - Bind each flow to one decision.** Create `CTL-##` for every required
flow and each declared prohibited or unmapped class. Use `PERMIT` only for the
minimum supported subject, resource, and action, with every prerequisite and
condition recorded separately. Use `DENY` for an explicitly reviewed
unnecessary class and `UNKNOWN` when whether to permit or deny is unsupported.
Record the policy decision source, proposed enforcement point, telemetry,
owner, expiry, and maximum conclusion.

**Step 5 - Select the smallest supported enforcement layer.** A switch or VLAN
may be a useful broadcast boundary. A routed policy point may control zone
crossings. A host, workload, application, database, or virtualization control
may be needed for resource-specific action. Choose from current supplied
capability evidence and record limits. Do not label one control complete zero
trust or invent product support.

**Step 6 - Preserve operations and recovery.** For every control, state the
expected behavior when policy, identity, telemetry, or the enforcement point is
unavailable. Record management access, logging, update, backup, restoration,
break-glass governance, alternate path, disable owner, and recovery test
authority. `FAIL CLOSED` is not automatically correct for every availability
need, and `FAIL OPEN` is not automatically acceptable. The accountable owner
must approve the trade-off before implementation.

**Step 7 - Prepare a reversible change handoff.** Describe the proposed delta
without live values. Link prerequisites, maintenance owner, test evidence,
success signal, failure signal, rollback owner, and independent approval.
Preserve current paths until a separately authorized implementation validates
the replacement. This chapter never applies the change.

**Step 8 - Review readiness.** `READY FOR NET-10: YES` requires every in-scope
zone current and owned; every required or prohibited flow atomic and traced;
every flow bound to a supported `CTL-##`; no broad, conflicting, expired, or
unmapped crossing; all management, observability, dependency, recovery, and
failover paths resolved; one current test and rollback handoff; and both
reviews `PASS`. A global intake defect stops all rows. A flow-local defect marks
only dependent controls `NOT RUN` while independent evidence continues. Any
consequential `UNKNOWN`, `FAIL`, or `NOT RUN` makes readiness `NO`.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
| --- | --- | --- |
| Quick | You need to challenge one broad trust assumption. | Name the resource, required action, current boundary, maximum conclusion, and owner. |
| Operator | You need a safe design review before a network change. | Map zones, required flows, enforcement candidates, operations paths, reviews, and stop conditions. |
| Builder | You need a reversible implementation handoff. | Add current capability evidence, atomic control decision, test signals, rollback, maintenance window, and approval owner. |
| Architect | You govern local, cloud, and hybrid enforcement. | Reconcile network, host, workload, application, data, identity, telemetry, failure, and recovery boundaries. |
| Lab | You need proof without touching a live network. | Use fictional opaque IDs; inject one missing dependency and verify only its branch stops. |

### Fictional Example

> **Fictional scenario.** Harborlight Workshop supplies a design for a
> managed operator context, an agent runtime, a retrieval resource, and an
> approved provider egress. Management and observability evidence remain inside
> `ZON-02`; no separate crossing is required. Authority covers only the design
> record. No VLAN number, address, port, rule, product, scan,
> configuration, connection, isolation test, or deployment is supplied.

| Row | Supplied design evidence | Bounded result |
| --- | --- | --- |
| `ZON-01` | Managed operator context; operator action is behind `OPA-01` | `PASS`; a source context, not a declaration that the device or user is trusted |
| `ZON-02` | Agent runtime and its orchestration resource | `PASS`; proposed workload zone only; current attachment and isolation remain unproven |
| `ZON-03` | Retrieval resource with a distinct data owner | `PASS`; proposed data boundary only |
| `ZON-04` | External provider behind the accepted route record | `PASS`; external boundary, not trusted |
| `FLW-01` | `ZON-01` operator requests one draft action from the `ZON-02` orchestration resource | `PASS`; identity, posture, resource, action, return path, consequence, and owner are supplied |
| `CTL-01` | `PERMIT` for `FLW-01` at a supplied application policy point; identity and posture conditions are separate | `PASS` as design intent; it proves no deployed policy or successful request |
| `FLW-02` | `ZON-02` retrieval query to `ZON-03`; workload identity evidence is missing | `UNKNOWN`; first blocker is the workload-identity evidence owner |
| `CTL-02` | Enforcement decision for `FLW-02` depends on the missing identity evidence | `NOT RUN`; no broad network permit is substituted |
| `FLW-03` | `ZON-02` approved provider request to `ZON-04` behind the accepted route record | `PASS`; independent evidence is preserved while `FLW-02` remains blocked |
| `CTL-03` | `PERMIT` for `FLW-03` at the accepted egress policy point; provider-purpose and route conditions are separate | `PASS` as design intent; conditions, owner, telemetry, and expiry are current |

Evaluation stops only the `FLW-02 -> CTL-02` branch. The only next-owner task
is to supply current workload-identity evidence. Enforcement-capability, rule,
test, and rollback questions remain deferred. Both reviews are
`REPAIR`, and `READY FOR NET-10` is `NO`. Nothing is configured.

### Zone-to-control visual

```text
[ZON-01 operator] -- FLW-01 -- [CTL-01] -- [ZON-02 runtime]
                                             |          \
                                      FLW-02 |           \ FLW-03
                                             v            v
                                     [CTL-02 NOT RUN] [CTL-03 PASS]
                                             |            |
                                             v            v
                                    [ZON-03 retrieval] [ZON-04 provider]
```

Text equivalent: the operator-to-runtime branch has a supported permit with
named conditions, the runtime-to-retrieval branch stops at missing workload
identity evidence, and the independent provider branch has its own supported
control decision. No line represents deployed reachability.

### Exercise or Test

Create `TRUST-ZONE-AND-CONTROL-MATRIX.md` for one fictional AI workflow. Run one
complete case and one case with a missing dependency or enforcement capability.
Prove the complete case reaches reviewed design readiness, the local defect
stops only dependent rows, and neither case scans or changes a network.

### Exact Agent Checkpoint Prompt

**Test state:** `PASSED INDEPENDENT QA`.

```text
Act as my read-only trust-zone and control-matrix recorder. Use only accepted
NET-01 through NET-08 artifacts, approved workspace state, current official
capability evidence I provide, and sanitized evidence I provide. Do not browse,
discover, scan, connect, capture traffic, assign addresses or VLANs, configure,
test, isolate, block, permit, deploy, or change any device, host, route, policy,
identity, cloud resource, or service.

Confirm the exact workflow, environment, architecture version, scope owner,
consequence, availability need, design-only authority, safe-reference rule,
privacy boundary, evidence freshness, required source contexts, subjects,
devices, workloads, resources, actions, data classes, dependencies, management,
observability, recovery, failover, and both review owners. Mark missing items
UNKNOWN. If workflow, architecture, scope, owner, authority, privacy, or safe
references are unclear, complete the exact template as a blocked artifact, set
both reviews REPAIR, set READY FOR NET-10 NO, show it, and stop.

Create AI-GROWTH-WORKSPACE/artifacts/TRUST-ZONE-AND-CONTROL-MATRIX.md from the
exact supplied template. If writing is unavailable, print it and do not claim
it was saved. Use opaque references; do not expose real addresses, VLAN IDs,
ports, identities, secrets, rule syntax, or internal hostnames.

Create ZON-## for each required design grouping. Record purpose, members by
opaque reference, membership basis, data sensitivity, exposure, candidate
Layer 2 broadcast scope, routing boundary, host/workload/application/database/
virtualization boundary, entry and exit enforcement references, dependencies,
management, observability, recovery, evidence, checked date, owner, expiry,
prerequisites, state, maximum conclusion, and task. Never call a zone trusted or
claim current membership, isolation, routing, or enforcement without evidence.

Create atomic FLW-## for every required or explicitly prohibited crossing.
Record source zone and context, subject or workload identity, destination zone,
resource and action, direction and return path, protocol or service safe
reference, data class, identity and posture evidence, dependencies, consequence,
required or prohibited basis, accepted NET references, owner, prerequisites,
state, maximum conclusion, and task. Include required identity, DNS, time,
telemetry, update, backup, management, recovery, and failover paths. Do not use
an undocumented wildcard or infer that same-zone traffic is authorized.

Create CTL-## for every FLW-## and each declared unmapped class. Record PERMIT,
DENY, or UNKNOWN as the decision and record all conditions separately; source
and destination; proposed
network, host, workload, application, database, or virtualization enforcement
layer and policy point; policy and capability evidence; authentication,
authorization, identity and posture conditions; telemetry; expiry; behavior on
dependency or control failure; bypass handling; management and recovery path;
implementation, test, rollback, and approval references; owner; prerequisites;
state; maximum conclusion; and task. Do not invent product support or turn a
design intent into a deployable rule or live result.

Use PASS, FAIL, UNKNOWN, NOT REQUIRED, or NOT RUN. Evaluate in declared order.
A global intake blocker stops all dependent authoring. At the first flow-local
failed or unknown prerequisite, mark only dependent rows NOT RUN, preserve
independent evidence, assign one task to the earliest blocker, and defer later
blockers. Finish with the first blocker, dependent rows, preserved evidence,
one next owner task, deferred items, Workflow-continuity review,
Boundary-control review, and READY FOR NET-10 YES or NO.

READY YES requires every zone current and owned; every required or prohibited
flow atomic and traced; each flow bound to a supported CTL; no broad,
conflicting, expired, bypassed, or unmapped crossing; required management,
observability, dependency, recovery, and failover paths resolved; a current
test and rollback handoff; and both reviews PASS. Show the artifact and wait.
Do not implement, approve, test, or continue to NET-10.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/TRUST-ZONE-AND-CONTROL-MATRIX.md`

### Pass Criteria

- Every zone has a purpose, opaque membership basis, boundary layers, current
  evidence, owner, expiry, dependencies, and maximum conclusion.
- Every necessary or prohibited crossing is atomic and includes its return,
  identity, policy, consequence, management, and recovery context.
- Each flow has one supported control decision; VLAN or location is never
  treated as identity, authorization, encryption, or complete containment.
- Unmapped or unsupported movement remains blocked in the design instead of
  receiving a broad permit.
- Operations, observability, update, backup, recovery, failover, test, and
  rollback paths are reviewed without making a live change.
- Global and flow-local blockers produce deterministic states, one earliest
  owner task, two reviews, and correct readiness.

### Stop Conditions

Stop for missing workflow, architecture, scope, owner, design authority,
privacy, safe-reference rule, zone evidence, required flow, identity or posture
evidence, policy or enforcement capability, dependency, management path,
telemetry, failure behavior, recovery path, expiry, review owner, test handoff,
rollback owner, or approval boundary. Stop on a wildcard permit, an unsupported
claim of isolation or zero trust, a request for real values, or any live change.

### Sources and Limits

- Solomon, Michael G., and David Kim. *Fundamentals of Communications and
  Networking*. 3rd ed., Jones & Bartlett Learning, 2022. Selected Chapters 7,
  13, and 14 support VLAN, resilience, containment, recovery, segmentation, and
  layered-control foundations; they do not prove current support or prescribe
  this artifact.
- NIST. *Zero Trust Architecture*, SP 800-207, 2020. Supports resource-focused,
  explicit access decisions and the limit on location-based trust; it does not
  make a zone, VLAN, product, or worksheet zero trust.
- CISA. *Microsegmentation in Zero Trust, Part One: Introduction and Planning*,
  2025. Supports planning across network and workflow-aware enforcement layers.
  Its primary audience is federal, and it does not prove buyer capability.
- NIST. *Guide to a Secure Enterprise Network Landscape*, SP 800-215, 2022,
  and *Implementing a Zero Trust Architecture*, SP 1800-35, 2025. Support
  modern network-security and implementation context; reference designs and
  examples require environment-specific validation.

### Next Step

Continue to **NET-10: Budget Capacity, Latency, Reliability, and Failover** only
after both reviews pass and `READY FOR NET-10: YES`. Carry forward zone and
flow IDs, supported control decisions, dependency and recovery paths, owners,
expiry, and proof limits, not an assumption that any boundary is deployed.


## 19. Budget Capacity, Latency, Reliability, and Failover

> **Chapter handle:** `NET-10`.

### Objective

Turn one critical AI workflow into a reviewable performance and
failover decision without inventing targets, blaming the network for total
response time, assuming redundant paths are independent, or running a live
test. Produce evidence and owner tasks for later observability.

### Required Inputs

- accepted `NET-01` through `NET-09` requirements, traffic, topology,
  dependency, route, access, zone, flow, control, and recovery artifacts;
- one safe workflow reference, consequence, criticality, start and end
  boundary, direction, path references, and accountable owner;
- declared workload, concurrency, payload, burst, growth, degraded conditions,
  exclusions, and public/private boundary;
- approved targets with source and expiry, or `UNKNOWN`; sanitized observations
  with units, windows, sample counts, methods, sources, clock basis, freshness,
  and variability;
- measurement permission, safety, privacy, retention, protected volume, cost,
  and time limits, plus explicit prohibitions on probes, load, scans, captures,
  route changes, and failover;
- named failures, detection evidence, alternates, shared dependencies, state
  behavior, degraded limits, recovery, failback, rollback, tests, and authority;
  and
- Performance-integrity and Continuity review owners.

If the shared contract lacks a safe workflow reference, consequence,
criticality, measurement boundary, permission, safety limit, data rule,
protected budget, or accountable owner, complete a blocked artifact and stop. A missing observation,
target, capacity owner, latency segment, alternate-path fact, or recovery fact
for one row is point-local: mark that row `UNKNOWN`, stop its dependents, and
preserve independent evidence. Do not generate traffic or change a system.

### Why This Matters

Fast is not a measurement. Response time needs a declared boundary, direction,
workload, method, unit, window, and source. An average can hide variation and
failure. A current baseline describes one observed condition, not a promise.

Capacity is bounded too. Link rate, a vendor limit, or an allocation is not
delivered throughput. Demand can move among transit, queueing, retrieval,
storage, model work, provider limits, and return handling. Headroom is an owner
policy tied to consequence and growth, not a universal percentage.

Redundancy is a design fact. Paths may share power, DNS, identity, egress,
provider, storage, or control state. Failover needs detection, a usable
alternate under degraded load, known state behavior, owned recovery and
failback, and a safe current test.

### Core Model

Use five stable row types:

- `SVC-##` freezes one workflow measurement contract;
- `BSL-##` records one workload-bound observation;
- `CAP-##` decides one capacity or headroom question;
- `LAT-##` bounds one observed or unmeasured delay segment; and
- `FOV-##` decides one failure, alternate, recovery, and rollback path.

| Record | Bounded question | Must not become |
| --- | --- | --- |
| Service | What workflow, boundary, consequence, workload, target source, and evidence permission apply? | A vague request to make the system fast |
| Baseline | What was observed, where, when, how, and under which workload? | A target, guarantee, cause claim, or permanent normal |
| Capacity | What demand and service evidence support the owner headroom decision? | A copied threshold or claim that link rate equals throughput |
| Latency | Which time boundary is observed, and which segments remain unmeasured? | A claim that end-to-end duration is network delay or root cause |
| Failover | Which failure, alternate, shared dependencies, degraded limits, and recovery evidence apply? | A claim that duplicate components prove availability |

Use `PASS`, `FAIL`, `UNKNOWN`, `NOT REQUIRED`, or `NOT RUN`. `PASS` means the
record supports its maximum conclusion, not that performance is good.
`OBSERVED` needs inspectable evidence. `OWNER-STATED` preserves a target or
limit without proving it. `RESEARCHED` supports a public definition, not a
buyer result, capability, or failure outcome.

### Ordered Method

**Step 1 - Freeze the contract.** Record the workflow, use, consequence,
criticality, accountable owner, boundaries, direction, path and zone references,
workload, exclusions, measurement permission, data handling, budgets, target
authority, expiry, and prohibited actions. Separate plan-writing permission from authority to
probe, load, change, fail over, fail back, recover, purchase, or deploy.

**Step 2 - Create atomic service rows.** Make one `SVC-##` per critical workflow
step or separately governed branch. Name criticality, requiredness, start, end,
direction, dependencies, workload, required metric classes, target source,
evidence permission, owner, prerequisites, state, and maximum conclusion. Do
not merge interactive and batch work or local and provider paths when their
consequences differ.

**Step 3 - Build current baselines.** Create `BSL-##` only from supplied
observations. Record metric, unit, direction, workload, concurrency, payload,
burst, window, sample count, statistic, result safe reference, method, source,
clock basis, freshness, variability, and unknowns. If only a total duration is
observed, say so. Do not manufacture a percentile from a single value or call a
target a baseline.

**Step 4 - Budget capacity.** Create `CAP-##` for each consequential resource or
segment. Separate owner-supplied ceiling from observed service rate. Record
demand, concurrency, payload, burst, growth, degraded condition, reserved
headroom rule, constraint, consequence, evidence task, owner, prerequisites,
state, and maximum conclusion. Missing ceiling or demand evidence stays
`UNKNOWN`.

**Step 5 - Bound latency.** Create `LAT-##` for each needed boundary. Classify it
as `OBSERVED SEGMENT`, `OBSERVED END-TO-END`, or `UNMEASURED`. Record direction,
workload, window, statistic, result reference, method, clock basis, included and
excluded time, unknowns, prohibited cause claim, owner, and task. One-way delay
needs appropriate endpoint timing; a round-trip or application duration cannot
silently substitute for it. A required unmeasured segment is `UNKNOWN` and
blocks readiness; an unrequired segment may remain explicitly excluded from a
bounded end-to-end conclusion.

**Step 6 - Decide failover evidence.** Create `FOV-##` per failure condition.
Record detection evidence, affected path, alternate, shared dependencies,
state, data, and session behavior, degraded capacity and latency limits,
activation, recovery, failback, rollback, test evidence, safety boundary,
owner, authority, prerequisites, state, and maximum conclusion. A design row
without a safe current test remains a plan, not proof of failover.

**Step 7 - Stop at the first blocker.** A shared-contract blocker stops all
authoring. A row-local blocker marks only dependent rows `NOT RUN`. Preserve
independent observations, assign one task to the earliest current owner, and
defer later blockers with reasons. An unresolved consequential row makes both
reviews `REPAIR` and readiness `NO`.

**Step 8 - Review readiness.** `READY FOR NET-11: YES` requires every critical
service complete; required baselines current and workload-bound; required
capacity, latency, and failover rows supported; no invented target, result,
independence, cause, availability, recovery, or continuity claim; and both
reviews `PASS`.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
| --- | --- | --- |
| Quick | One response path feels slow. | Freeze one boundary, workload, observation source, unknown, and owner task. |
| Operator | A buyer needs a usable baseline. | Complete service, baseline, capacity, and latency rows without causal guessing. |
| Builder | A workload may grow or degrade. | Add concurrency, bursts, headroom policy, constraints, and safe evidence tasks. |
| Architect | The path has alternates or shared infrastructure. | Reconcile failure domains, state, degraded limits, recovery, failback, and rollback. |
| Lab | You need branch-local blocker proof. | Use fictional evidence; block one alternate while preserving an independent baseline. |

### Fictional Example

> **Fictional scenario.** Harborlight Workshop supplies a sanitized `SVC-01`
> support-retrieval path, accepted path and zone references, one owner-approved
> workload class, 60 fictional completions during a 200-second observation
> window at concurrency three, a target and headroom policy with expiry, an
> alternate retrieval design, and plan-writing authority only. `SVC-01` is
> critical and requires end-to-end completion time, observed service rate, and
> a continuity decision. Retrieval, provider, and queue segment timing is not
> required for this decision and is explicitly excluded. No probe, load, route
> change, failover, or recovery is allowed.

| Row | Supplied or proposed state | Bounded result |
| --- | --- | --- |
| `SVC-01` | Critical support-retrieval workflow; required measures are end-to-end completion and service rate; a continuity decision is required; internal timing segments are not required | `PASS` for contract completeness; unrequired segments remain explicit exclusions |
| `BSL-01` | End-to-end completion p95 is 2.6 seconds for the supplied fictional window; same-host start and end clock; source `OBS-01` | `PASS` for that workload and window; no segment or cause claim |
| `BSL-02` | Source `OBS-02` records 60 completed requests in the supplied 200-second window; count divided by elapsed window gives 18 completed requests per minute; same clock and workload as `BSL-01` | `PASS` for observed service rate in that window; no ceiling or growth claim |
| `CAP-01` | `BSL-02` observes 18 completed requests per minute; owner ceiling `LIM-01` is 24; owner policy `POL-01` requires at least 20 percent of the ceiling unused, and 25 percent is unused | `PASS` for the declared workload and current window; no growth or universal threshold claim |
| `LAT-01` | User-simulator start to response receipt is `OBSERVED END-TO-END`; the `SVC-01` contract marks retrieval, provider, and queue segments unrequired and excluded | `PASS` as a bounded total; segment attribution remains prohibited |
| `FOV-01` | Alternate retrieval path exists, but independence from the primary upstream and degraded-load evidence are not supplied | `UNKNOWN`; dependent degraded-capacity and recovery rows are `NOT RUN` |

The first owner task is for the Continuity owner to supply a safe dependency
map for the alternate. `BSL-01`, `BSL-02`, `CAP-01`, and `LAT-01` remain
preserved. Later failover-test and rollback questions are deferred. Both
reviews are `REPAIR` and `READY FOR NET-11` is `NO`.

### Evidence-flow visual

```text
[SVC-## measurement contract]
            |
         [BSL-##]
        /        \
   [CAP-##]    [LAT-##]
        \        /
         [FOV-##]
            |
 [two reviews + READY NET-11]

Row-local blocker: dependent rows NOT RUN; independent evidence continues.
```

Text equivalent: freeze the service contract, bind a current observation to its
workload, decide capacity and latency within their evidence limits, then decide
failover and recovery. A local blocker stops only its dependents.

### Exercise or Test

Create `PERFORMANCE-BASELINE-AND-FAILOVER-DECISION.md` for two fictional service
branches. Give one complete current baseline. Withhold alternate-path
independence for the second. Prove the complete baseline remains evaluated,
only dependent failover rows stop, one earliest owner task is assigned, later
blockers defer, both reviews become `REPAIR`, and readiness is `NO`.

### Exact Agent Checkpoint Prompt

**Test state:** `PASSED INDEPENDENT QA`.

```text
Act as my read-only AI-workflow performance and failover recorder. Use only
accepted NET-01 through NET-09 artifacts, approved workspace state, current
official metric guidance I provide, and sanitized evidence I provide. Do not
probe, scan, capture packets, generate load, browse private systems, change a
route or policy, trigger failover or failback, recover a service, purchase,
deploy, or claim availability.

Confirm the safe workflow reference, use, consequence, criticality,
accountable workflow owner, start and end, direction, path and zone references,
workload classes and exclusions,
measurement permission and safety limits, data handling, protected volume,
cost and time budgets, target source and expiry, change and failover authority,
and both review owners. Mark missing items UNKNOWN. If a shared contract field
is unclear, complete the exact template as a blocked artifact, set both reviews
REPAIR, set READY FOR NET-11 NO, show it, and stop. A missing fact or owner for
one SVC, BSL, CAP, LAT, or FOV row is point-local, not a global stop.

Create AI-GROWTH-WORKSPACE/artifacts/PERFORMANCE-BASELINE-AND-FAILOVER-DECISION.md
from the exact supplied template. If writing is unavailable, print it and do
not claim it was saved. Keep private values behind opaque safe references.

Create atomic SVC-## rows for each critical workflow step or governed branch.
Record consequence, criticality, requiredness, start, end, direction, accepted
path and zone references, workload, exclusions, metric classes, target source
and expiry, evidence permission, owner, prerequisites, state, maximum
conclusion, and task.

Create BSL-## only from supplied observations. Record metric, unit, direction,
workload, concurrency, payload, burst, window, sample count, statistic, result
safe reference, method, source, clock basis, freshness, variability, unknowns,
owner, prerequisites, state, maximum conclusion, and task. Do not turn a target,
single value, vendor limit, or link rate into an observed baseline.

Create CAP-## for each required resource or segment. Separate owner-supplied
ceiling from observed service rate. Record demand, concurrency, payload, burst,
headroom rule, growth and degraded conditions, constraint, consequence, owner,
next evidence task, prerequisites, state, and maximum conclusion.

Create LAT-## for each required timing boundary. Use OBSERVED SEGMENT, OBSERVED
END-TO-END, or UNMEASURED. Record direction, workload, window, statistic,
result, method, source, clock basis, included and excluded time, unknowns,
prohibited cause claim, owner, prerequisites, state, conclusion, and task. Do
not label total application duration as network or one-way delay. Mark a
required unmeasured segment UNKNOWN and readiness NO. If the contract does not
require that segment, preserve it as an explicit exclusion without attributing
the bounded end-to-end result to a component.

Create FOV-## for each failure condition. Record detection evidence, affected
path, alternate, shared dependencies, state, data, session behavior, degraded
capacity and latency limits, activation, recovery, failback, rollback, test
evidence, safety boundary, owner, authority, prerequisites, state, maximum
conclusion, and task. A redundant design is not proof of failover.

Use PASS, FAIL, UNKNOWN, NOT REQUIRED, or NOT RUN. Evaluate in declared order.
A missing shared contract field stops all authoring. At the first row-local
failed or unknown prerequisite, mark only dependent rows NOT RUN, preserve
independent evidence, assign one task to the earliest current owner, and defer
later blockers. An unresolved consequential blocker makes both reviews REPAIR
and READY FOR NET-11 NO. Finish with the first blocker, dependent rows,
preserved evidence, unmeasured segments, shared dependencies, one owner task,
deferred items, both reviews, and readiness.

READY YES requires every critical SVC complete; required baselines current and
workload-bound; required CAP, LAT, and FOV rows supported; no invented target,
result, independence, cause, availability, recovery, or continuity claim; and
both reviews PASS. Show the artifact and wait. Do not measure, change, fail
over, recover, purchase, deploy, or continue to NET-11.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/PERFORMANCE-BASELINE-AND-FAILOVER-DECISION.md`

### Pass Criteria

- Each service has auditable criticality and requiredness; each critical service
  has a bounded workload, measurement contract, owner, evidence permission,
  target source, expiry, and maximum conclusion.
- Baselines separate observed results from targets, ceilings, causes, and
  permanent-normal claims.
- Capacity and latency decisions name their workload, method, evidence,
  unknowns, constraint, and prohibited conclusion.
- Failover rows expose shared dependencies, degraded operation, state and data
  behavior, test evidence, recovery, failback, rollback, authority, and owner.
- Global and row-local blockers preserve independent evidence and produce one
  earliest owner task, two reviews, and deterministic readiness.

### Stop Conditions

Stop for a missing shared contract field; unsafe or unauthorized measurement;
private values without a safe-reference rule; invented target, result, ceiling,
headroom, independence, cause, availability, or recovery claim; a request to
probe, load, scan, capture, change, fail over, fail back, recover, purchase, or
deploy; or any consequential `FAIL`, `UNKNOWN`, or `NOT RUN`.

### Sources and Limits

- Solomon, Michael G., and David Kim. *Fundamentals of Communications and
  Networking*. 3rd ed., Jones & Bartlett Learning, 2022. Selected Chapters 7,
  11, and 12 support durable redundancy, alternate-path, fault, baseline,
  capacity, throughput, and latency foundations. They do not prove a buyer
  workload, target, safe threshold, alternate independence, or failover result.
- Almes, G., S. Kalidindi, M. Zekauskas, and A. Morton. *A One-Way Delay Metric
  for IP Performance Metrics (IPPM)*, IETF RFC 7679, Internet Standard, 2016.
  Official record checked 2026-08-19. It supports explicit endpoints,
  direction, units, samples, statistics, clock uncertainty, and reporting for
  an IP-path metric. It does not define total AI response time or root cause.

### Next Step

Continue to **NET-11: Observe and Change the Network Without Guessing** only
after both reviews pass and `READY FOR NET-11: YES`. Carry forward stable
`SVC/BSL/CAP/LAT/FOV` IDs, workload, evidence, unknowns, owners, and maximum
conclusions, not a claim that performance, capacity, or availability is proven.


## 20. Observe and Change the Network Without Guessing

> **Chapter handle:** `NET-11`.

### Objective

Turn a small set of supplied AI-workflow signals into a truthful telemetry,
service-objective, alert, and change plan. Preserve missing and stale evidence,
bind every target and action to an owner, and make pre-change, post-change, abort,
and rollback proof inspectable. Do not convert a dashboard color into proof of
health, an alert into an incident, or a before-and-after difference into cause.

### Required Inputs

- accepted `NET-01` through `NET-10` requirements, asset, path, topology,
  dependency, route, access, zone, performance, and continuity artifacts;
- one declared AI workflow, consequence, criticality, accountable owner, safe
  service and dependency references, observation boundary, direction, and
  workload class;
- supplied signal sources, methods, clocks, collection permissions, sampling or
  aggregation windows, expected cadence, maximum staleness, and safe evidence;
- data sensitivity, minimum fields, sanitization, access, retention, and
  deletion or expiry decisions for metrics, logs, traces, events, and heartbeats;
- owner-supplied service indicators, targets, evaluation windows, allowed
  exceptions or budgets, approval, consequence, decision owner, and expiry;
- alert conditions, missing-data behavior, severity authority, route,
  acknowledgement expectation, runbook or handoff reference, and owner;
- when change is in scope, a current approved configuration baseline, exact
  proposed delta, affected configuration items and dependencies, impact review,
  approval route, window, validation, abort, rollback, and evidence needs; and
- Telemetry-integrity and Change-safety review owners.

If the shared contract lacks workflow, consequence, criticality, accountable
owner, safe-reference rule, accepted input references, observation boundary,
collection permission, protected data rule, target authority, alert authority,
current configuration-baseline rule, change boundary, or both review owners,
complete a blocked artifact and stop. A missing fact, owner, evidence item, or
prerequisite for one signal, objective, alert, or change is row-local: mark that
row `UNKNOWN`, stop its dependents, and preserve independent supplied evidence.
Do not poll, query, capture, scan, generate load, send an alert, create a ticket,
change configuration, use an emergency exception, deploy, roll back, or recover.

### Why This Matters

Observability is not the largest possible pile of data. It is the smallest
evidence set that helps an owner answer a declared question. An unbounded log
stream can expose content, identifiers, secrets, costs, and false confidence
while still failing to explain whether a buyer workflow completed.

A single current value lacks history and workload context. A historical
baseline can reveal change, but it is not automatically a promise, normality,
or a safe target. An objective is an owner decision that needs an indicator,
window, tolerance, consequence, approval, and expiry. These remain separate.

An alert is also a decision record, not merely a threshold. It must say what
evidence condition occurred, how long it persisted, what missing data means,
who receives it, what the receiver may do, and when it expires or deduplicates.
No data is not green. A triggered condition does not by itself prove outage,
security incident, user impact, root cause, or required response.

Changes make evidence harder. A later value may differ because of workload,
time, dependency, sampling, or unrelated state. A safe plan freezes comparable
preconditions, the exact delta, success and abort criteria, observation window,
and rollback before implementation. This chapter writes that plan; it does not
authorize the change.

### Core Model

Use four stable row types:

- `SIG-##` defines one minimum useful metric, log, trace, event, or heartbeat;
- `SLO-##` binds an indicator to an owner target, window, tolerance, and expiry;
- `ALR-##` turns a supported condition or no-data state into an owned route; and
- `CHG-##` freezes one proposed delta, evidence plan, accountable change owner,
  abort rule, and rollback. Its stable subchecks are `.PRE`, `.VAL`, `.POST`,
  and `.RBK` for precheck, validation, post-change comparison, and rollback.

Every displayed state must use one of these evidence-aware labels:

| Label | Meaning | Prohibited inference |
| --- | --- | --- |
| `WITHIN CONDITION` | Supplied current evidence does not cross the declared condition for its window. | The service is healthy, available, safe, or successful. |
| `OUTSIDE CONDITION` | Supplied current evidence crosses the declared condition for its window. | An outage, incident, impact, or cause is proven. |
| `NO DATA` | Expected evidence did not arrive within maximum staleness. | The observed service is up, down, or unchanged. |
| `UNKNOWN` | Evidence, interpretation, owner, or authority is insufficient. | A guess may replace the missing field. |
| `NOT EVALUATED` | A prerequisite has not passed or the row is outside the declared order. | The condition passed or failed. |

Artifact-row states remain `PASS`, `FAIL`, `UNKNOWN`, `NOT REQUIRED`, and `NOT
RUN`; never display them as health. `STALE` means a receipt exists but its newest
supported timestamp exceeds maximum staleness. `MISSING` means no expected
receipt exists after maximum staleness. Either supported receipt state can be a
truthful row `PASS`, but a critical one blocks current-signal readiness, makes
its SLO current-result branch `NOT RUN`, sets both reviews `REPAIR`, assigns one
evidence-owner task, and makes readiness `NO`. A declared no-data alert may
still evaluate directly from that signal; historical objectives and independent
rows remain preserved. An unsupported receipt state is `UNKNOWN` and stops its
dependents.

### Ordered Method

**Step 1 - Freeze the observation and change contract.** Record workflow,
consequence, criticality, accountable owner, safe references, accepted inputs,
boundary, direction, workload, permissions, protected budgets, clocks, cadence,
staleness, data rules, target and alert authority, configuration baseline,
change boundary, prohibited actions, and reviewers.

**Step 2 - Select minimum useful signals.** Start with the buyer question, not
with available fields. For every `SIG-##`, declare signal class, exact boundary,
unit or event shape, source, method, clock, workload, sample and aggregation,
expected cadence, maximum staleness, current data state, sensitivity,
minimization, retention, owner, and maximum conclusion. Treat collection load,
sampling, transformations, clock disagreement, and dropped records as evidence
limits. Do not add content, prompts, responses, tokens, identifiers, or secrets
when a less sensitive count or state answers the question.

**Step 3 - Separate baseline from objective.** Link current observations to the
accepted `NET-10` baseline only when boundary, direction, workload, method,
clock, unit, and comparison window are compatible. For each `SLO-##`, record the
indicator, owner target, evaluation window, allowed exception or budget rule,
target source, approval, expiry, current result, data coverage, uncertainty,
consequence, and decision owner. Never invent a percentage, threshold, error
budget, or universal definition of acceptable service.

**Step 4 - Design truthful alerts and status.** An `ALR-##` needs an
evidence-supported condition and duration, separate missing or stale data
behavior, status label, owner-authorized severity, deduplication or suppression,
expiry, route, acknowledgement expectation, and runbook or incident-handoff
reference. State whether automatic action is prohibited. An alert can request
review; it cannot assign cause or declare an incident without the responsible
owner's evidence and authority.

**Step 5 - Freeze the proposed change.** Create `CHG-##` only from a supplied
request. Record why it is needed, current approved baseline, affected
configuration items, exact delta, exclusions, dependencies, security, privacy,
cost and workflow impact, approval route, window, communications, prechecks,
backup or restore reference, evidence ticket, accountable change owner, and
implementation authority. Keep the change owner, approval authority, and
rollback owner separate. Do not write a live value or command when the user has
not authorized implementation.

**Step 6 - Make success, abort, and rollback testable.** Before a change, record
the expected result, exact comparable post-change evidence, observation window,
allowed variance, abort condition, rollback trigger, rollback owner, and proof
that the restoration reference is current. A missing rollback path blocks the
change row; it does not erase independent telemetry or SLO evidence. A rollback
plan does not prove rollback will work. Record `.PRE`, `.VAL`, `.POST`, and
`.RBK` states so a local blocker has stable dependent IDs.

**Step 7 - Preserve the operational handoff.** For an outside condition, no
data, failed change, or unexplained deviation, package only the safe references,
time window, workflow consequence, observed state, evidence gaps, current owner,
allowed next action, and prohibited conclusions needed by `NET-12`. Keep alert,
incident classification, containment, recovery, and cause as separate owner
decisions.

**Step 8 - Review readiness.** `READY FOR NET-12: YES` requires a complete
shared contract; current and bounded required signals; approved, current, and
evidence-backed required objectives and alerts; every required in-scope change
supported by baseline, impact, accountable change ownership, implementation
authority, approval, validation, abort, rollback, observation, and evidence
plans; truthful missing-data states; no invented
health, target, incident, cause, success, approval, or recovery; and both
reviews `PASS`.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
| --- | --- | --- |
| Quick | One buyer workflow needs a truthful status. | Freeze one critical signal, cadence, staleness rule, safe reference, owner, and maximum conclusion. |
| Operator | A service needs usable monitoring. | Add workload-bound signals, one owner objective, no-data behavior, route, and retention. |
| Builder | A proposed change needs evidence. | Add current baseline, exact delta, impact, precheck, validation, abort, rollback, and post-change window. |
| Architect | Several paths or teams share status. | Reconcile clocks, dependencies, SLO ownership, alert routing, configuration items, exceptions, and retirement. |
| Lab | You need branch-local blocker proof. | Use fictional evidence; block one change while preserving independent signal and SLO decisions. |

### Fictional Example

> **Fictional scenario.** Harborlight Workshop supplies sanitized accepted
> `SVC-01`, `BSL-01`, and `BSL-02` references for its critical support-retrieval
> workflow. The end-to-end boundary, workload, same-host clock, and methods are
> unchanged. The owner supplies an SLO, alert condition, 24-hour fictional
> evidence set, a proposed observer-cadence change, and plan-writing authority
> only. No collection, alert, ticket, change, exception, or rollback is allowed.

`CHG-01` names change owner `Owner-T`, current configuration `CFG-10`, item
`CI-OBS-01`, the exact delta, exclusions, dependencies, impacts, communication
`COM-11`, `.PRE`, success, abort, post-change, evidence `EVD-11`, and retirement
fields. Its declared order puts impact evidence first. Only the collection-load
comparison and current rollback reference are missing there; implementation
approval and scheduling are later deferred questions.

| Row | Supplied or proposed state | Bounded result |
| --- | --- | --- |
| `SIG-01` | End-to-end completion p95 by 15-minute window; same workflow boundary, workload class, source method, and clock as `BSL-01`; 96 current window records at `REF-SIG-01`; no content or identifiers retained | `PASS` for current supplied coverage; no health or cause claim |
| `SIG-02` | Completion count divided by elapsed window; same workload and method class as `BSL-02`; expected every 15 minutes, maximum staleness 20 minutes, current safe ref `REF-SIG-02` | `PASS` for current supplied count evidence; no capacity or availability claim |
| `SLO-01` | Owner-approved p95 target at or below 3.0 seconds per 15-minute window; at most two outside-target windows in a rolling 24 hours; approval `DEC-11`, expiry in 30 days | 94 of 96 windows within target and two outside; `PASS` at the owner budget boundary for this supplied day only |
| `ALR-01` | `OUTSIDE CONDITION` after three consecutive p95 windows above 3.0 seconds; `NO DATA` after one expected record exceeds 20 minutes; warning route to the named operator; no automatic action | Current 24-hour evidence never meets the outside condition and has no missing windows; `PASS` for evaluation only, not proof of health |
| `CHG-01` | Complete supplied contract above; proposed cadence changes from 60 to 30 seconds; collection-load comparison and current rollback reference are missing | `UNKNOWN`; `CHG-01.VAL`, `CHG-01.POST`, and `CHG-01.RBK` are `NOT RUN`; no implementation or benefit claim |

Owner-T must first supply a bounded collection-load comparison and
current rollback reference for `CHG-01`. `SIG-01`, `SIG-02`, `SLO-01`, and
`ALR-01` remain preserved. Later change approval and scheduling questions are
deferred. Both reviews are `REPAIR` and `READY FOR NET-12` is `NO`.

### Evidence-flow visual

```text
[accepted workflow + observation contract]
                   |
                [SIG-##]
                /      \
          [SLO-##]   [ALR-##]
                \      /
                [CHG-##]
                   |
      [two reviews + READY NET-12]

Row-local blocker: dependent rows NOT RUN; independent evidence continues.
```

Text equivalent: freeze the workflow and observation contract, collect only
declared signals, compare compatible evidence with an owner objective, route a
truthful condition, and prepare but do not execute a reversible change. A local
change blocker preserves independent telemetry and objective decisions.

### Exercise or Test

Create the exact artifact for one fictional critical workflow with two signals,
one owner objective, one outside or no-data alert branch, and one proposed
change. Withhold either comparable collection-load evidence or the rollback
reference. Prove the change becomes `UNKNOWN`, dependent validation stays `NOT
RUN`, independent signals and SLO evidence remain evaluated, one earliest owner
task is assigned, later blockers defer, both reviews become `REPAIR`, and
readiness is `NO` without collecting data or changing anything.

### Exact Agent Checkpoint Prompt

**Test state:** `PASSED INDEPENDENT QA`.

```text
Act as my read-only AI-workflow telemetry, service-objective, alert, and change
plan recorder. Use only accepted NET-01 through NET-10 artifacts, the exact
template, current official guidance I provide, and sanitized evidence I provide.
Do not browse private systems, poll, query, scan, capture, generate load, send an
alert, create or update a ticket, change configuration or policy, approve an
exception, deploy, roll back, contain, recover, purchase, or claim health,
availability, incident status, cause, change success, or recovery.

Confirm workflow, consequence, criticality, accountable owner, accepted safe
references, observation boundary, workload, collection permission, clocks,
cadence, staleness, data rules, SLO and alert authority, configuration baseline,
change and rollback authority, prohibited actions, and both review owners.
Mark missing items UNKNOWN. If a shared contract field is unclear, complete the
exact template as a blocked artifact, set both reviews REPAIR, set READY FOR
NET-12 NO, show it, and stop. A missing fact, evidence item, or owner for one
SIG, SLO, ALR, or CHG row is row-local, not a global stop.

Create AI-GROWTH-WORKSPACE/artifacts/TELEMETRY-SLO-ALERT-AND-CHANGE-PLAN.md
from the exact supplied template. If writing is unavailable, print it and do not
claim it was saved. Keep private values behind opaque safe references.

Create minimum SIG-## rows. Record class, boundary, unit or event, source,
method, clock, workload, sample, aggregation, cadence, staleness, data state,
safe ref, privacy, retention, owner, prerequisites, state, conclusion, and task.
Use CURRENT, STALE, MISSING, or UNKNOWN. STALE has an over-age receipt; MISSING
has none after maximum staleness. A supported required STALE or MISSING SIG may
PASS as a receipt record, but its SLO current-result branch is NOT RUN, a
declared no-data ALR branch may evaluate, both reviews are REPAIR, one task goes
to the evidence owner, and readiness is NO. Preserve independent rows. An
unsupported receipt is UNKNOWN and stops dependents.

Create SLO-## rows with supplied SVC, SIG, and BSL support. Keep indicator,
owner target, comparison, evaluation window, workload, allowed exception or
budget, target source, approval, expiry, current result, coverage, uncertainty,
consequence, owner, prerequisites, state, maximum conclusion, and task separate.
Do not turn a baseline into a target or invent a universal threshold.

Create ALR-## rows from supplied evidence conditions. Record duration, missing
or stale data behavior, status label, owner-authorized severity, deduplication,
suppression, expiry, route, acknowledgement target, runbook or incident-handoff
ref, automatic-action prohibition, owner, authority, prerequisites, state,
maximum conclusion, and task. Use WITHIN CONDITION, OUTSIDE CONDITION, NO DATA,
UNKNOWN, or NOT EVALUATED. Do not infer incident, outage, impact, or cause.

Create CHG-## only for supplied proposals. Record reason, baseline and items,
delta, exclusions, impacts, approval, window, communications, precheck, restore,
success, abort, post-change comparison, rollback, evidence, retirement, change
owner, implementation authority, prerequisites, conclusion, and task. Keep
change, approval, and rollback owners separate. Record `.PRE`, `.VAL`, `.POST`,
and `.RBK` subcheck states and dependencies. Never write live commands. A
missing required field makes CHG UNKNOWN and dependent subchecks NOT RUN.

Evaluate in declared order. At the first row-local failed, unknown, or required
noncurrent-signal prerequisite, mark only dependent rows or subchecks NOT RUN,
preserve independent supplied
evidence, assign one task to the earliest current owner, and defer later
blockers. Package an outside, no-data, failed-change, or unexplained-deviation
handoff with safe refs, window, workflow consequence, observed state, evidence
gaps, owner, allowed next action, and prohibited conclusions. Do not classify an
incident, contain, recover, or claim cause.

READY YES requires a complete contract; every critical required signal current,
bounded, and privacy-reviewed; every required objective supplied, approved,
current, and evidence-backed; every required alert truthful about missing data
and assigned an owner and route; every required in-scope change supported by a
current baseline, impact review, accountable change owner, implementation
authority, approval, validation, abort, rollback, observation, and evidence
plan; no invented data, target, health, severity,
incident, cause, success, approval, or recovery; and both reviews PASS. An
explicitly out-of-scope change may be NOT REQUIRED. Finish with the first
blocker, dependent rows, preserved evidence, one owner task, deferred items,
NET-12 handoff, both reviews, and readiness. Show the artifact and wait. Do not
collect, alert, change, deploy, roll back, contain, recover, or continue.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/TELEMETRY-SLO-ALERT-AND-CHANGE-PLAN.md`

### Pass Criteria

- Every signal is tied to one workflow question, boundary, method, clock,
  workload, cadence, staleness rule, data boundary, owner, and safe evidence.
- Baselines, indicators, owner targets, windows, exception rules, current
  results, and maximum conclusions remain separate and comparable.
- Alerts expose missing data, use owner-approved severity and routing, prohibit
  unsupported automatic action, and do not claim incident or cause.
- Every required change freezes current state, exact delta, impacts, approval,
  validation, abort, rollback, observation, evidence, and owner before action.
- Two reviews and deterministic readiness preserve independent evidence and
  produce a bounded `NET-12` handoff without operating the network.

### Stop Conditions

Stop for a missing shared contract field; private or unauthorized collection;
unbounded content, identifier, secret, cost, or retention; incompatible baseline
comparison; invented signal, target, threshold, severity, health, incident,
cause, approval, success, rollback, or recovery; missing-data shown as healthy;
an in-scope required change without impact, approval, abort, validation, or
rollback evidence; a request to collect, alert, ticket, change, deploy, contain,
or recover; or any consequential required `FAIL`, `UNKNOWN`, or `NOT RUN`.

### Sources and Limits

- Solomon, Michael G., and David Kim. *Fundamentals of Communications and
  Networking*. 3rd ed., Jones & Bartlett Learning, 2022. Selected Chapter 12
  foundations support monitoring over time, context, baselines, collection
  impact, reporting, and governed change. They do not prescribe this artifact,
  signal set, SLO, alert threshold, status label, change, tool, or AI workflow.
- NIST. [SP 800-128, Guide for Security-Focused Configuration Management of
  Information Systems](https://www.nist.gov/publications/guide-security-focused-configuration-management-information-systems-0).
  Official record checked 2026-08-19. It supports security-aware configuration
  baselines, impact analysis, approval, testing, monitoring, and documentation.
  Its federal security-management context does not define this workflow,
  threshold, authority, change window, or configuration.
- NIST. [SP 800-61 Rev. 3, Incident Response Recommendations and Considerations
  for Cybersecurity Risk Management](https://csrc.nist.gov/pubs/sp/800/61/r3/final).
  Final publication checked 2026-08-19; it was published in April 2025 and
  supersedes Rev. 2. It supports integrating incident response across
  cybersecurity risk management and continuous improvement. It does not make
  every alert an incident or authorize containment, recovery, or a cause claim.

### Next Step

Continue to **NET-12: Troubleshoot, Contain, Recover, and Prove the Capstone**
only after both reviews pass and `READY FOR NET-12: YES`. Carry forward the
accepted workflow and dependency references, signal contracts, SLO authority,
alert states, missing-data records, change evidence, first blocker, and bounded
handoff packet, not a dashboard color or claim that the network is healthy.


## 21. Troubleshoot, Contain, Recover, and Prove the Path

> **Chapter handle:** `NET-12`.

### Objective

Turn one supplied AI-workflow deviation into an evidence-bound case, layered
diagnostic record, bounded action plan, and comparable recovery proof. Separate
an alert from an owner-declared incident, a failed check from root cause, a
containment proposal from authority, and restored operation from permanent
health. Finish the networking track without operating a live network.

### Required Inputs

- accepted `NET-01` through `NET-11` workflow, asset, path, topology, layer,
  dependency, route, access, zone, baseline, failover, telemetry, and change
  artifacts;
- one supplied symptom or deviation, first-observed and last-known-good windows,
  affected and unaffected scope, consequence, criticality, and safe evidence;
- accountable case owner plus service-incident and security-incident
  classification authorities;
- allowed evidence-review and isolated-test boundary, sensitive-data rule,
  preservation need, retention, and chain-of-custody owner when applicable;
- containment, recovery, rollback, communication, closure, and residual-risk
  authorities; and
- Diagnosis-integrity and Recovery-evidence review owners.

If the shared contract lacks workflow, consequence, criticality, accountable
case owner, safe-reference rule, accepted input references, evidence boundary,
protected-data rule, classification authority, action boundary, closure
authority, or both review owners, complete a blocked artifact and stop. A
missing fact, evidence item, owner, or prerequisite for one case check, action,
or proof row is local: mark it `UNKNOWN`, stop its dependents, and preserve
independent supplied evidence. Do not query, scan, capture, test, isolate,
block, restart, restore, patch, reconfigure, disclose, close, or claim cause.

### Why This Matters

A visible symptom is not a diagnosis. A slow response can originate at several
path or service boundaries. Changing several things at once can destroy
comparison evidence or create a second failure.

Only the responsible owner may classify an alert as an incident. A declared
security incident
may add evidence-preservation, legal, privacy, communication, and response-team
requirements that a routine service deviation does not. This chapter records
those decisions; it supplies none of that authority.

Recovery requires more than a green tile. The post-state must use the same
workflow boundary, workload, method, clock, window, and acceptance rule as the
pre-state. It must also preserve rollback, unresolved risks, and the owner's
closure decision. A passing window proves only the declared window.

### Core Model

Use four stable row types:

- `CAS-##` freezes the symptom, scope, consequence, classification, authority,
  evidence rules, and maximum conclusion;
- `CHK-##` tests one competing hypothesis at one declared boundary;
- `ACT-##` records a proposed or already supplied `CONTAINMENT`, `RECOVERY`, or
  `ROLLBACK` proposal, receipt, or owner-authorized not-required decision; and
- `PRF-##` compares accepted pre-state and post-state evidence and records
  residual risk, follow-up, and owner closure.

Use only `DEVIATION`, `DECLARED SERVICE INCIDENT`, `DECLARED SECURITY INCIDENT`,
or `UNKNOWN` for case classification. Use `OBSERVED`, `NOT OBSERVED`, `NO DATA`,
`UNKNOWN`, or `NOT EVALUATED` for evidence results. These labels do not replace
artifact-row states `PASS`, `FAIL`, `UNKNOWN`, `NOT REQUIRED`, and `NOT RUN`.

A `DECLARED SECURITY INCIDENT` must carry the supplied classification owner,
authority reference, preservation and custody rule, communication boundary, and
response handoff. Missing one of those fields makes the security-response branch
`UNKNOWN`; it does not erase independent service evidence or authorize a less
restricted service action. A `DEVIATION` may still be consequential, but it
cannot borrow security-incident authority. Reclassification creates a new
owner decision and review point rather than silently changing the existing row.

### Ordered Method

**Step 1 - Freeze the case contract.** Record the workflow, consequence,
criticality, symptom, time windows, affected and unaffected scope,
last-known-good reference, recent change references, current owner, safe
evidence, permissions, preservation need, authorities, prohibited actions, and
reviewers. Record the owner's case classification; do not infer it.

**Step 2 - Separate observation from hypothesis.** Copy only accepted safe
references and supplied observations. List competing hypotheses without ranking
them as facts. Name evidence that would distinguish each hypothesis and the
maximum conclusion available if the evidence supports or fails to support it.

**Step 3 - Choose the smallest useful checks.** Use `NET-04` layer locations
and the accepted path and dependency records to select the first disputed
boundary. A `CHK-##` needs one hypothesis, layer or dependency, supplied source,
method, workload, time, authorization, expected discriminating results, actual
supplied result, uncertainty, prerequisite, owner, and next decision. Do not
walk every layer when accepted evidence already settles it.

**Step 4 - Preserve competing explanations.** A passing check narrows only the
named hypothesis. It does not prove every lower layer, rule out an intermittent
fault, or establish cause. A failed check locates the next evidence need, not a
license to change configuration. Stop at the first unsupported prerequisite.

**Step 5 - Bound containment.** Create a `CONTAINMENT` action only for a
supplied owner decision. Record exact target, allowed and prohibited effect,
dependency and continuity impact, evidence-preservation need, privacy,
accountable action owner, approval authority, duration, monitoring, success,
abort, rollback owner, and communication rule.
Keep service continuity and security-response decisions separate.
An owner-authorized not-required decision records its authority ref, rationale,
scope, expiry, and state `NOT REQUIRED`; it is not a proposal or receipt.

**Step 6 - Bound recovery and rollback.** A `RECOVERY` row needs an approved
last-known-good or target state, exact scope, prerequisites, dependency order,
validation window, accountable action owner, approval authority, success and
abort conditions, rollback trigger, rollback owner, and evidence plan. An
already performed action can be recorded only from a supplied receipt. A
proposed action remains `NOT RUN`.

**Step 7 - Prove acceptance and closeout.** A `PRF-##` compares compatible
pre-state and post-state evidence, workflow success, critical dependencies,
telemetry freshness, security and privacy checks, rollback readiness, residual
risk, and follow-up. Only the closure owner may set `CLOSED BY OWNER`. Restored
service does not prove cause removal, permanent health, or absence of impact.

**Step 8 - Review the capstone.** `CAPSTONE VERIFIED: YES` requires a complete
contract; owner classification; supported checks; every required action either
`PASS` from a supplied receipt or explicitly `NOT REQUIRED`; comparable
acceptance proof; rollback and residual-risk disposition; named follow-up;
owner closure; no invented evidence, incident, cause, action, success, or health
claim; and both reviews `PASS`.

### Choose Your Depth Route

| Route | Use it when | Complete before moving on |
| --- | --- | --- |
| Quick | One deviation needs a truthful handoff. | Freeze one case, one disputed boundary, evidence gap, owner, and maximum conclusion. |
| Operator | One service path needs diagnosis. | Add competing hypotheses, ordered checks, current evidence, and escalation boundary. |
| Builder | A bounded action is proposed. | Add target, dependency impact, approval, preservation, success, abort, rollback, and proof. |
| Architect | Several services or teams share the case. | Reconcile authority, continuity, data, communication, dependency order, residual risk, and closure. |
| Lab | The networking track needs capstone proof. | Use only supplied fictional or isolated receipts and comparable pre/post evidence. |

### Fictional Example

> **Fictional isolated lab.** Harborlight Workshop supplies a `NET-11`
> `OUTSIDE CONDITION` for three consecutive support-retrieval p95 windows, no
> missing data, accepted path and baseline references, and owner receipts from
> an isolated lab. Production was never in scope. The owner classifies the case
> as `DEVIATION`, not a declared service or security incident. The agent may
> record evidence only. Supplied action receipt refs include exact target,
> allowed and prohibited effect, dependency and continuity impact, preservation,
> privacy, duration, monitoring, success, abort, communication, and evidence.

| Row | Supplied evidence or decision | Bounded result |
| --- | --- | --- |
| `CAS-01` | Same workflow, workload, clock, and 15-minute method as accepted references; p95 windows are 3.7, 4.2, and 3.8 seconds against the owner 3.0-second condition; other declared lab workflows remain within their own conditions | `PASS`; deviation is observed for this lab window; impact and cause remain unknown |
| `CHK-01` | Accepted path signals stay within their declared conditions while the supplied retrieval-wait segment alone rises when lab state `CFG-22` is selected; `CFG-21` and `CFG-22` receipts are otherwise comparable | `PASS`; evidence supports a `CFG-22` contribution in this lab case, not universal root cause |
| `ACT-01` | Owner-supplied `CONTAINMENT` receipt names action owner `Owner-R`, approval authority `AUTH-LAB`, and rollback owner `Owner-B`; it disabled only lab intake, preserved safe logs, left production untouched, and retained a timed rollback | `PASS` for the supplied receipt; no live action is authorized |
| `ACT-02` | Owner-supplied `RECOVERY` receipt names action owner `Owner-R` and approval authority `AUTH-LAB`, restored approved lab state `CFG-21`, and records rollback owner `Owner-B`, abort rule, and evidence references | `PASS` for the supplied isolated-lab receipt only |
| `PRF-01` | Eight comparable post-recovery windows are 2.1-2.6 seconds, eight of eight lab tasks complete, critical signals are current, no protected content is retained, rollback remains available, residual risk is accepted for this lab window by `AUTH-RISK`, follow-up owner `Owner-F` is due before reuse, and closure owner `Owner-C` records `CLOSE-LAB-01` | `PASS`; `CLOSED BY OWNER`; no production, permanence, security, or general-health claim |

Both reviews can `PASS` and `CAPSTONE VERIFIED` can be `YES` for this isolated
lab packet. The maximum conclusion is that `CFG-22` contributed under the
declared lab conditions and the supplied `CFG-21` recovery met the eight-window
acceptance rule. It is not a production certification or root-cause proof.

### Evidence-flow visual

```text
[accepted NET-01..NET-11 + case contract]
                     |
                  [CAS-##]
                     |
                  [CHK-##]
                     |
                  [ACT-##]
                     |
                  [PRF-##]
                     |
       [two reviews + CAPSTONE VERIFIED]

Local blocker: dependent rows NOT RUN; independent evidence remains.
```

Text equivalent: freeze and classify the case, test one evidence-supported
boundary at a time, record only authorized action proposals or supplied
receipts, compare compatible recovery evidence, expose residual risk, and let
the named owner close the case.

### Exercise or Test

Complete the artifact from supplied fictional evidence, but withhold the
post-recovery workload or method reference. The case, independent checks, and
supplied action receipts remain preserved. `PRF-01` becomes `UNKNOWN`, owner
closure stays `NOT RUN`, one evidence-owner task is assigned, later closeout
questions defer, both reviews become `REPAIR`, and `CAPSTONE VERIFIED` is `NO`.
Do not rerun a test, change a system, or invent comparable evidence.

### Exact Agent Checkpoint Prompt

**Test state:** `PASSED INDEPENDENT QA`.

```text
Act as my read-only AI-workflow troubleshooting and recovery capstone recorder.
Use only accepted NET-01 through NET-11 artifacts, the exact template, current
official guidance I provide, and sanitized fictional or isolated evidence I
provide. Do not query, scan, capture, test, isolate, block, restart, restore,
patch, reconfigure, send, disclose, close a case, or claim incident, impact,
cause, recovery, security, or health.

Confirm workflow, consequence, criticality, case owner, symptom, first-observed
and last-known-good windows, affected and unaffected scope, accepted safe
references, evidence permissions, protected-data and preservation rules,
service-incident and security-incident classification authorities, action and
rollback boundaries, communication, residual-risk and closure authorities,
prohibited actions, and both review owners. Mark missing items UNKNOWN. If a shared field is
unclear, complete the exact template as blocked, set both reviews REPAIR, set
CAPSTONE VERIFIED NO, show it, and stop. A missing item for one row is local.

Create AI-GROWTH-WORKSPACE/artifacts/NETWORK-TROUBLESHOOTING-AND-RECOVERY-CAPSTONE.md
from the exact supplied template. If writing is unavailable, print it and do not
claim it was saved. Keep private values behind opaque safe references.

Create CAS-## from supplied observations and the owner's classification. Use
DEVIATION, DECLARED SERVICE INCIDENT, DECLARED SECURITY INCIDENT, or UNKNOWN.
An alert or outside condition is not an incident by itself. List competing
hypotheses separately from observations and cap every conclusion.
A declared security incident needs a supplied classification owner and
authority ref, preservation and custody rule, communication boundary, and
response handoff. If one is missing, mark that branch UNKNOWN, preserve
independent service evidence, set both reviews REPAIR, and set capstone NO.

Create CHK-## rows in declared order. Record one hypothesis, layer or
dependency, source, method, workload, window, authorization, expected
discriminating results, actual supplied result, uncertainty, owner,
prerequisites, state, maximum conclusion, and task. Use OBSERVED, NOT OBSERVED,
NO DATA, UNKNOWN, or NOT EVALUATED for evidence result. Do not invent a command,
run a check, change multiple variables, or promote a failed check to root cause.

Create ACT-## rows only for owner-supplied proposals, supplied receipts, or an
owner-authorized not-required decision. Mark CONTAINMENT, RECOVERY, or ROLLBACK
and PROPOSED, RECEIPT, or OWNER NOT-REQUIRED DECISION. Record exact target,
allowed and prohibited effect, dependency and continuity impact, evidence
preservation, privacy, accountable action owner, approval authority, duration,
communication, monitoring, success, abort, rollback trigger, method and owner,
evidence, prerequisites, state, conclusion, and task. Keep action, approval, and
rollback ownership separate. A proposal remains NOT RUN. A receipt proves only
its bounded supplied record. A not-required decision needs authority ref,
rationale, scope, expiry, and state NOT REQUIRED.

Create PRF-## rows with comparable pre-state and post-state boundaries,
workload, method, clock, window, results, task success, critical dependencies,
telemetry freshness, security and privacy checks, rollback readiness, residual
risk, acceptance authority and owner, follow-up owner and due rule, closure
owner, decision and authority ref, prerequisites,
state, maximum conclusion, and task. Missing comparability makes PRF UNKNOWN and
closure NOT RUN. Restored operation does not prove cause removal or permanence.

At the first local failed or unknown prerequisite, mark only dependents NOT RUN,
preserve independent evidence, assign one task to the earliest current owner,
and defer later blockers. Treat a required PROPOSED action in state NOT RUN as
the first unexecuted required row: mark dependent proof and closure NOT RUN,
assign one action-owner task, set both reviews REPAIR, and set capstone NO.
CAPSTONE YES requires the complete contract, owner
classification, supported checks, every required action PASS from a supplied
receipt or NOT REQUIRED, comparable acceptance proof, rollback and residual-risk
disposition, named follow-up, CLOSED BY OWNER, no invented evidence or action,
and both reviews PASS. Finish with the first blocker, dependent rows, preserved
evidence, one owner task, deferred items, both reviews, and capstone result.
Show the artifact and wait. Do not operate the network or continue.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/NETWORK-TROUBLESHOOTING-AND-RECOVERY-CAPSTONE.md`

### Pass Criteria

- Case scope, owner classification, evidence rules, authority, and maximum
  conclusion are explicit.
- Checks test one hypothesis at a time and preserve competing explanations.
- Action proposals or receipts expose impact, approval, preservation, abort,
  rollback, owner, and proof limits.
- Acceptance uses comparable pre/post evidence, residual risk, follow-up, and
  owner closure without claiming permanent health or root cause.
- Two reviews produce a deterministic capstone result while preserving all
  accepted upstream evidence.

### Stop Conditions

Stop for a missing shared contract field; unsupported incident classification;
private or unauthorized evidence; destructive or live testing; invented cause,
action, approval, receipt, success, closure, or health; containment without
dependency, preservation, approval, abort, or rollback decisions; recovery
without a target, comparable proof, residual-risk owner, or rollback; a request
to operate or disclose; or any consequential required `FAIL`, `UNKNOWN`, or
`NOT RUN`.

### Sources and Limits

- Solomon, Michael G., and David Kim. *Fundamentals of Communications and
  Networking*. 3rd ed., Jones & Bartlett Learning, 2022. Selected Chapters 13
  and 15 support bounded incident planning, evidence handling, ticket intake,
  change history, escalation, layered diagnosis, recovery, and lessons. They do
  not prescribe this artifact, case labels, row model, authority, checks,
  actions, proof rule, AI workflow, or threshold.
- NIST. [SP 800-61 Rev. 3, Incident Response Recommendations and Considerations
  for Cybersecurity Risk Management](https://csrc.nist.gov/pubs/sp/800/61/r3/final).
  Final publication checked 2026-08-19; it was published in April 2025 and
  supersedes Rev. 2. It supports integrating incident response across
  cybersecurity risk management and continuous improvement. It does not
  classify this case, authorize an action, prescribe disclosure, or prove cause.

### Next Step

The networking track is complete only after both reviews pass and `CAPSTONE
VERIFIED: YES`. Carry the accepted path, dependency, trust, performance,
telemetry, case, check, action-receipt, acceptance, residual-risk, and follow-up
records into the English manuscript integration review. Do not carry forward a
dashboard color, unsupported incident label, or general health claim.
