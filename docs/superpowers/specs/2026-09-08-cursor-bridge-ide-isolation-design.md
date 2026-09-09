# Cursor bridge IDE isolation — fork compaction (locked)

**Status:** Locked for implementation on `cursor-bridge`  
**Date:** 2026-09-08  
**Reverses:** `2026-09-06-cursor-agent-fullscreen-chat-design.md` § “IDE agents continue via `resume_agent`”

## Problem

Panda and the Windows Remote-SSH Cursor IDE share the same Linux identity (`HOME=/home/labsadmin`, rw `~/.cursor`). Calling `resume_agent` on IDE transcript UUIDs collides with IDE checkpoints and broke IDE chat (Sep 6–7).

## Decision

| Boundary | Behavior |
|---|---|
| IDE transcript agents | **Read-only** in Panda until explicit fork |
| Fork (“Continue in Panda”) | `create_agent` + compaction handoff; **never** `resume_agent(ide_uuid)` |
| After fork | `resume_agent` only on **Panda-owned** `sdk_agent_id` |
| Send without fork | HTTP **409** `ide_fork_required` |
| Resume on IDE uuid | HTTP **409** `ide_fork_required` |

## Fork compaction contract

On `POST /agents/{ide_agent_id}/fork`:

1. **Create** a new SDK local agent (`create_agent`) in the Panda sandbox cwd.
2. Run **one Composer turn** with `build_handoff_user_prompt(transcript)`; parse JSON handoff:
   - `goal` (string)
   - `files` (string[])
   - `next_steps` (string[])
   - `summary` (string)
3. Store registry row:
   - `forked: true`
   - `sdk_agent_id` = new local agent id
   - `ide_source_id` = original IDE transcript uuid (when detectable)
   - `handoff` = parsed object
   - `pending_context` = `[system_handoff_message] + tail(last 15 messages)`
4. Tail limit constant: `FORK_TAIL_MESSAGE_LIMIT = 15`.

### Handoff system message shape

First `pending_context` entry is an assistant message with text from `format_handoff_system_message(handoff)` (goal, summary, files, next steps).

### Send after fork

- First send may inline `pending_context` into the user prompt (existing behavior), then clear `pending_context`.
- `_resume_sdk_agent` resolves via `resolve_sdk_resume_id` → always `sdk_agent_id` for forked rows.

## IDE id guard

`is_ide_transcript_agent_id(agent_id)` is true when:

- `agent_id` matches UUID format, and
- A file exists at `{projects_root}/**/agent-transcripts/**/{agent_id}.jsonl`

Default `projects_root`: `/home/labsadmin/.cursor/projects`  
Override: `PANDAMONIUM_PC_CURSOR_PROJECTS_ROOT`

`resolve_sdk_resume_id` **raises** `IdeAgentResumeForbidden` if asked to resume a bare IDE transcript id.

## HTTP surface

| Route | IDE uuid (unforked) | Forked row |
|---|---|---|
| `GET …/session` | IDE mirror read-only | Bridge registry + merged messages |
| `POST …/fork` | Creates fork + compaction | `already_forked: true` |
| `POST …/resume` | **409** | Resumes `sdk_agent_id` only |
| `POST …/send` | **409** (no registry / not forked) | Normal send |

Panda app route mirrors sidecar: `POST /api/cursor/agents/{id}/fork`.

## Out of scope (follow-up cards)

- Dedicated bridge `HOME` (`data/cursor-bridge/home`)
- Drop rw `~/.cursor` Docker mount
- Sandbox git worktree default cwd
- `setting_sources: []` + inline MCP snapshot
- Disable canvas relay / agent-exec patching

## Tests (required)

1. `fork_compaction`: tail 15, handoff parse, `pending_context` shape.
2. `ide_agent_guard`: detects transcript ids under fake projects tree; forbids IDE resume.
3. **Forked send path**: mock SDK client; assert `resume_agent` is **never** called with any id discoverable under projects root; only `sdk_agent_id` after fork.
4. Routes: send without fork → 409; explicit fork → send OK.

## Verification

```bash
cd /mnt/dev-env/projects/pandamonium
pytest tests/test_cursor_bridge_fork_compaction.py tests/test_cursor_bridge_ide_isolation.py -q
```
