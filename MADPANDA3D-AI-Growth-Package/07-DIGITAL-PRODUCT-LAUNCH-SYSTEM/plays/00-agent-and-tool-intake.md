# Play 0 — Agent and Tool Intake

## Objective

Create an honest capability and permission map before asking an agent to research, build, publish, or transact.

## Required inputs

- Human owner's name or role
- Private workspace location
- Tools the human believes are connected
- Accounts or channels that may be in scope
- Budget ceiling, approval rules, prohibited actions, and escalation conditions

## Tool capability needed

- **Needed:** document creation and local/private file storage
- **Helpful:** read-only tool/account discovery
- **Manual fallback:** the human lists available tools and confirms each account; mark every unverified capability as `UNVERIFIED`

## Ordered actions

1. Open this exact file: `plays/00-agent-and-tool-intake.md`. Create the private working folder. For a new workspace, copy `STATUS.template.md`, record the current package version and exact archive SHA-256, set identity to `MATCH`, then copy every editable file from `assets/`. For an existing workspace, run the Playbook resume integrity protocol before changing anything; a blank/mismatched identity or unresolved contradiction stops without workspace mutation. Leave the purchased package unchanged.
2. Ask: “What single business outcome should this launch project produce?”
3. Ask for the budget ceiling. Do not interpret a blank answer as permission to spend.
4. Inventory capabilities by outcome: web research, document creation, file storage, media, storefront, checkout, delivery, support, analytics, and social publishing.
5. For every capability, record whether it is available, tested, account-scoped, read-only or write-capable, and what proof a successful action returns.
6. Record actions that always require approval: spend, publish, send, account/permission changes, real payments/refunds, legal choices, and destructive actions.
7. Record data boundaries: secrets, customer data, private client material, health/financial/legal data, and licensed source material.
8. Write escalation conditions and the human's preferred review cadence.
9. Save `work/00-intake/AGENT-CAPABILITY-MAP.md` and update `STATUS.md`.

## Produced artifact

`AGENT-CAPABILITY-MAP.md` containing:

- one business outcome;
- human and agent roles;
- capability table;
- approved account/destination table;
- budget and approval boundaries;
- data-handling boundaries;
- authoritative-readback expectations;
- escalation conditions;
- known gaps.

## Success criteria

- No tool or account is marked available without evidence or human confirmation.
- Read access and write authority are distinguished.
- A dollar budget ceiling is explicit.
- External writes and real transactions require explicit approval.
- At least one manual fallback exists for every unavailable critical capability.
- The private workspace contains `STATUS.md` and the capability map.

## Stop conditions

- No private workspace can be created.
- The owner requests credential sharing in plain text.
- The requested outcome depends on an unapproved account, unlawful action, deceptive claim, or undefined spending authority.

## Next play

Proceed to Play 1 only after the capability map passes. Otherwise keep Play 0 `BLOCKED` and state the smallest missing owner decision.
