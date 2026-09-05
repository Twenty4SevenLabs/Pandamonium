# OS System Performance Baseline

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

| Row ID | Metric | Boundary/unit/clock | Workload/version/request mix | Cold/warm/warmup | Duration/sample count/population | Sampling/aggregation/percentile method | Completed/failed/rejected/timeouts | Baseline | Collection overhead | Evidence source/receipt | Freshness/uncertainty | Owner | Maximum conclusion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |

| Row ID | Observed deviation | Constraint candidate | Hypothesis | Competing explanation | Discriminating one-variable test | Test authority | Primary/guardrail metrics | Success condition | Abort/rollback | Evidence | Maximum conclusion | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  |  | `KEEP / REVERT / INVESTIGATE / NOT TESTED` |

Decision precedence: not run or incomparable means `NOT TESTED`; an abort or
guardrail failure means `REVERT`; success with every guardrail passing means
`KEEP`; any other evaluated result means `INVESTIGATE`.
