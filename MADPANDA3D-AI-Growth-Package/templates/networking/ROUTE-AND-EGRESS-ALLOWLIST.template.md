# ROUTE-AND-EGRESS-ALLOWLIST

## Scope Control

| Field | Value | Evidence basis | Checked | Owner |
| --- | --- | --- | --- | --- |
| Environment, outcome, and C-## |  |  |  |  |
| Source workload and destination service role |  |  |  |  |
| Direction and address family |  |  |  |  |
| Data class and minimum necessary fields |  |  |  |  |
| Controlled boundary order |  |  |  |  |
| Translation applicability / reason |  |  |  |  |
| Return-path scope |  |  |  |  |
| Evidence location and freshness rule |  |  |  |  |
| Authority and prohibited actions |  |  |  |  |
| Retention, expiry, and review trigger |  |  |  |  |
| Opaque-reference and private-value boundary |  |  |  |  |
| Route-evidence and Egress-policy review owners |  |  |  |  |

## Boundary Order

| BND-## | Order | Boundary role | Control / contract owner | Entry evidence expected | Supplied evidence / class / checked | Opaque reference | Inspection boundary | State | Maximum conclusion | Still unproven | Task or defer reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  | `PASS` / `FAIL` / `UNKNOWN` / `NOT REQUIRED` / `NOT RUN` |  |  |  |

## Route Decisions

| RTE-## | Order | C-## / BND-## | Source and destination classes | Address family | Route class | Selected next boundary / gateway reference | Evidence / class / checked | Owner | Return-path owner / evidence | Prerequisite IDs | State | Maximum conclusion | Still unproven | Task or defer reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | Connected / more-specific / default / policy-selected / provider-managed / `UNKNOWN` |  |  |  |  |  | `PASS` / `FAIL` / `UNKNOWN` / `NOT REQUIRED` / `NOT RUN` |  |  |  |

## Translation Boundaries

| XLT-## | Order | C-## / BND-## | Direction / family | Opaque pre-tuple reference | Opaque post-tuple reference | Translation type | State owner | Evidence / class / checked | Lifetime / expiry | Return association | Prerequisite IDs | State | Maximum conclusion / still unproven | Task or defer reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  | Address / port / both / provider-managed / `UNKNOWN` |  |  |  |  |  | `PASS` / `FAIL` / `UNKNOWN` / `NOT REQUIRED` / `NOT RUN` |  |  |

## Transport and Application Flow

| FLW-## | Order | C-## | Transport protocol | Opaque port reference | Registry source / checked | Source / destination identity references | Listener / application / identity / authentication / authorization evidence | Evidence classes / checked times | Owner | Prerequisite IDs | State | Maximum conclusion | Still unproven | Task or defer reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  | `PASS` / `FAIL` / `UNKNOWN` / `NOT REQUIRED` / `NOT RUN` |  |  |  |

## Egress Allowlist Decisions

| EGR-## | Order | C-## / purpose | Source workload identity | Destination service identity | BND / RTE / XLT / FLW prerequisites | Data class / minimum fields | Authentication mechanism | Authorization decision / owner | Encryption requirement | Retention / expiry / review trigger | Prohibited uses | Evidence / class / checked | State | Maximum conclusion | Still unproven / blockers | First task or defer reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  | `PASS` / `FAIL` / `UNKNOWN` / `NOT REQUIRED` / `NOT RUN` |  |  |  |

## Reviews and Readiness

- First failed or unknown required row:
- Dependent rows marked `NOT RUN`:
- Independent supplied-evidence rows preserved and evaluated:
- First next-action row and owner task:
- Later blockers and defer reasons:
- Route-evidence review owner:
- Route-evidence review: `PENDING` / `PASS` / `REPAIR`
- Egress-policy review owner:
- Egress-policy review: `PENDING` / `PASS` / `REPAIR`
- `READY FOR NET-08: YES` / `READY FOR NET-08: NO`

Only current `OBSERVED` evidence meeting the declared proof rule establishes
`PASS`. A public registry can establish a `RESEARCHED` convention, not live
behavior. `NOT REQUIRED` needs a reason and owner. Evaluate rows in declared
order. At the first failed or unknown prerequisite, mark only transitive
dependents `NOT RUN`, preserve and evaluate independent supplied evidence,
assign one task to the earliest required blocker, and defer later blockers.

`READY FOR NET-08: YES` requires every required `BND-##`, `RTE-##`, `XLT-##`,
`FLW-##`, and `EGR-##` at `PASS`; justified `NOT REQUIRED` rows; current
evidence and owners; explicit return-path scope; private values excluded; complete identity,
authentication, authorization, data, retention, expiry, and review controls;
and both reviews at `PASS`. Any required `FAIL`, `UNKNOWN`, or `NOT RUN`, stale
evidence, unsupported conclusion, unresolved conflict, missing owner, or
unjustified omission makes readiness `NO`. This artifact does not authorize a
query, trace, scan, connection, disclosure, route or firewall change, allow
rule, restart, purchase, or other external action.
