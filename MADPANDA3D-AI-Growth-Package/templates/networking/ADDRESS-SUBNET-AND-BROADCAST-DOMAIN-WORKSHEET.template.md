# ADDRESS-SUBNET-AND-BROADCAST-DOMAIN-WORKSHEET

## Scope Control

| Field | Value | Evidence basis | Checked | Owner |
| --- | --- | --- | --- | --- |
| Environment and outcome |  |  |  |  |
| C-## connection and endpoints |  |  |  |  |
| Physical or virtual placement |  |  |  |  |
| Supplied attachment evidence |  |  |  |  |
| Address-family need |  |  |  |  |
| Endpoint demand and growth horizon |  |  |  |  |
| Allocation authority |  |  |  |  |
| Permitted read-only inspection boundary |  |  |  |  |
| Evidence freshness rule |  |  |  |  |
| Opaque-reference convention |  |  |  |  |
| Private-value boundary |  |  |  |  |

## Link and Broadcast or Multicast Scope

| BD-## | C-## | Endpoints | Attachment type | Broadcast or multicast scope | Evidence state | Opaque reference / checked | Owner | Limit or open question |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | `OBSERVED` / `OWNER-STATED` / `UNKNOWN` / `RECOMMENDATION` |  |  |  |

## Prefix and Subnet Purpose

| PFX-## | BD-## | Family | Purpose and scope | Demand / growth / reservations | Prefix or UNKNOWN | Capacity method | Overlap state | Zone relationship | Evidence state | Owner | Readiness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | IPv4 / IPv6 / dual / UNKNOWN |  |  |  |  | `PASS` / `CONFLICT` / `UNKNOWN` |  |  |  | `PASS` / `REPAIR` / `UNKNOWN` |

## Allocation and Gateway Handoffs

| AH-## | PFX-## | Assignment method or UNKNOWN | Owner | Gateway or no-gateway decision | Later dependency and owner | Evidence state / opaque reference | Limit and smallest next task |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |

## Reviews and Readiness

- Overlap state:
- Blockers:
- Smallest owner-assigned evidence task:
- Address-plan review: `PENDING` / `PASS` / `REPAIR`
- Private-value-boundary review: `PENDING` / `PASS` / `REPAIR`
- `READY FOR NET-06: YES` / `READY FOR NET-06: NO`

Real prefixes, addresses, hostnames, ports, gateways, neighbor records, and
full configurations remain in the approved private register. Use only opaque
references here. Label approved example values `DOCUMENTATION ONLY - NOT
DEPLOYABLE`. Private IPv4 does not prove isolation or authorization. IPv6 does
not use broadcast addresses. `READY FOR NET-06: YES` requires a confirmed
connection; current `OBSERVED` or `OWNER-STATED` attachment with an owner;
every prefix's purpose, family, capacity basis, readiness, and overlap at
`PASS`; every allocation and gateway decision or later handoff explicitly
owned; fresh evidence; a private-value boundary; and both reviews at `PASS`.
Any other state makes readiness `NO`. `UNKNOWN` or `CONFLICT` overlap also makes
Address-plan review `REPAIR`. Readiness does not authorize action.
