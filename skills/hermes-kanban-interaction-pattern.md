---
name: hermes-kanban-interaction-pattern
category: hermes
status: published
version: 1.0.0
confidence: 0.95
tags: [hermes, kanban, workflow, locked, decision]
when_to_use: Before any Hermes Kanban operation to verify workflow decisions and ensure single-board discipline
---

# Hermes Kanban Interaction Pattern — Locked Decision

**Status:** LOCKED (permanent reference)  
**Last Updated:** 2026-09-06  
**Author:** Pandamonium (Panda)

## When to Use
Load this skill BEFORE any Hermes Kanban operation to verify workflow decisions and ensure single-board discipline. This is mandatory for:
- Creating new Kanban cards
- Responding to tagged cards
- Decomposing tasks with Morpheus
- Archiving completed work
- Any board administration

## Procedure

### 1. Verify Single Board Discipline
- Confirm all new cards are created on **Pandamonium Kanban only** (single source of truth)
- No parallel or duplicate boards allowed
- The Pandamonium Kanban is the authoritative task queue for all work

### 2. Confirm Response Pattern
- **Pandamonium (Panda app):** answer cards with `assignee: pandamonium` when Panda implements in-app.
- **Hermes specialists:** answer cards **assigned to your profile** on the `pandamonium` board (e.g. `hermes-bert`). Cards with `created_by: pandamonium` are authoritative work orders from Panda.
- **Morpheus (`default`):** decompose parent cards (`assignee: default`); do not implement.
- Do NOT pick up another specialist's assignee unless Panda or Morpheus explicitly reassigns.

### 3. Select Tool Chain

#### Primary: Hermes MCP Tools
Use these for all Kanban operations when connected:

| Operation | MCP Tool | Required Params |
|-----------|----------|-----------------|
| Create card | `kanban_create` | title, assignee, body |
| Show task | `kanban_show` | task_id |
| Comment | `kanban_comment` | task_id, body |
| Complete | `kanban_complete` | task_id, result, artifacts |
| Block | `kanban_block` | task_id, kind, reason |
| Unblock | `kanban_unblock` | task_id |
| Link | `kanban_link` | parent_id, child_id |
| List | `kanban_list` | assignee, status filters |
| Attach | `kanban_attach` / `kanban_attach_url` | task_id, filename/content or url |
| Request review | `kanban_request_review` | task_id, summary |
| Request changes | `kanban_request_changes` | task_id, reason |

#### Fallback: SSH CLI (for archive, promote, decompose, boards, gateway)
When MCP lacks capability or for admin operations:
```bash
hermes_ssh vm-hermes 'hermes <command>'
```
Common commands:
- `hermes kanban archive t_id1 t_id2 ...`
- `hermes kanban boards switch default`
- `hermes gateway restart`
- `sudo systemctl status hermes-gateway`

### 4. Execute Card Lifecycle

#### Creation
```bash
hermes kanban create --title "Task title" --assignee pandamonium --body "Details..."
```
Via MCP:
```json
kanban_create(title="...", assignee="pandamonium", body="...")
```

#### Execution Steps
1. Read task via `kanban_show` to get full context
2. Check for parent dependencies (`parents` field)
3. Implement or dispatch (to specialists if multi-step/parallel)
4. Comment progress via `kanban_comment`
5. Complete via `kanban_complete` with structured handoff

#### Blocking (Human Intervention)
```bash
hermes kanban block --task-id <id> --kind needs_input --reason "Waiting on X"
```
**NEVER** use `--initial-status blocked`. Always use explicit blocking with kind.

#### Completion
Provide structured handoff:
```json
kanban_complete(
  task_id="<id>",
  result="Final output summary",
  artifacts={"path": "/mnt/dev-env/...", "url": "...", "vmid": "..."},
  created_cards=["t_child1", "t_child2"],
  board="default"
)
```

### 5. Specialist Assignment Rules

#### Named Hermes Specialists (for parallel work)
When dispatching independent tasks:
- Bert, Raj, Stuart, Leonard, Amy, Howard, Penny, etc.
- Leave live assignees in place
- Comment direction changes on existing cards

#### Self-Implementation
- Assign to `pandamonium` (not Hermes profile)
- **NEVER** create Hermes profile named `pandamonium` or `cursor` — dispatcher skips these
- Complete in same session from blocked/ready/running
- Do NOT leave finished cards as "ready"

### 6. Morpheus (default) Special Rules
- **Decomposes ONLY** — creates children, does not implement
- Complete parent immediately after linking children
- Children cannot run while parent is open
- Never decompose cards with existing children or spec paths

### 7. Archive Protocol
```bash
hermes kanban archive t_abc t_def t_ghi
```
- Use `kanban_list --status done` to find archived candidates
- Preserve active specialist trees — do not vacuum

## Pitfalls
- Creating cards on non-Pandamonium boards (violates single-source discipline)
- Answering untagged cards (wastes cycle time)
- Using `--initial-status blocked` instead of explicit blocking with kind
- Leaving finished cards in "ready" state
- Vacuuming live specialist trees when direction changes
- Creating Hermes profiles named `pandamonium` or `cursor`
- Morpheus implementing tasks (should only decompose)

## Verification
Before declaring workflow correct:
- [ ] All new cards on Pandamonium Kanban only
- [ ] Response pattern: answer tagged cards, ignore untagged
- [ ] MCP tools preferred; SSH CLI for admin ops
- [ ] Block kind uses `needs_input` for human park
- [ ] Self-implemented cards assigned to `pandamonium` (not Hermes profile)
- [ ] No live specialist trees vacuumed

## References
- Documentation: `/mnt/dev-env/projects/pandamonium/brain/hermes/HERMES-KANBAN-INTERACTION-PATTERN.md`
- MCP Status: hermes provider connected with full Kanban support
