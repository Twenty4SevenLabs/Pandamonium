# LAYER-TO-COMPONENT-DIAGNOSIS-CARD

## Incident Scope

| Field | Value | Evidence basis | Checked | Owner |
| --- | --- | --- | --- | --- |
| Outcome and expected result |  |  |  |  |
| Target environment |  |  |  |  |
| Symptom and time window |  |  |  |  |
| Affected C-## connection |  |  |  |  |
| Initiator and receiver |  |  |  |  |
| Service / asset / zone IDs |  |  |  |  |
| Approved read-only boundary |  |  |  |  |
| Opaque evidence-reference convention |  |  |  |  |
| Evidence freshness rule |  |  |  |  |

## Diagnostic Bands

| Band | Bounded question | Proof boundary |
| --- | --- | --- |
| Outcome | Did the approved user-visible result reach readback and record? | Not a protocol layer; one test-case pass does not prove general authority, security, capacity, or recovery |
| Application | Did the named service correctly understand and answer? | Does not prove every dependency or future availability |
| Transport | Did the endpoints exchange on the expected transport and receiving port? | Does not prove identity, request validity, or useful response |
| Internet | Did current addressing and route evidence support the destination? | Does not prove end-to-end delivery or a listener |
| Link and media | Did the inspected local interface or segment work? | Does not prove a remote route, transport, or service |

## Diagnosis Rows

| Step ID | Band | C-## / component IDs | Bounded question | Prerequisite | Expected evidence | Supplied actual evidence | Evidence basis / checked | Result | Maximum supported conclusion | Still unproven / open alternatives | Owner | Opaque evidence reference | Smallest permitted next evidence task |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  | `PASS` / `FAIL` / `UNKNOWN` / `NOT RUN` |  |  |  |  |  |

## Owner Review and Readiness

- First failed or unproven band:
- Evidence used:
- Open alternatives:
- Next evidence-task owner:
- Smallest safe evidence task:
- Diagnostic-method review: `PENDING` / `PASS` / `REPAIR`
- Current-topology review: `PENDING` / `PASS` / `REPAIR`
- `READY FOR NET-05: YES` / `READY FOR NET-05: NO`

Only current `OBSERVED` evidence establishes `PASS`. Keep `OWNER-STATED`,
`RESEARCHED`, `INFERENCE`, `ASSUMPTION`, `UNKNOWN`, and `RECOMMENDATION`
distinct. Record Outcome as symptom context, then walk required prerequisites
bottom-up from Link and media toward Application and Outcome. Stop at the first
`FAIL` or consequential `UNKNOWN`; mark dependent higher bands `NOT RUN`.
`READY FOR NET-05: YES` requires confirmed inputs, a reproducible boundary or
all-pass result, a named owner and permitted task, and both reviews at `PASS`.
It does not require repair. This card does not authorize a scan, contact,
restart, deployment, configuration change, or repair.
