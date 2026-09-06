# Twenty4SevenLabs / labs247 Pandamonium overlay changelog

Canonical fork: **https://github.com/Twenty4SevenLabs/Pandamonium**

This document inventories every change applied to Pandamonium since the original
safe-repo ingest of upstream `MADPANDA3D/Pandamonium` at **v1.0.5** (`d287b663`).

| Metric | Value |
|--------|-------|
| Baseline | Pandamonium v1.0.5 (`d287b663`) |
| Current `APP_VERSION` | 1.0.11 (`src/constants.py`) |
| Fork HEAD (at authoring) | `8546c83b` |
| Files touched vs baseline | 319 (200 added, 119 modified) |
| Lines vs baseline | +61,806 / −2,057 |

Runtime secrets, MCP connection JSON in `data/settings.json`, SSH private keys,
and other `data/` artifacts are **gitignored** and documented here only by
reference — they are not part of this repository.

---

## Commit timeline (labs247 + fork integration)

| Commit | Summary |
|--------|---------|
| `48b3553b` | Safe-repo ingest of MADPANDA3D/Pandamonium; pin Python deps; gitleaks allowlists; Dependabot cooldown; GitLab `labs247/pandamonium` origin |
| `ec9667b0` | labs247 overlay on v1.0.5: Unsloth fleet wiring, Proxmox host compose, GitHub update helper, overlay path preservation |
| `7c11bad2` | GitLab forge migration (Gitea → GitLab); `import_cursor_opencode_bundle.py` for Cursor/OpenCode personality import |
| `38a7cf9f` | Voice Orb live-call STT/TTS: local Whisper, Chatterbox TTS, barge-in RMS, AEC-off capture, spoken clock expansion, listen-turn policy |
| `35b66733` | Ship full MADPANDA3D AI Growth Package (PDF, guides, templates, launch system) |
| `f1fc597e` | Hermes Kanban MCP, MCP manager hardening, SSH cookbook, voice echo/barge, DuckDuckGo MCP design, imported MCP fixes |
| `a67ce767`… | Upstream MADPANDA3D v1.0.6–v1.0.11 (authority protocol v2, worker routing, selector catalog, release updater, platform truth rules) |
| `8546c83b` | Merge Twenty4SevenLabs fork `main` with full labs247 overlay |

---

## 1. Cluster LLM — Unsloth fleet integration

**New modules**

- `src/unsloth_client.py` — Fleet scanner and OpenAI-compatible client for LAN M1/M2
  and Tailscale Unsloth Studios (`192.168.1.2`, `192.168.1.181`, `192.168.1.191`,
  `100.80.146.51`, etc.); wake URL support; model discovery across hosts.
- `src/unsloth_endpoints.py` — Endpoint registration helpers for settings/UI.
- `tests/test_unsloth_client.py`, `tests/test_unsloth_endpoints.py` — Fleet scan,
  failover, and endpoint resolution tests.

**Modified**

- `src/llm_core.py` — Route chat completions through Unsloth fleet when configured.
- `src/model_discovery.py` — Discover models on all configured Unsloth hosts.
- `src/endpoint_resolver.py` — Resolve default chat endpoint from fleet.
- `routes/model_routes.py` — Expose fleet-discovered models in API.
- `.env.example` — `UNSLOTH_*`, `LLM_HOSTS`, `PANDAMONIUM_UNSLOTH_WAKE_URL` blocks.

---

## 2. Voice Orb — live call STT/TTS and listen policy

**Backend**

- `routes/voice_routes.py` — Voice session bridge to agent loop; Chatterbox/Unsloth
  chat model guard (never send FLUX/image models to voice brain); spoken-text policy
  handoffs for files and worker results; streaming speech gating.
- `routes/stt_routes.py`, `routes/tts_routes.py` — Local Whisper STT and Chatterbox
  WAV TTS endpoints.
- `services/stt/stt_service.py` — Faster-Whisper local transcription; persistent
  model cache under `data/`.
