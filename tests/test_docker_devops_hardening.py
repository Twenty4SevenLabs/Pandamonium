"""Static regressions for Docker/devops hardening contracts."""

import ast
import re
from pathlib import Path

import yaml
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILES = [
    ROOT / "docker-compose.yml",
    ROOT / "docker-compose.gpu-nvidia.yml",
    ROOT / "docker-compose.gpu-amd.yml",
]
HOST_DOCKER_OVERLAY = ROOT / "docker" / "host-docker.yml"
HOST_PROXMOX_OVERLAY = ROOT / "docker" / "host-proxmox.yml"
TEST_DOCS = [
    ROOT / "tests" / "README.md",
    ROOT / "tests" / "TESTING_STANDARD.md",
    ROOT / "tests" / "LAYOUT_INVENTORY.md",
]


def _compose_env_names(path: Path) -> set[str]:
    compose = yaml.safe_load(path.read_text(encoding="utf-8"))
    env = compose["services"]["pandamonium"]["environment"]
    return {entry.split("=", 1)[0] for entry in env}


def _upload_limit_env_names() -> set[str]:
    source = (ROOT / "src" / "upload_limits.py").read_text(encoding="utf-8")
    legacy_names = set(re.findall(r'"(ODYSSEUS_[A-Z_]*BYTES)"', source))
    return {name.replace("ODYSSEUS_", "PANDAMONIUM_", 1) for name in legacy_names} | {
        "PANDAMONIUM_CHAT_UPLOAD_MAX_BYTES"
    }


def _cors_allow_methods() -> list[str]:
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
            if "CORS_ALLOW_METHODS" in names:
                return ast.literal_eval(node.value)
    raise AssertionError("CORS_ALLOW_METHODS not found")


def test_compose_files_forward_every_upload_limit_env_var():
    expected = _upload_limit_env_names()
    assert expected
    for path in COMPOSE_FILES:
        assert expected <= _compose_env_names(path), path.name


