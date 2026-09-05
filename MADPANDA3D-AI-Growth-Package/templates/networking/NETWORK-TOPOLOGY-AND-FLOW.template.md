# NETWORK-TOPOLOGY-AND-FLOW

## Scope and Control

| Field | Value | Evidence basis | Source / private evidence reference | Checked | Owner |
| --- | --- | --- | --- | --- | --- |
| Outcome |  |  |  |  |  |
| Target environment |  |  |  |  |  |
| Workflow owner |  |  |  |  |  |
| Network-record owner |  |  |  |  |  |
| Approved read-only evidence boundary |  |  |  |  |  |
| Opaque private evidence-reference convention |  |  |  |  |  |

Evidence basis: `OBSERVED`, `OWNER-STATED`, `RESEARCHED`, `INFERENCE`,
`ASSUMPTION`, or `UNKNOWN`. Keep `RECOMMENDATION` separate.

ID legend: preserve accepted `NET-01` asset IDs and `NET-02` `C-##` connection
IDs exactly. Assign `S-##` service, `Z-##` zone, and `D-##` data-category IDs
only where the accepted inputs do not already supply a stable ID.

## Physical View

```text
[Draw sites or controlled locations, inventoried devices and hosts with their
unchanged NET-01 asset IDs, link media, and external ownership boundaries. Do
not invent or assign an asset ID to unknown provider placement.]
```

### Physical text equivalent

[List every node and link in reading order. State location, medium, direction
when material, and external ownership boundary without exposing private values.]

## Logical View

```text
[Draw services inside declared zones or segments. Label every directed edge
with its accepted NET-02 C-## connection ID.]
```

### Logical text equivalent

[List every service, zone, initiator, receiver, and C-## edge in reading order.]

## Data-Flow View

```text
[Draw one approved outcome from trigger through transformation, storage,
approval, external crossing, readback, and record. Label C-## and D-## IDs.]
```

### Data-flow text equivalent

[List each D-## category and C-## crossing in order, including transformations,
retention, approval, external crossing, readback, and record.]

## Node Register

| Node ID | View(s) | Role | Current placement or zone | Owner | Source | Checked | Evidence basis | State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |

## Edge and Data Register

| C-## | Initiator -> receiver | Physical medium or boundary | Logical zones | D-## and classification | Handling / retention / approval | Owner | Source and checked date | Evidence basis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |

## Reconciliation Register

| Issue ID | Affected views / IDs | Conflict or unknown | Blocking? | Owner | Approved read-only evidence task | Expected evidence | State |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | `YES` / `NO` |  |  |  | `OPEN` / `RESOLVED` / `ACCEPTED RISK` |

## Review and Readiness

- Workflow-owner review: `PENDING` / `PASS` / `REPAIR`
- Network-record-owner review: `PENDING` / `PASS` / `REPAIR`
- Evidence used:
- Unresolved blockers:
- Smallest safe next action:
- Next-action owner:
- `READY FOR NET-04: YES` / `READY FOR NET-04: NO`

A mapped line is not proof of reachability, encryption, identity,
authorization, security, health, capacity, or recovery. Keep sensitive values
and raw evidence outside this shareable artifact and use only opaque references.
Do not scan, contact an external party, or make a live change to complete this
artifact.
