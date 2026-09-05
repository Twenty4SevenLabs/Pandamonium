# Orientation

## 1. What You Will Build and What This Package Will Not Do

> **Chapter handle:** `ORI-01`.

Use one user-owned project workspace in a local folder, private repository, or
private document directory. Keep it dated and under your control.

Create this starting structure:

```text
AI-GROWTH-WORKSPACE/
├── AGENTS.md
├── STATUS.md
├── DECISIONS.md
├── SYSTEM-MAP.md
├── MEMORY.md
├── BUGS.md
├── HANDOVER.md
├── BACKLOG.md
├── artifacts/
├── evidence/
└── tickets/
    ├── open/
    ├── in-progress/
    ├── completed/
    ├── failed/
    ├── blocked/
    └── skipped/
```

Generated project artifacts belong under `artifacts/`. Control files stay at the
workspace root. Implementation source stays in a separate repository whose
location and permitted boundary are recorded in `SYSTEM-MAP.md`.

### The artifacts and why they matter

- **`AGENTS.md`** - operating contract for every participating agent.
- **`STATUS.md`** - current stage, blockers, and next action.
- **`DECISIONS.md`** - dated accepted choices and reconsideration triggers.
- **`SYSTEM-MAP.md`** - architecture, flows, dependencies, and implementation repository reference.
- **`MEMORY.md`** - compact durable project facts with provenance.
- **`BUGS.md`** - known defects, effects, workarounds, and repair tickets.
- **`HANDOVER.md`** - exact continuation point for the next session.
- **`BACKLOG.md`** - useful ideas deferred until the current stage passes.
- **`artifacts/`** - assessments, plans, inventories, and playbooks.
- **`evidence/`** - provider or system-of-record readback, tests, restore records, and acceptance notes.
- **`tickets/`** - work moving through open, active, and truthful final states.

### Working rule

Complete one section, review its file, and update `STATUS.md`. Durable systems grow from reviewed decisions, not one enormous prompt.

**Produced artifact:** the empty `AI-GROWTH-WORKSPACE` structure.

**Completion check**

- The workspace exists in a location you control.
- `STATUS.md` identifies this package, today’s date, and “Foundation: in progress.”
- `DECISIONS.md` and `BACKLOG.md` exist, even if they are nearly empty.
- You know where later generated files will be stored.

**Next step:** establish how you and your LLM will work through the package.

---


## 2. Choose Your Learning Depth

> **Chapter handle:** `ORI-02`.

### Objective

Choose the smallest route that produces the evidence you need now without
turning one guide into five duplicated books. Your route controls how deeply
you work through each chapter; it does not change the chapter's facts, safety
rules, authority boundaries, or completion evidence.

### The Five Routes

| Route | Use it when | Required exit |
| --- | --- | --- |
| `QUICK` | You need the decision, boundary, and next safe action | Record the decision, owner, blocker, and next review point |
| `OPERATOR` | You own the workflow and need a usable operating artifact | Complete the chapter artifact and its pass or blocked state |
| `BUILDER` | You will implement or test the design in an authorized environment | Add interfaces, validation, rollback, and implementation evidence |
| `ARCHITECT` | You must reconcile several systems, owners, risks, or failure domains | Record alternatives, dependencies, tradeoffs, and promotion criteria |
| `LAB` | You need practice before touching a consequential system | Complete the fictional or isolated exercise and preserve its evidence |

Start with `OPERATOR` when you are unsure. Move down to `QUICK` when you only
need a bounded decision. Move up to `BUILDER` or `ARCHITECT` only when the
owner has authorized that work and the added depth changes a real decision.
Use `LAB` whenever live access, private data, cost, safety, or authority is not
ready.

### One Chapter, One Canonical Explanation

Every chapter has one objective, one core model, one artifact, and one set of
stop conditions. Route markers add depth to that shared lesson:

- `QUICK` identifies the minimum decision and the facts that can block it;
- `OPERATOR` completes and reviews the buyer-owned record;
- `BUILDER` adds implementation contracts and reversible tests;
- `ARCHITECT` examines system-wide consequences and alternatives; and
- `LAB` proves the method with fictional values or an isolated environment.

Do not complete every route automatically. That creates activity rather than
evidence. A route is complete only when its exit is visible in the chapter
artifact. Reading more text is not a completion state.

### Choose a Route for the Current Outcome

Create one row before beginning a part of the guide:

| Field | Record |
| --- | --- |
| Current outcome | One approved result, not a general wish |
| Consequence | What happens if the decision is wrong or incomplete |
| Starting evidence | Accepted artifact or source-of-truth reference |
| Chosen route | `QUICK`, `OPERATOR`, `BUILDER`, `ARCHITECT`, or `LAB` |
| Why this depth is enough | Decision that the extra work must support |
| Authority boundary | Read, test, implement, approve, or no live action |
| Exit evidence | Exact artifact, review, receipt, or blocked record |
| Promotion trigger | Evidence that would justify a deeper route |
| Owner and review date | Accountable person and next check |

