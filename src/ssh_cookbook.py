"""Cookbook SSH layout for Pandamonium agent bash and remote Hermes access.

Agent subprocesses set HOME to DATA_DIR (/app/data), so OpenSSH reads
``$HOME/.ssh/config``. Keys and known_hosts live on the bind mount at
``/app/.ssh`` (host ``data/ssh/``).
"""

from __future__ import annotations

import logging
import os
import shlex
import subprocess
from pathlib import Path

from src.constants import DATA_DIR
from src.hermes_kanban_cli import DEFAULT_HERMES_KANBAN_BOARD, normalize_hermes_cli_command

logger = logging.getLogger(__name__)

# Bind-mounted cookbook identity (see docker-compose.yml).
SSH_DIR = Path(os.environ.get("PANDAMONIUM_SSH_DIR", "/app/.ssh"))
SSH_IDENTITY = SSH_DIR / "id_ed25519"
SSH_KNOWN_HOSTS = SSH_DIR / "known_hosts"

# Read by bash/python subprocesses via data/bin/ssh wrapper (HOME=/app/data).
AGENT_SSH_DIR = Path(DATA_DIR) / ".ssh"
AGENT_SSH_CONFIG = AGENT_SSH_DIR / "config"
AGENT_BIN_DIR = Path(DATA_DIR) / "bin"
AGENT_SSH_WRAPPER = AGENT_BIN_DIR / "ssh"

# Canonical client config colocated with cookbook keys (see write_agent_ssh_config).

_HERMES_HOSTS = ("vm-hermes", "192.168.1.192")
_HERMES_USER = "openclaw1"
_HERMES_ADDR = "192.168.1.192"


def _ssh_config_body() -> str:
    identity = SSH_IDENTITY
    known_hosts = SSH_KNOWN_HOSTS
    return f"""# Pandamonium agent SSH — auto-generated; do not edit by hand.
# Regenerated on setup / container start via src.ssh_cookbook.ensure_ssh_cookbook().

Host vm-hermes {_HERMES_ADDR}
    HostName {_HERMES_ADDR}
    User {_HERMES_USER}
    IdentityFile {identity}
    IdentitiesOnly yes
    BatchMode yes
    RequestTTY no
    StrictHostKeyChecking accept-new
    UserKnownHostsFile {known_hosts}
    ConnectTimeout 15

Host openclaw1@vm-hermes openclaw1@{_HERMES_ADDR}
    HostName {_HERMES_ADDR}
    User {_HERMES_USER}
    IdentityFile {identity}
    IdentitiesOnly yes
    BatchMode yes
    RequestTTY no
    StrictHostKeyChecking accept-new
    UserKnownHostsFile {known_hosts}
    ConnectTimeout 15
"""

def wrap_hermes_remote_command(
    remote: str,
    *,
    default_board: str = DEFAULT_HERMES_KANBAN_BOARD,
) -> str:
    """Wrap a remote shell snippet for non-interactive Hermes CLI execution."""
    remote = normalize_hermes_cli_command((remote or "").strip()) or "true"
    inner = shlex.quote(remote)
    board_env = ""
    if default_board and "HERMES_KANBAN_BOARD" not in remote:
        board_env = f"HERMES_KANBAN_BOARD={shlex.quote(default_board)} "
    return (
        f'PATH="/usr/local/bin:$HOME/.hermes/hermes-agent/venv/bin:$PATH" '
        f"{board_env}"
        f"HERMES_QUIET=1 CI=1 TERM=dumb bash -lc {inner}"
    )


def hermes_ssh_argv(remote_command: str, *, ssh_config: Path | None = None) -> list[str]:
    """Build argv for a non-interactive ssh invocation to vm-hermes."""
    config = ssh_config or (SSH_DIR / "config")
    return [
        "/usr/bin/ssh",
        "-T",
        "-o",
        "RequestTTY=no",
        "-F",
        str(config),
        "vm-hermes",
        wrap_hermes_remote_command(remote_command),
    ]


def _run_keyscan(target: str) -> bytes:
    proc = subprocess.run(
        ["ssh-keyscan", "-H", "-t", "ed25519,ecdsa,rsa", target],
        capture_output=True,
        timeout=12,
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        detail = (proc.stderr or proc.stdout or b"").decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or f"ssh-keyscan returned no keys for {target}")
    return proc.stdout.strip() + b"\n"


def refresh_known_hosts(*, targets: tuple[str, ...] = _HERMES_HOSTS) -> None:
    """Append missing host keys for Hermes targets into the cookbook known_hosts."""
    SSH_DIR.mkdir(parents=True, exist_ok=True)
    SSH_KNOWN_HOSTS.touch(mode=0o600, exist_ok=True)
    existing = SSH_KNOWN_HOSTS.read_bytes() if SSH_KNOWN_HOSTS.is_file() else b""
    chunks: list[bytes] = []
    for target in targets:
        if target.encode() in existing:
            continue
        try:
            chunks.append(_run_keyscan(target))
        except Exception as exc:
            logger.warning("ssh-keyscan for %s failed: %s", target, exc)
    if not chunks:
        return
    with SSH_KNOWN_HOSTS.open("ab") as handle:
        if existing and not existing.endswith(b"\n"):
            handle.write(b"\n")
        for chunk in chunks:
            handle.write(chunk)
    os.chmod(SSH_KNOWN_HOSTS, 0o600)


def write_agent_ssh_config() -> Path:
    """Write SSH client config beside cookbook keys and install a PATH wrapper."""
    body = _ssh_config_body()
    ssh_dir = SSH_DIR
    ssh_config = ssh_dir / "config"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(ssh_dir, 0o700)
    current = ssh_config.read_text(encoding="utf-8") if ssh_config.is_file() else ""
    if current != body:
        ssh_config.write_text(body, encoding="utf-8")
        os.chmod(ssh_config, 0o600)

    agent_bin = Path(DATA_DIR) / "bin"
    agent_wrapper = agent_bin / "ssh"
    agent_bin.mkdir(parents=True, exist_ok=True)
    wrapper = (
        "#!/bin/sh\n"
        "# Pandamonium agent SSH wrapper — cookbook config + no TTY (non-interactive).\n"
        f'exec /usr/bin/ssh -T -o RequestTTY=no -F "{ssh_config}" "$@"\n'
    )
    if not agent_wrapper.is_file() or agent_wrapper.read_text(encoding="utf-8") != wrapper:
        agent_wrapper.write_text(wrapper, encoding="utf-8")
        os.chmod(agent_wrapper, 0o755)

    return ssh_config


def ensure_ssh_cookbook() -> None:
    """Idempotent: agent SSH config + Hermes known_hosts entries."""
    write_agent_ssh_config()
    if not SSH_IDENTITY.is_file():
        logger.warning(
            "Cookbook SSH identity missing at %s — generate a key in data/ssh/ "
            "and authorize it on vm-hermes as %s",
            SSH_IDENTITY,
            _HERMES_USER,
        )
        return
    try:
        refresh_known_hosts()
    except Exception as exc:
        logger.warning("Could not refresh cookbook known_hosts: %s", exc)
