# OS Isolation, Platform, Performance, and Operations Decision

Status: `BLANK / DRAFT / BLOCKED / REVIEWED / ACCEPTED`

## Isolation Decision

| Pattern | Data/identity boundary | Shared kernel/device/control plane | Resource enforcement proof | Storage/network | Provenance/patch | Failure/cleanup | Restore/portability | Skill/cost | Decision/limits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Direct process |  |  |  |  |  |  |  |  |  |
| Supervised service |  |  |  |  |  |  |  |  |  |
| Container |  |  |  |  |  |  |  |  |  |
| Virtual machine |  |  |  |  |  |  |  |  |  |
| Separate host |  |  |  |  |  |  |  |  |  |
| External provider |  |  |  |  |  |  |  |  |  |

## Platform Fit

| Candidate/version/support | Hardware/accelerator | Runtime/app | Processes/services | Memory/device | Files/storage/restore | Identity/network/isolation | Patch/observability/recovery | Skill/cost/migration | Hard-gate result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  | `REQUIRED PASS / SUPPORTED WITH LIMIT / NOT PROVEN / FAIL / N/A` |

## Performance Baseline and Feedback Loop

| Metric | Workload/boundary | Unit/clock/window/method | Baseline | Proposed one-variable test | Guardrails | Collection impact | Success/abort/rollback | Evidence | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  | `KEEP / REVERT / INVESTIGATE / NOT TESTED` |

## Maintenance and Recovery

| Gate | Required record | Owner | Evidence/freshness | Authority | Result/blocker |
| --- | --- | --- | --- | --- | --- |
| inventory and support |  |  |  |  |  |
| advisory/need/applicability |  |  |  |  |  |
| backup/restore/rollback/evidence preservation |  |  |  |  |  |
| approved implementation scope |  |  |  |  |  |
| technical/service/security/performance/buyer validation |  |  |  |  |  |
| failed-change and incident handoff |  |  |  |  |  |
| residual risk and return-to-service acceptance |  |  |  |  |  |

## Decision

- Selected placement/platform:
- Scope and limitations:
- First blocker and owner task:
- Technical review: `PASS / REPAIR / BLOCKED`
- Security/recovery review: `PASS / REPAIR / BLOCKED`