Changing routes is allowed. Record why. For example, an `OPERATOR` inventory
may expose an unknown trust boundary and promote the work to `ARCHITECT`. A
planned `BUILDER` test may move to `LAB` when production authorization is
missing. Never relabel incomplete work as a shallower route after the fact.

### Agent Checkpoint Prompt

```text
Act as a route-selection facilitator for one chapter of the MADPANDA3D AI
Growth Package. Use only the supplied outcome, current artifact, chapter
contract, and authority statement. Do not load unrelated modules.

Return one LEARNING-DEPTH-DECISION with: outcome, consequence, accepted input,
recommended route, why that depth is sufficient, excluded work, authority
boundary, exact exit evidence, promotion trigger, owner, and review date.

Choose OPERATOR when the evidence does not justify another route. Choose LAB
when a live test or implementation is not authorized. Mark decision-changing
missing information UNKNOWN and assign one owner task. Do not implement,
purchase, connect, deploy, send, or infer authority. Show the record and wait.
```

### Produced Artifact

`AI-GROWTH-WORKSPACE/artifacts/LEARNING-DEPTH-DECISION.md`

### Pass Criteria

- One current outcome and consequence determine the route.
- The chosen route has explicit included and excluded work.
- The exit is an observable artifact or truthful blocked state.
- Authority and promotion triggers are recorded.
- The choice does not weaken a chapter hard gate.

### Stop Conditions

Stop when there is no approved outcome, no owner, no chapter contract, or no
authority statement; when the requested route would expose private material or
operate a consequential system; or when the route is being used to skip a
required safety, source, rights, accessibility, or review gate.

### Next Step

Carry the route record into `ORI-03`. The agent working contract remains the
same at every depth: facts stay labeled, consequential actions stay owned, and
progress stays durable.


## 3. Work With an LLM Without Losing Ownership

> **Chapter handle:** `ORI-03`.

Your LLM facilitates, researches, and drafts. You own goals, accounts,
approvals, and consequential actions.

The best workflow is selective:

1. Give the agent `02-AI-GROWTH-GUIDE.txt`.
2. Tell it where the user-owned project workspace is located.
3. Ask it to read `STATUS.md` and the artifact for the current section.
4. Work through one major section at a time.
5. Ask one question at a time when your answer affects the design.
6. Save the reviewed result before moving forward.
7. Update `STATUS.md` with the completed section, unresolved facts, and next action.

- **OBSERVED**  -  direct current inspection or provider or system-of-record readback.
- **OWNER-STATED**  -  supplied by you and accepted as the business requirement.
- **RESEARCHED**  -  found in a dated external source with a link.
- **ASSUMPTION**  -  reasonable for planning but not yet verified.
- **UNKNOWN**  -  required information that has not been established.

`RECOMMENDATION` identifies a proposed action; it is not evidence.

> **Credential and privacy note:** do not paste passwords, API keys, private keys, recovery codes, customer records, or unredacted confidential data into prompts or workspace documents. Ask the owner to confirm the approved provider credential area or secret store and use placeholders in project files.

### Master working prompt

Copy and paste this prompt after providing the guide:

```text
Act as my guided AI infrastructure coach and working-document editor.

We will build my AI Growth Workspace one section at a time. Begin by reading
STATUS.md and the current section of the guide. Ask one question at a time when
the answer affects architecture, cost, privacy, authority, or sequence.

For every section:
1. separate OBSERVED, OWNER-STATED, RESEARCHED, ASSUMPTION, and UNKNOWN facts;
2. prefer equipment and services I already have when they satisfy the need;
3. label the smallest proposed stage RECOMMENDATION, not evidence;
4. show the proposed artifact before treating it as final;
5. record accepted decisions and their reasons in DECISIONS.md;
6. put attractive but unnecessary ideas in BACKLOG.md;
7. define a completion check based on evidence;
8. update STATUS.md with progress, blockers, and the next action.

Do not ask me to provide credentials in chat. Ask me to confirm the approved
provider credential area or secret store. Before sending any client-facing SMS,
email, or WhatsApp message, show me the exact final draft and wait for my
explicit approval. For another outbound or public action, show the exact
content, recipient or account, channel, and timing. Apply the same exact-action
approval to purchases, deployments, access changes, deletions, and other
consequential actions.

Start by confirming the workspace location and asking whether a current-state
inventory already exists.
```

### Resume procedure

In a later session, provide the guide, `STATUS.md`, and current artifacts:

```text
Resume this project from STATUS.md. Summarize the last accepted decision, the
current blocker, and the next action in five lines or fewer. Do not reopen
completed decisions unless new evidence conflicts with them.
```

**Produced artifact:** `STATUS.md` containing the working protocol, current section, and next action.

**Completion check**

- The agent can explain the workspace, current section, and evidence labels.
- The agent asks focused questions rather than generating an entire architecture immediately.
- You can end the session and resume from `STATUS.md`.

**Next step:** inventory what you already have.

---
