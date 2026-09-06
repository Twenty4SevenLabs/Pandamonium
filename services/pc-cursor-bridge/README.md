# PC Cursor bridge

Read-only LAN companion that exposes **Remote-SSH** Cursor IDE agent transcripts for
Panda's sidebar mirror (Phase 2).

Jason codes only through **Windows Cursor → Remote-SSH → Linux**. The Cursor UI runs on
Windows; `cursor-server` and agent transcripts live on **whichever Linux host you SSH
into**, under that user's `~/.cursor/projects`. They are **not** on the Windows laptop.

Panda (on M3 / `pve-prod`) merges IDE agents from every bridge URL you configure.

## Cluster layout

| SSH target | Host IP | Transcripts on | Bridge install |
|------------|---------|----------------|----------------|
| **M3** `pve-prod` (primary) | `192.168.1.93` | `/home/labsadmin/.cursor/projects` | Docker `pc-cursor-bridge` in Panda compose (already wired) |
| **M1** `pve-heavy` | `192.168.1.2` | same path on **that** host | systemd on M1 (see below) |
| **M2** `pve-agents` | `192.168.1.90` | same path on **that** host | systemd on M2 (see below) |

If you Remote-SSH into a **guest** instead of the Proxmox host (e.g. `vm-gpu-creative`
`192.168.1.181` or M2 GPU guest `192.168.1.191`), install the bridge **on that guest**
— transcripts follow the SSH session host, not Panda's host.

**Yes — M1 and M2 need their own bridge** whenever you code there. M3's Docker sidecar
only reads M3's `~/.cursor/projects`; it cannot see transcripts written on other nodes.

## One shared token

Use the **same bearer token** on every node. Panda already stores it at
`data/cursor-bridge/pc-ide-token` on M3.

Copy that file's contents to each remote bridge host, e.g.
`~/.config/jarvis/cursor-bridge-token` (mode `600`).

## M3 — Panda Docker (default)

On `pve-prod`, the compose service mounts M3 transcripts read-only:

```yaml
# docker-compose.yml — pc-cursor-bridge
volumes:
  - /home/labsadmin/.cursor/projects:/cursor-projects:ro
```

Panda env (inside compose):

```bash
PANDAMONIUM_PC_CURSOR_BRIDGE_URL=http://pc-cursor-bridge:8051
PANDAMONIUM_PC_CURSOR_BRIDGE_URLS=http://pc-cursor-bridge:8051,http://192.168.1.2:8051,http://192.168.1.90:8051
PANDAMONIUM_PC_CURSOR_BRIDGE_TOKEN_FILE=/app/data/cursor-bridge/pc-ide-token
```

`PANDAMONIUM_PC_CURSOR_BRIDGE_URL` remains for backward compatibility; prefer
`PANDAMONIUM_PC_CURSOR_BRIDGE_URLS` (comma-separated) for the full cluster.

## M1 / M2 — systemd on each Proxmox host

From a checkout of pandamonium on the target node (or copy the install script):

```bash
# On pve-heavy (M1) or pve-agents (M2), as labsadmin
cd /mnt/dev-env/projects/pandamonium   # or your clone path
chmod +x services/pc-cursor-bridge/install-systemd.sh
./services/pc-cursor-bridge/install-systemd.sh
```

The installer:

- Copies `pc_cursor_bridge.py` + `transcript_io.py` to `~/.local/share/pandamonium/pc-cursor-bridge`
- Registers `pc-cursor-bridge.service` (listens `0.0.0.0:8051`, LAN only)
- Reads transcripts from `$HOME/.cursor/projects` on **that** machine
- Expects token at `~/.config/jarvis/cursor-bridge-token` (paste M3's `pc-ide-token` content)

Verify from M3:

```bash
curl -s -H "Authorization: Bearer $(cat data/cursor-bridge/pc-ide-token)" \
  http://192.168.1.2:8051/health
curl -s -H "Authorization: Bearer $(cat data/cursor-bridge/pc-ide-token)" \
  http://192.168.1.90:8051/health
```

Then restart Panda so it picks up `PANDAMONIUM_PC_CURSOR_BRIDGE_URLS`.

## Foreground dev (any Linux SSH host)

```bash
chmod +x services/pc-cursor-bridge/install-linux.sh
./services/pc-cursor-bridge/install-linux.sh
```

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Companion alive + projects root |
| GET | `/v1/ide/agents` | Agent list from transcripts |
| GET | `/v1/ide/agents/{id}` | Agent metadata |
| GET | `/v1/ide/agents/{id}/session` | Full Cursor-style message panel |

All routes require `Authorization: Bearer <token>`.

Panda merges IDE agents when bridge URL(s) are set and loads full sessions through
`/api/cursor/agents/{id}/session`. Check `/api/cursor/status` → `ide_mirror.hosts[]`
for per-node connectivity.
