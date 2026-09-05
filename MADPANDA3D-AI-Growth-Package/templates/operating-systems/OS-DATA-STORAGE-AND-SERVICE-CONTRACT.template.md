# OS Data, Storage, Network, and Service Contract

Status: `BLANK / DRAFT / BLOCKED / REVIEWED / ACCEPTED`

## Device and I/O Path

| Operation | Runtime | OS identity/permission | Driver/firmware | Transfer/bus | Device queue/execution | Completion/error | App/buyer result | Timeout/cancel/cleanup | Evidence | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  |

## Storage and Failure Domains

| Data class | Medium/device | Controller/enclosure/power | Redundancy/volume | Encryption/filesystem | App structure | Backup/recovery copy | Shared failure | RPO/RTO | Restore/app validation | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  |

## Filesystem State and Publication

| Artifact | Logical role | Namespace/mount/path | Object identity/metadata | Readers/writers/locks | Version/hash/schema | State | Approval | Promotion/adoption | Rollback/retention | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  | `DRAFT / STAGED / VALIDATED / APPROVED / PROMOTED / OBSERVED / ACCEPTED / REJECTED / ROLLED BACK / UNKNOWN` |  |  |  |  |

## Host-Network Boundary

| Service/process | Namespace | Transport/address/interface/port | Peer and NET edge | Resolver/name | Route/policy | Clock | Readiness/protocol | Data/encryption | Evidence | Maximum conclusion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  |

## Service Lifecycle

| State/transition | Required receipt | Dependency | Timeout/retry | Drain/cancel | Shutdown/grace/force | Children/locks/leases/temp/device work | Restart budget | Rollback/revalidation | Owner/authority | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  |

## Review

- Availability decision:
- Integrity decision:
- Recoverability decision:
- Rebuildability decision:
- First blocker and owner task:
- Technical review: `PASS / REPAIR / BLOCKED`
- Data/recovery review: `PASS / REPAIR / BLOCKED`

