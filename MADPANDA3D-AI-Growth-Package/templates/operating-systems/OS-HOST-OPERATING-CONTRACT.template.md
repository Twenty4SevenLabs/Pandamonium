# OS Host Operating Contract

Status: `BLANK / DRAFT / BLOCKED / REVIEWED / ACCEPTED`

## Declared Scope and Evidence

| Field | Value |
| --- | --- |
| Workload and buyer outcome |  |
| Host/platform/runtime and environment |  |
| Evidence mode | `FICTIONAL / SUPPLIED READ-ONLY / ISOLATED EXECUTED / PREPRODUCTION EXECUTED / PRODUCTION EXECUTED` |
| Evidence window and maximum age |  |
| Planning/observation/change authority |  |
| All known blockers |  |
| One current owner task |  |
| Next review date and reopen triggers |  |

## Contract Boundary

| Field | Value |
| --- | --- |
| Workload and buyer outcome |  |
| Host/platform/runtime |  |
| Accountable owner |  |
| Planning authority |  |
| Observation authority |  |
| Change authority |  |
| Safe evidence location |  |
| Checked date and maximum age |  |

## Responsibility Map

| Dependency | Human | Agent/application | Runtime | OS | Hardware | External | Owner | State | Evidence | Maximum conclusion | Next proof |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  | `PRESENT / AVAILABLE / PROVEN / UNKNOWN` plus `CONFIGURED / ALLOCATED / PRESSURED` facets |  |  |  |

## Identity and Privilege

| Row ID | Actor/action | Actor owner | Resource | Purpose | Identity class | Enforcement boundary | Required | Technical state | Business authority | Expiry | Review/revoke owner | Evidence | Decision | Next proof |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  | `YES / NO / UNKNOWN` |  |  |  |  |  | `PROVEN AND OWNER APPROVED / NOT REQUIRED / OWNER BLOCKED / TECHNICALLY NOT PROVEN / EXPIRED / UNKNOWN` |  |

## Process, Worker, Queue, Service, and Outcome State

| Row | Layer | Safe ID | Parent/supervisor | State | Receipt/time | Max age | Timeout/cancel | Exit/cleanup/orphan | Owner | Maximum conclusion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | `JOB / PROCESS / WORKER / SERVICE / OUTCOME` |  |  |  |  |  |  |  |  |  |

## CPU, Scheduling, and Memory

| Workload/phase | Class | Arrivals/queue | Runnable/running/blocked | Latency/throughput/outcome | Host installed/reserved/committed/resident/available/peak | Device memory | Pressure/fault/swap | Guardrail | Evidence | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | `INTERACTIVE / BATCH / DEADLINE / BACKGROUND / CONTROL` |  |  |  |  |  |  |  |  |  |

## Concurrency and Liveness

| Object/resource | Scope | Readers/writers | Atomic action | Ordering/coordination | Idempotency | Timeout/cancel/crash | Wait/owner edges | Liveness class | Authority | Next proof |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | `PROCESS / HOST / DISTRIBUTED` |  |  |  |  |  |  | `RACE RISK / DEADLOCK / LIVELOCK / STARVATION / SLOW OR BLOCKED / UNKNOWN` |  |  |

## Review

- First blocker:
- Preserved independent evidence:
- One current owner task:
- Deferred items:
- Technical review: `PASS / REPAIR / BLOCKED`
- Owner review: `PASS / REPAIR / BLOCKED`
