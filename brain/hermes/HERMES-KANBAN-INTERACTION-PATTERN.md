# Hermes Kanban Interaction Pattern — Locked Decision

**Status:** LOCKED (permanent reference)  
**Last Updated:** 2026-09-06  
**Author:** Pandamonium (Panda)

---

## Core Principles

### 1. Single Source of Truth: Pandamonium Kanban
- **All task creation** happens on the **Pandamonium Kanban board only**
- No parallel or duplicate boards
- The Pandamonium Kanban is the authoritative task queue for all work

### 2. Response Protocol: Tag-Based Activation
- **Pandamonium (Panda app):** answer cards with `assignee: pandamonium` when implementing in-app.
- **Hermes specialists:** execute cards **assigned to your profile** on the `pandamonium` board. Cards with `created_by: pandamonium` are authoritative work orders from Panda.
- **Morpheus (`default`):** decompose parent cards (`assignee: default`); do not implement.
- Do not pick up another specialist's assignee unless Panda or Morpheus explicitly reassigns.

### 3. Tool Chain: MCP + SSH Fallback

#### Primary: Hermes MCP Tools
The updated Hermes MCP provides full Kanban operations:

| Operation | MCP Tool | Notes |
|-----------|----------|-------|
| Create card | `kanban_create` | For new tasks |
| Show task | `kanban_show` | Read full task state |
| Comment | `kanban_comment` | Append durable notes |
| Complete | `kanban_complete` | Mark done with handoff |
| Block | `kanban_block` | Stop work, route WHY |
| Unblock | `kanban_unblock` | Resume when parents ready |
| Link (parent→child) | `kanban_link` | Add dependencies |
| List tasks | `kanban_list` | Filter by assignee/status |
| Attach file | `kanban_attach` / `kanban_attach_url` | File artifacts |
| Request review | `kanban_request_review` | QA/security review |
| Request changes | `kanban_request_changes` | Return with fixes needed |

#### Fallback: SSH CLI (for archive, promote, decompose, boards, gateway)
When MCP lacks capability or for admin operations:
```bash
hermes_ssh vm-hermes 'hermes <command>'
```
Examples:
- `hermes kanban archive t_id1 t_id2 ...`
- `hermes kanban boards switch default`
- `hermes gateway restart`
- `sudo systemctl status hermes-gateway`

### 4. Card Lifecycle Rules

#### Creation
- Always create on Pandamonium Kanban
- Use `kanban_create` with required: title, assignee (pandamonium), body
- Optional: parents (for child tasks), priority, project

#### Execution
1. Read task via `kanban_show` to get full context
2. Check for parent dependencies
3. Implement or dispatch (to specialists if multi-step/parallel)
4. Comment progress via `kanban_comment`
5. Complete via `kanban_complete` with artifacts/results

#### Blocking
- Use `kanban_block` with kind: `dependency`, `waiting_on`, `needs_input`, `stuck`
- Set clear reason for human intervention or routing

#### Completion
- Always provide structured handoff in `kanban_complete`:
  - `result`: final output
  - `artifacts`: paths, URLs, VMIDs
  - `created_cards`: if spawned children
  - `board`: which board this lives on

### 5. Board Locking Decision

**LOCKED:** All interaction patterns apply to **all Kanban boards** under Pandamonium control:
- Default board is primary work queue
- Any custom board follows same creation/response rules
- No deviation unless explicitly approved by Jason

### 6. Specialist Assignment Pattern

#### Named Hermes Specialists (for parallel work)
When dispatching independent tasks:
- Bert, Raj, Stuart, Leonard, Amy, Howard, Penny, etc.
- Leave live assignees in place
- Comment direction changes on existing cards

#### Self-Implementation
- Assign to `pandamonium` (not Hermes profile)
- Never create Hermes profile named `pandamonium` or `cursor`
- Complete in same session from blocked/ready/running
- Do NOT leave finished cards as "ready"

### 7. Morpheus (default) Special Rules

- **Decomposes ONLY** — creates children, does not implement
- Complete parent immediately after linking children
- Children cannot run while parent is open
- Never decompose cards with existing children or spec paths

### 8. Session & Archive Protocol

- Archive completed work: `hermes kanban archive <task_ids>`
- Use `kanban_list --status done` to find archived candidates
- Preserve active specialist trees — do not vacuum

### 9. Human Park Pattern

**NEVER** use `--initial-status blocked` for human park  
**INSTEAD:** Use `hermes kanban block --kind needs_input "<reason>"`

---

## Quick Reference Commands

### List my tasks
```bash
hermes kanban list --assignee pandamonium
# or via MCP: kanban_list(assignee="pandamonium")
```

### Show task details
```bash
hermes kanban show <task_id>
# or via MCP: kanban_show(task_id="<id>")
```

### Comment on task
```bash
hermes kanban comment --task-id <id> --body "Note here"
# or via MCP: kanban_comment(task_id="<id>", body="...")
```

### Complete task
```bash
hermes kanban complete --task-id <id> --result "Done"
# or via MCP: kanban_complete(task_id="<id>", result="...", artifacts={...})
```

### Block task (human intervention)
```bash
hermes kanban block --task-id <id> --kind needs_input --reason "Waiting on X"
# or via MCP: kanban_block(task_id="<id>", kind="needs_input", reason="...")
```

### Archive tasks
```bash
hermes kanban archive t_abc t_def t_ghi
```

---

## Tool Status Matrix (as of 2026-09-06)

| MCP Provider | Status | Kanban Support |
|--------------|--------|----------------|
| hermes | ✅ connected | Full (all 18 tools) |
| mad-mcp-portal | ✅ connected | Discovery/routing only |
| aikido | ❌ error | N/A |
| gitlab | ❌ error | N/A (use glab CLI) |
| prisma-local | ❌ error | N/A |
| prisma-remote | ⚠️ needs_auth | N/A |
| neon | ⚠️ needs_auth | N/A |

**Fallback:** SSH to vm-hermes for any blocked MCP operations.

---

## Verification Checklist

Before declaring workflow locked:
- [ ] All new cards created on Pandamonium Kanban only
- [ ] Response pattern: answer tagged cards, ignore untagged
- [ ] MCP tools preferred; SSH CLI for admin ops
- [ ] Block kind uses `needs_input` for human park (not `--initial-status blocked`)
- [ ] Morpheus decomposes only, completes parent after linking children
- [ ] Self-implemented cards assigned to `pandamonium` (not Hermes profile)
- [ ] No live specialist trees vacuumed on direction changes

---

**This document is LOCKED.** Do not modify unless Jason explicitly requests a workflow change. All decisions herein apply to all Kanban boards under Pandamonium control.