- `services/tts/tts_service.py` — Chatterbox OpenAI-compatible speech synthesis.
- `src/voice_pcm.py` — `expand_spoken_clocks()` rewrites `2:51` → "two fifty-one"
  for TTS; `result_speech()` word-threshold handoff contract (merged with upstream).

**Frontend**

- `static/js/jarvisVoice.js` — Major rewrite: live-call capture, barge-in energy
  threshold, echo cancellation off for headset, turn timers, Chatterbox playback
  queue, voice target selection, worker handoff events, unlock capture/sphere audio.
- `static/js/voiceMeterProcessor.js` — RMS metering for barge-in (sample count fix).
- `static/vendor/organic-sphere/` — Jarvis fullscreen orb assets updated.
- `static/index.html`, `static/sw.js` — Cache-bust versions; voice script loading.

**Tests & specs**

- `tests/test_barge_energy.js`, `tests/test_chatterbox_endpoint_tts.py`
- `tests/test_voice_pcm_stream.py`, `tests/test_voice_session_chat_bridge.py`
- `tests/test_jarvis_voice_chunks.js`, `tests/test_voice_orb.js`
- `tests/browser/voice-orb.spec.js`
- `docs/superpowers/specs/2026-09-05-voice-listen-cutoff-design.md`
- `docs/superpowers/specs/2026-09-05-tts-clock-pronunciation-design.md`
- `docs/superpowers/plans/2026-09-05-voice-listen-cutoff.md`
- `docs/superpowers/plans/2026-09-05-tts-clock-pronunciation.md`
- `docs/superpowers/plans/2026-09-06-voice-tts-echo-barge.md`

---

## 3. Hermes Kanban MCP and vm-hermes SSH control

**New modules**

- `src/hermes_kanban_cli.py` — Builds correct `hermes kanban` CLI syntax; fixes
  model mistake `create --title` → positional title; default board `pandamonium`;
  actions: list, show, create, complete, archive, comment, block, boards_list,
  dispatch, raw.
- `src/agent_tools/hermes_kanban_tool.py` — Native `hermes_kanban` agent tool.
- `src/ssh_cookbook.py` — Agent SSH layout: `data/ssh/config`, `data/bin/ssh`
  wrapper, `vm-hermes` / `192.168.1.192` as `openclaw1`, cookbook key at
  `/app/.ssh/id_ed25519`, `HERMES_KANBAN_BOARD=pandamonium` auto-export.
- `brain/hermes/HERMES-KANBAN-INTERACTION-PATTERN.md` — Orchestrator playbook.
- `skills/hermes-kanban-interaction-pattern.md` — Agent skill mirror.
- `scripts/_rebuild_panda_mcp_env.sh` — Rebuild MCP venv/npm env inside container.
- `tests/test_hermes_kanban_cli.py`, `tests/test_ssh_cookbook.py`

**MCP manager (`src/mcp_manager.py`)**

- `_expand_env_placeholders()` — Resolve `${VAR}` in MCP server env from process env.
- `_http_headers_from_env()`, `_mcp_connect_kwargs()` — HTTP MCP bearer/header routing.
- `_format_mcp_connection_error()` — Actionable hints (Playwright install, Aikido
  API key, Hermes SSH `hermes_tools_mcp_server` vs `hermes mcp serve`).
- `ensure_connected()` / `call_tool()` auto-reconnect for Hermes stdio MCP after crash.
- Hermes MCP catalog: SSH to `openclaw1@192.168.1.192` with `-i /app/.ssh/id_ed25519`,
  remote `python -m agent.transports.hermes_tools_mcp_server` (14 `kanban_*` tools).
- Separate `hermes-messaging` MCP: `hermes mcp serve` for conversations/messages.

**Agent loop & tools**

- `src/agent_loop.py` — `hermes` domain rules (three control paths: MCP →
  `hermes_kanban` → `hermes_ssh`); tool RAG seeds for Kanban intents.
