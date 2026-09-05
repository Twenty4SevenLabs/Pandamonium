# CAPTURE-CHECK-RESPOND-RECORD

## Scope Control

| Field | Value | Evidence basis | Checked | Owner |
| --- | --- | --- | --- | --- |
| Outcome and response mode |  |  |  |  |
| Requester, accountable owner, and recipient |  |  |  |  |
| In-scope sources and reading order |  |  |  |  |
| Current authority and prohibited actions |  |  |  |  |
| Decision consequence and urgency |  |  |  |  |
| Freshness and conflict rule |  |  |  |  |
| Private-data and minimum-necessary boundary |  |  |  |  |
| Retention, expiry, and handover target |  |  |  |  |

## Capture Register

| CAP-## | Safe source reference | Evidence class | Speaker / source owner | Requested outcome or response mode | Decision-critical fact, constraint, exact value, or preference | Consequence if wrong or omitted | Received / checked | Freshness / expiry | Private-data handling | State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | `OBSERVED` / `OWNER-STATED` / `RESEARCHED` / `INFERENCE` / `ASSUMPTION` / `UNKNOWN` |  |  |  |  |  |  |  | `CAPTURED` / `SUPERSEDED` / `CONFLICT` / `UNKNOWN` / `EXPIRED` |

## Context State

| CTX-## | Class | CAP-## or CHK-## references | Current statement | Owner | Checked | Carry forward / expiry | Conflict or privacy note |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  | Accepted fact / constraint / decision / open question / deferred / out of scope / conflict |  |  |  |  |  |  |

## Clarification Checks

| CHK-## | CAP-## references | Neutral restatement | Interpretation or exact unknown | Decision impact | One necessary question | Permitted answer source / owner | Answer and evidence class | Answered / checked | Resolution | Updated CTX references |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  | `RESOLVED` / `NOT REQUIRED` / `OPEN` / `BLOCKED` |  |

## Response Plan

| RSP-## | Response mode | CAP / CHK / CTX references | Proposed output or next action | Authority basis | Protected constraints and exact values | Unresolved blockers | Owner | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Inform / Decide / Draft / Troubleshoot / Reflect / Handoff / `UNKNOWN` |  |  |  |  |  |  | `READY` / `REPAIR` / `BLOCKED` |

## Reviews and Readiness

- Last confirmed decision and source:
- Open decision-critical checks:
- Conflicts and governing source:
- Deferred and out-of-scope items:
- Smallest owner-assigned clarification task:
- Context-integrity review: `PENDING` / `PASS` / `REPAIR`
- Action-readiness review: `PENDING` / `PASS` / `REPAIR`
- `READY FOR COM-07: YES` / `READY FOR COM-07: NO`

`READY FOR COM-07: YES` requires every decision-critical input captured with a
source and evidence class; every required `CHK-##` at `RESOLVED` or justified
`NOT REQUIRED`; conflicts reconciled through the named governing source;
freshness, authority, retention, expiry, private-data, and handover controls complete; every
required `RSP-##` at `READY`; and both reviews at `PASS`. Any decision-critical
`UNKNOWN`, `OPEN`, `BLOCKED`, or `REPAIR` state, expired item, conflict,
missing owner, or unsupported authority makes readiness `NO`. This record does not prove a
person was understood and does not authorize contact, delivery, publication,
configuration, purchase, deletion, or any other external action.
