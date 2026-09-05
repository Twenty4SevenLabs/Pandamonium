# OS Service Lifecycle and Termination Contract

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

## Owners

| Service owner | Startup owner | Shutdown owner | Recovery owner | Acceptance owner |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

| Service/generation | Host/platform/supervisor/version | Identity | Start policy | Required capability/dependency class | Startup order/timeout/failure | Readiness probe | Liveness probe | Evidence clock/window | Restart budget | Buyer acceptance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  | `HARD / DEGRADED / OPTIONAL / DEFERRED` |  |  |  |  |  |  |

## State and Probe Ledger

| Row ID | State/transition | Receipt/source/time | Process existence | Readiness | Liveness | Dependency readiness | Buyer acceptance | Maximum conclusion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | `PASS / FAIL / UNKNOWN / NOT PROVEN / BLOCKED / NOT RUN` | `PASS / FAIL / UNKNOWN / NOT PROVEN / BLOCKED / NOT RUN` | `PASS / FAIL / UNKNOWN / NOT PROVEN / BLOCKED / NOT RUN` | `PASS / FAIL / UNKNOWN / NOT PROVEN / BLOCKED / NOT RUN` | `PASS / FAIL / UNKNOWN / NOT PROVEN / BLOCKED / NOT RUN` |  |

| Transition | Admission/drain | Accepted work disposition | Cancel/checkpoint | Children/locks/leases/temp/listeners/device work | Grace/force boundary | Evidence preservation | Recovery/rollback/revalidation | Authority | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  | `PASS / FAIL / UNKNOWN / NOT PROVEN / BLOCKED / NOT RUN` |