- `src/tool_schemas.py` — `hermes_ssh` and `hermes_kanban` function schemas.
- `src/agent_tools/subprocess_tools.py` — `hermes_ssh` execution via ssh cookbook.
- `src/agent_tools/__init__.py`, `src/agent_tools/admin_tools.py` — Tool registration.
- `src/tool_index.py`, `src/tool_parsing.py`, `src/tool_policy.py`, `src/tool_security.py`
- `src/tool_execution.py` — Dispatch for new tools.
- `src/authority_protocol.py` — MCP kanban readonly/write classification;
  `hermes_ssh`/`hermes_kanban` as `reversible_write`; merged upstream action-effect v2.
- `routes/mcp_routes.py` — MCP route adjustments for imported servers.

**Import & env**

- `scripts/import_cursor_opencode_bundle.py` — Import Cursor/OpenCode bundle;
  Hermes MCP server definitions; GitLab/GitHub/Context7 API key placeholders.
- `.env.example` — `GITHUB_TOKEN`, `GITLAB_TOKEN`, `GITLAB_API_URL`, MCP API keys,
  `PANDAMONIUM_HERMES_TOKEN_FILE`, worker workspace JSON examples.

**Specs**

- `docs/superpowers/specs/2026-09-06-hermes-mcp-kanban-design.md`
- `docs/superpowers/specs/2026-09-05-imported-mcp-servers-fix-design.md`
- `docs/superpowers/specs/2026-09-06-duckduckgo-mcp-design.md`

---

## 4. Cursor / OpenCode migration and slash commands

- `scripts/import_cursor_opencode_bundle.py` — Skills, agents, MCP defs, memory import
  from `~/.config/opencode` into Pandamonium `data/`.
- `scripts/patch_slash_commands.py` — Patch slash command registry.
- `tests/test_cursor_opencode_import.py` — Import regression tests.
- `docs/superpowers/specs/2026-09-04-cursor-pandamonium-migration-design.md`

---

## 5. Deploy, Docker, and Proxmox host overlay

**New**

- `deploy/systemd/pandamonium.service` — systemd unit for native Linux install.
- `deploy/systemd/pandamonium-tailscale-serve.sh` — Tailscale serve helper.
- `deploy/update-from-github.sh` — Pull upstream with overlay preservation.
- `deploy/overlay-paths.txt` — Tracked paths restored after `git reset --hard`.
- `docker/host-proxmox.yml` — Proxmox host-side compose overlay.

**Modified**

- `docker-compose.yml` — SSH key bind mount (`data/ssh` → `/app/.ssh`), Unsloth env,
  Chatterbox/STT volume paths, Hermes network reachability.
- `setup.py` — Calls `ensure_ssh_cookbook()` on setup.
- `app.py` — Startup hooks for SSH cookbook and overlay wiring.

---

## 6. MADPANDA3D AI Growth Package (bundled content)

Entire `MADPANDA3D-AI-Growth-Package/` tree added (~150 files):

- `01-AI-GROWTH-GUIDE.pdf`, `02-AI-GROWTH-GUIDE.txt`
- `guide/` chapters 00–92 (orientation, foundation, networking, OS, infra,
  communication, agents-mcp, business, appendices)
- `07-DIGITAL-PRODUCT-LAUNCH-SYSTEM/` playbook, plays 00–08, assets, templates
- `06-BUYER-WORKSPACE/` ticket scaffolding and workspace docs
- `modules/*.json`, `templates/`, `MANIFEST.json`, `SHA256SUMS.txt`, `PROVENANCE.md`

---

## 7. Upstream MADPANDA3D v1.0.6–v1.0.11 (merged at `8546c83b`)

Integrated from `MADPANDA3D/Pandamonium` without dropping labs247 overlay:

| Version | Highlights |
|---------|------------|
| v1.0.6 | Grounded tool routing protocol restore |
| v1.0.7 | Installation-owned worker labels |
| v1.0.8 | Adaptive approvals and concise voice handoffs |
| v1.0.9 | Authority consent unification text+voice; capability contracts |
| v1.0.10–11 | New chat immediacy; MAD-802 acceptance; governed identity lifecycle; atomic native updates; selector catalog API; `codexWorkspace.js`; release artifact workflow |