def _compose_bytes(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip().lower()
    match = re.fullmatch(r"(\d+)([kmg]i?b?)?", text)
    if not match:
        raise AssertionError(f"unparseable compose memory value: {value!r}")
    amount = int(match.group(1))
    suffix = match.group(2) or ""
    multiplier = {
        "": 1,
        "k": 1000,
        "kb": 1000,
        "ki": 1024,
        "kib": 1024,
        "m": 1000 ** 2,
        "mb": 1000 ** 2,
        "mi": 1024 ** 2,
        "mib": 1024 ** 2,
        "g": 1000 ** 3,
        "gb": 1000 ** 3,
        "gi": 1024 ** 3,
        "gib": 1024 ** 3,
    }[suffix]
    return amount * multiplier


def _host_proxmox_service_block(name: str) -> str:
    text = HOST_PROXMOX_OVERLAY.read_text(encoding="utf-8")
    match = re.search(rf"(?ms)^  {re.escape(name)}:\n(.*?)(?=^  [a-z]|\Z)", text)
    assert match, f"{name} service missing from host-proxmox overlay"
    return match.group(1)


def test_host_proxmox_overlay_does_not_cgroup_oom_pandamonium():
    """A 2GiB mem_limit with memswap_limit equal to it disables swap.

    uvicorn then dies with Docker exit 137 / CONSTRAINT_MEMCG (observed RSS
    ~0.5GiB, total-vm ~3.8GiB) and the UI stops loading.
    """
    body = _host_proxmox_service_block("pandamonium")
    mem_match = re.search(r"mem_limit:\s*(\S+)", body)
    swap_match = re.search(r"memswap_limit:\s*(\S+)", body)
    mem = _compose_bytes(mem_match.group(1) if mem_match else None)
    swap = _compose_bytes(swap_match.group(1) if swap_match else None)
    min_bytes = 4 * 1024 ** 3
    if mem is not None:
        assert mem >= min_bytes, f"pandamonium mem_limit {mem_match.group(1)!r} OOMs uvicorn"
    if mem is not None and swap is not None:
        assert swap > mem or swap >= min_bytes, "equal mem/memswap disables swap and OOM-kills uvicorn"


def test_default_compose_files_do_not_mount_host_docker_socket():
    for path in COMPOSE_FILES:
        text = path.read_text(encoding="utf-8")
        assert "/var/run/docker.sock" not in text, path.name


def test_hardened_image_does_not_bundle_or_download_docker_cli():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "DOCKER_CLI_VERSION" not in dockerfile
    assert "download.docker.com/linux/static" not in dockerfile
    assert not re.search(
        r"\b(docker\.io|docker-ce-cli|docker-cli|moby-cli)\b", dockerfile
    )


def test_host_docker_overlay_mounts_socket_and_adds_docker_group():
    overlay = yaml.safe_load(HOST_DOCKER_OVERLAY.read_text(encoding="utf-8"))
    service = overlay["services"]["pandamonium"]

    assert "/var/run/docker.sock:/var/run/docker.sock" in service["volumes"]
    assert "${DOCKER_GID:-963}" in service["group_add"]
    assert "PANDAMONIUM_ENABLE_HOST_DOCKER=true" in service["environment"]


def test_docker_entrypoint_gates_socket_group_plumbing_on_explicit_opt_in():
    script = (ROOT / "docker" / "entrypoint.sh").read_text(encoding="utf-8")
    block_start = script.index("DOCKER_SOCK=\"${DOCKER_SOCK:-/var/run/docker.sock}\"")
    block_end = script.index("\nmount_root_for()", block_start)
    socket_group_block = script[block_start:block_end]

    opt_in_check = socket_group_block.index(
        "[ \"$HOST_DOCKER_ENABLED\" = \"true\" ]"
    )
    socket_check = socket_group_block.index("[ -S \"$DOCKER_SOCK\" ]")
    stat_socket = socket_group_block.index("stat -c")
    add_group = socket_group_block.index("groupadd -g")
    add_user_group = socket_group_block.index("usermod -aG")

    assert opt_in_check < socket_check < stat_socket < add_group < add_user_group


def test_docker_entrypoint_does_not_resolve_root_commands_from_app_local_path():
    script = (ROOT / "docker" / "entrypoint.sh").read_text(encoding="utf-8")
    path_export = script.index('export PATH="/app/.local/bin:$PATH"')
    gosu_capture = script.index('GOSU_BIN="$(command -v gosu)"')
    python_capture = script.index('PYTHON_BIN="$(command -v python)"')
    setup_call = script.index('"$GOSU_BIN" "$APP_USER" "$PYTHON_BIN" /app/setup.py')
    final_exec = script.index('exec "$GOSU_BIN" "$APP_USER" "$@"')

    assert gosu_capture < path_export < setup_call
    assert python_capture < path_export < setup_call
    assert final_exec > path_export


def test_docker_entrypoint_ownership_repair_stays_inside_expected_mounts():
    script = (ROOT / "docker" / "entrypoint.sh").read_text(encoding="utf-8")
    assert "find /app -xdev" in script
    for path in ("/app/data", "/app/logs", "/app/.ssh", "/app/.cache", "/app/.local"):
        assert f"-path {path}" in script
    assert "mount_root_for" in script
    assert "is_broad_mount_root" in script
    assert "Skipping recursive ownership repair" in script


def test_docker_bakes_pinned_browser_mcp_and_repairs_only_its_cache():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    entrypoint = (ROOT / "docker" / "entrypoint.sh").read_text(encoding="utf-8")
    builtin = (ROOT / "src" / "builtin_mcp.py").read_text(encoding="utf-8")
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    volumes = compose["services"]["pandamonium"]["volumes"]

    assert "ARG PLAYWRIGHT_MCP_VERSION=0.0.80" in dockerfile
    assert '"@playwright/mcp@${PLAYWRIGHT_MCP_VERSION}"' in dockerfile
    assert "playwright-core/cli.js install-deps chromium" in dockerfile
    assert "playwright-core/cli.js install --no-shell chromium" in dockerfile
    assert "PLAYWRIGHT_BROWSERS_PATH=/ms-playwright" in dockerfile
    assert (
        "${APP_DATA_DIR:-./data}/browser-mcp:/app/.cache/browser-mcp:z"
        in volumes
    )
    assert "mkdir -p /app/.cache/browser-mcp/output" in entrypoint
    assert "/app/.cache/browser-mcp /app/.local" in entrypoint
    assert '_BROWSER_MCP_PACKAGE = "@playwright/mcp@0.0.80"' in builtin
    assert '/opt/pandamonium-browser-mcp/node_modules/@playwright/mcp/cli.js' in builtin
    assert '"--browser", "chromium"' in builtin
    assert '"--no-sandbox"' in builtin
    assert '"--isolated"' in builtin
    assert '"PLAYWRIGHT_BROWSERS_PATH": "/ms-playwright"' in builtin
    assert '"XDG_CACHE_HOME": "/app/.cache/browser-mcp"' in builtin


def test_dockerignore_excludes_secrets_editor_backups():
    patterns = set((ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines())
    assert {
        "secrets.env",
        "secrets.env.*",
        "secrets.env~",
        ".secrets.env.swp",
        ".secrets.env.swo",
        "**/#secrets.env#",
    } <= patterns
    assert "!secrets.env.example" in patterns


def test_cors_allow_methods_include_patch():
    methods = _cors_allow_methods()
    assert "PATCH" in methods


def test_patch_preflight_is_allowed_by_configured_cors_methods():
    async def patched(_request):
        return PlainTextResponse("ok")

    app = Starlette(routes=[Route("/api/document/1", patched, methods=["PATCH"])])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://client.local"],
        allow_credentials=True,
        allow_methods=_cors_allow_methods(),
        allow_headers=["Content-Type"],
    )

    response = TestClient(app).options(
        "/api/document/1",
        headers={
            "Origin": "http://client.local",
            "Access-Control-Request-Method": "PATCH",
        },
    )

    assert response.status_code == 200


def test_testing_docs_use_project_venv_for_python_validation():
    stale_patterns = [
        "python3 -m pytest",
        "python3 -m py_compile",
        "Focused `pytest`",
        "`pytest` on neighboring",
        ".venv/bin/python",
    ]
    for path in TEST_DOCS:
        text = path.read_text(encoding="utf-8")
        for stale in stale_patterns:
            assert stale not in text, f"{path.name} still contains {stale!r}"


def test_docker_publish_keeps_release_version_tags_immutable():
    workflow = (ROOT / ".github" / "workflows" / "docker-publish.yml").read_text(
        encoding="utf-8"
    )

    assert "tags: ['v*']" in workflow
    assert "Tag $GITHUB_REF_NAME does not match APP_VERSION $v" in workflow
    assert (
        "type=raw,value=${{ steps.ver.outputs.version }},"
        "enable=${{ github.ref_type == 'tag' }}"
    ) in workflow
    assert "type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}" in workflow


def test_published_container_embeds_exact_source_revision():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "docker-publish.yml").read_text(
        encoding="utf-8"
    )
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))

    assert "ARG PANDAMONIUM_SOURCE_REVISION" in dockerfile
    assert "ENV PANDAMONIUM_SOURCE_REVISION=${PANDAMONIUM_SOURCE_REVISION}" in dockerfile
    assert "org.opencontainers.image.revision=${PANDAMONIUM_SOURCE_REVISION}" in dockerfile
    assert "PANDAMONIUM_SOURCE_REVISION=${{ github.sha }}" in workflow
    assert compose["services"]["pandamonium"]["build"]["args"] == {
        "PANDAMONIUM_SOURCE_REVISION": "${PANDAMONIUM_SOURCE_REVISION:-}"
    }
