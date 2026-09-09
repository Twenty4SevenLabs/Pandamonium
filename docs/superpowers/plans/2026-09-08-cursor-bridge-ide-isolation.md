---
name: cursor-bridge-ide-isolation
overview: Lock fork compaction (handoff + 15-message tail), ban resume on IDE transcript ids, add fork endpoint and isolation tests.
todos:
  - id: fork-compaction-modules
    content: ide_agent_guard.py + fork_compaction.py with handoff schema and tail limit 15
    status: completed
  - id: wire-bridge-service
    content: fork endpoint, resume/send 409 for IDE ids, compaction on fork, guarded resume
    status: completed
  - id: wire-panda-routes
    content: /api/cursor/agents/{id}/fork, send requires fork, no auto resume→fork
    status: completed
  - id: isolation-tests
    content: fork compaction unit tests + forked send never resumes IDE ids under projects root
    status: in_progress
  - id: bridge-home
    content: PANDAMONIUM_CURSOR_BRIDGE_HOME=data/cursor-bridge/home; drop ~/.cursor rw mount
    status: pending
  - id: sandbox-cwd
    content: Default bridge cwd to dedicated panda-cursor worktree
    status: pending
isProject: false
---

# Cursor bridge IDE isolation — implementation plan

Spec: [2026-09-08-cursor-bridge-ide-isolation-design.md](../specs/2026-09-08-cursor-bridge-ide-isolation-design.md)

## Done this pass

- `services/cursor-bridge/ide_agent_guard.py`
- `services/cursor-bridge/fork_compaction.py`
- `POST /agents/{id}/fork` on sidecar + Panda routes
- Resume/send 409 for unforked IDE transcript ids
- `_resume_sdk_agent` uses `resolve_sdk_resume_id` only

## Next

1. Finish isolation tests and run pytest.
2. Bridge HOME + Docker mount split.
3. UI “Continue in Panda” button → `POST /api/cursor/agents/{id}/fork`.
4. Restart `pandamonium.service`; verify IDE SSH chat unaffected.