**Notable upstream files now in fork**

- `src/authority_protocol.py` — Eight action effects, separate gates, workspace boundary
- `src/selector_catalog.py`, `src/action_intents.py`, `src/worker_routing.py`
- `src/release_updater.py`, `src/update_status.py`, `src/operational_protocol.py`
- `static/js/codexWorkspace.js`, `static/js/updater.js`, `static/js/marketplace.js`
- `routes/chatgpt_subscription_routes.py`, `routes/extension_routes.py`
- `.github/workflows/release-artifact.yml`
- Extensive browser acceptance tests under `tests/browser/`

---

## 8. Tests added or expanded (labs247-relevant)

| File | Coverage |
|------|----------|
| `tests/test_hermes_kanban_cli.py` | CLI command builder, `--title` normalization |
| `tests/test_ssh_cookbook.py` | SSH config generation, wrapper, Hermes host |
| `tests/test_mcp_manager.py` | Env placeholders, HTTP headers, Hermes/Aikido/Playwright errors |
| `tests/test_authority_protocol.py` | Hermes MCP effect classification |
| `tests/test_unsloth_client.py` | Fleet scan and endpoint selection |
| `tests/test_chatterbox_endpoint_tts.py` | Chatterbox TTS route |
| `tests/test_barge_energy.js` | Voice barge-in RMS threshold |
| `tests/test_voice_pcm_stream.py` | Clock expansion + speech handoff contract |
| `tests/test_voice_session_chat_bridge.py` | Voice chat model guard + speech policy |
| `tests/test_cursor_opencode_import.py` | OpenCode bundle import |

---

## 9. Complete file inventory (319 paths vs v1.0.5 baseline)

See git: `git diff --name-status d287b663..HEAD`

```
.env.example
.github/workflows/ci.yml
.github/workflows/release-artifact.yml
.gitignore
MADPANDA3D-AI-Growth-Package/ (entire tree — 150+ files)
README.md
THREAT_MODEL.md
app.py
brain/hermes/HERMES-KANBAN-INTERACTION-PATTERN.md
deploy/overlay-paths.txt
deploy/systemd/pandamonium.service
deploy/systemd/pandamonium-tailscale-serve.sh
deploy/update-from-github.sh
docker-compose.yml
docker/host-proxmox.yml
docs/LABS247-OVERLAY-CHANGELOG.md
docs/superpowers/plans/*.md (4 files)
docs/superpowers/specs/*.md (6 files)
requirements.txt
routes/*.py (agent_task, auth, chat, chatgpt_subscription, extension, mcp, model, session, stt, tts, voice, research)
scripts/_rebuild_panda_mcp_env.sh
scripts/build_release_artifact.py
scripts/import_cursor_opencode_bundle.py
scripts/pandamonium
scripts/pandamonium-backup
scripts/pandamonium-update
scripts/patch_slash_commands.py
services/stt/stt_service.py
services/tts/tts_service.py
setup.py
skills/hermes-kanban-interaction-pattern.md
src/*.py (40+ modules — see section 1–7 above)
static/* (app.js, index.html, js/*, style.css, sw.js, vendor/organic-sphere/*)
tests/* (50+ test modules including browser/ and deployed/)
```

Run `git diff --name-status d287b663..HEAD` for the authoritative per-file A/M/D list.

---

## 10. Operational notes

- **Canonical remote:** `origin` → `https://github.com/Twenty4SevenLabs/Pandamonium.git`
- **Legacy mirror:** `gitlab` → `ssh://git@192.168.1.93:2222/labs247/pandamonium.git` (do not push unless asked)
- **Upstream read-only:** `github` fetch → `MADPANDA3D/Pandamonium`
- **Local checkout:** `/mnt/dev-env/projects/pandamonium`
- **Cursor memory:** `/mnt/dev-env/.cursor/memories/pandamonium-fork-repo.md`
