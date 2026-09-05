#!/usr/bin/env python3
"""Import Cursor/OpenCode personality bundle into Pandamonium data/."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_SOURCE = Path.home() / ".config" / "opencode"
DEFAULT_REPO = Path("/mnt/dev-env/projects/pandamonium")

SUPERPOWERS_EXACT = {
    "brainstorming",
    "using-superpowers",
    "using-git-worktrees",
    "writing-plans",
    "writing-skills",
    "test-driven-development",
    "verification-before-completion",
    "systematic-debugging",
    "subagent-driven-development",
    "executing-plans",
    "finishing-a-development-branch",
    "dispatching-parallel-agents",
    "receiving-code-review",
    "requesting-code-review",
}

TRINITY_PREFIXES = (
    "coding-trinity",
    "context7-",
    "taste-",
    "design-taste-",
    "design-",
    "brandkit",
    "stitch-design-taste",
    "redesign-existing-projects",
    "high-end-visual-design",
    "minimalist-ui",
    "industrial-brutalist-ui",
    "image-to-code",
    "imagegen-frontend-",
    "gpt-taste",
    "full-output-enforcement",
    "anti-lazy-output",
    "gold-standard-files",
)

HERMES_PREFIXES = ("hermes-", "request-hermes-")

INTEGRATION_NAMES = {
    "shadcn",
    "scan",
    "setup",
    "issues",
    "neon",
    "neon-postgres",
    "neon-postgres-branches",
    "neon-postgres-egress-optimizer",
    "neon-object-storage",
    "neon-functions",
    "neon-ai-gateway",
    "claimable-postgres",
    "aikido",
}

CURSOR_TOOL_REPLACEMENTS = [
    (r"\bTodoWrite\b", "task list tool"),
    (r"\bTask tool\b", "Agent tool"),
    (r"\bopen_resource\b", "open the file in the UI"),
    (r"\bcursor-app-control\b", "IDE control (not available in Pandamonium)"),
    (r"\bCursor Cloud Agent\b", "Hermes Kanban parallel work"),
    (r"\bCursor orchestrator\b", "Pandamonium orchestrator"),
    (r"\bOpenCode orchestrator\b", "Pandamonium orchestrator"),
]

CONDENSED_CONSTITUTION = """You are the Pandamonium orchestrator for the 24/7 Labs Hermes agency. Default action is dispatch through Hermes Kanban — do not implement project code unless the user says "do it here", Hermes/SSD is down, or the work is agent config only.

## Trinity (mandatory)
1. Superpowers — specs in docs/superpowers/specs/, plans in docs/superpowers/plans/. Never gate on agent-os/.
2. Taste skills — taste-skills-router (default design-taste-frontend) for all UI work.
3. Context7 — query latest library docs before implementing; re-query when stuck.
Stuck: STOP → Context7 → re-read spec/plan → retry.

## Disk and forge
- App code: /mnt/dev-env/projects/<slug> on dev-env SSD. Fail closed if mountpoint /mnt/dev-env is false.
- App repos: GitLab labs247. Personality sync: GitLab labs247/opencode-config at ~/.config/opencode.

## Session protocol
1. Superpowers first. 2. Confirm /mnt/dev-env mounted. 3. Create Morpheus parent card before project work.
4. Never force-push main. Never paste secrets into prompts.
5. After first-party code changes, run Aikido scan skill before declaring done.

## Tool safety
Deny or ask before: git push --force, git push -f, rm -rf /, DROP TABLE."""

MCP_SERVERS: list[dict[str, Any]] = [
    {
        "name": "hermes",
        "transport": "stdio",
        "command": "ssh",
        "args": [
            "openclaw1@vm-hermes",
            "bash",
            "-lc",
            "source ~/.hermes/hermes-agent/venv/bin/activate && hermes mcp serve",
        ],
        "env": {},
        "url": None,
    },
    {
        "name": "context7",
        "transport": "sse",
        "command": None,
        "args": [],
        "env": {},
        "url": "https://mcp.context7.com/mcp",
    },
    {
        "name": "github",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"},
        "url": None,
    },
    {
        "name": "gitlab",
        "transport": "sse",
        "command": None,
        "args": [],
        "env": {},
        "url": "https://prod.tail61d527.ts.net:3443/api/v4/mcp",
    },
    {
        "name": "prisma-local",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "prisma", "mcp"],
        "env": {},
        "url": None,
    },
    {
        "name": "prisma-remote",
        "transport": "sse",
        "command": None,
        "args": [],
        "env": {},
        "url": "https://mcp.prisma.io/mcp",
    },
    {
        "name": "shadcn",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "shadcn@latest", "mcp"],
        "env": {},
        "url": None,
    },
    {
        "name": "neon",
        "transport": "sse",
        "command": None,
        "args": [],
        "env": {},
        "url": "https://mcp.neon.tech/mcp",
    },
    {
        "name": "figma",
        "transport": "sse",
        "command": None,
        "args": [],
        "env": {},
        "url": "https://mcp.figma.com/mcp",
    },
    {
        "name": "aikido",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@aikidosec/mcp@1.0.17"],
        "env": {},
        "url": None,
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(name: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return value or "skill"


def categorize_skill(folder_name: str) -> str:
    lower = folder_name.lower()
    if any(lower.startswith(p) for p in HERMES_PREFIXES) or lower in HERMES_PREFIXES:
        return "hermes"
    if lower in SUPERPOWERS_EXACT or any(
        lower.startswith(p) for p in ("writing-", "test-driven-", "verification-", "systematic-", "subagent-", "executing-", "finishing-", "dispatching-", "receiving-", "requesting-")
    ):
        return "superpowers"
    if lower.startswith("cursor-"):
        return "cursor"
    if lower.startswith("prisma-") or lower.startswith("prisma"):
        return "prisma"
    if lower.startswith("figma-") or lower in INTEGRATION_NAMES or lower.startswith("neon"):
        return "integrations"
    if any(lower.startswith(p) for p in TRINITY_PREFIXES) or lower.endswith("-ui"):
        return "trinity"
    return "imported"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    block = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body


def render_frontmatter(meta: dict[str, str]) -> str:
    lines = ["---"]
    for key in ("name", "description", "version", "category", "tags", "status", "source", "confidence"):
        if key in meta and meta[key]:
            lines.append(f"{key}: {meta[key]}")
    lines.append("---")
    return "\n".join(lines)


def normalize_skill_text(folder_name: str, text: str, category: str) -> str:
    meta, body = parse_frontmatter(text)
    meta["name"] = meta.get("name") or folder_name
    meta["category"] = category
    meta["status"] = "draft" if category == "cursor" else "published"
    meta["source"] = "imported"
    if "description" not in meta:
        meta["description"] = f"Imported from Cursor/OpenCode bundle ({folder_name})"
    for pattern, repl in CURSOR_TOOL_REPLACEMENTS:
        body = re.sub(pattern, repl, body)
    return render_frontmatter(meta) + "\n\n" + body.strip() + "\n"


def copy_tree(src: Path, dest: Path, dry_run: bool) -> None:
    if dry_run:
        return
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def import_skills(source: Path, data_dir: Path, dry_run: bool) -> dict[str, int]:
    skills_src = source / "skills"
    skills_dest = data_dir / "skills"
    counts: dict[str, int] = {}
    if not skills_src.is_dir():
        raise FileNotFoundError(f"skills directory not found: {skills_src}")
    if not dry_run:
        skills_dest.mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted(skills_src.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        category = categorize_skill(skill_dir.name)
        counts[category] = counts.get(category, 0) + 1
        dest_dir = skills_dest / category / skill_dir.name
        if dry_run:
            continue
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        dest_dir.mkdir(parents=True)
        text = skill_md.read_text(encoding="utf-8")
        (dest_dir / "SKILL.md").write_text(
            normalize_skill_text(skill_dir.name, text, category), encoding="utf-8"
        )
        for child in skill_dir.iterdir():
            if child.name == "SKILL.md":
                continue
            if child.is_dir():
                shutil.copytree(child, dest_dir / child.name)
            else:
                shutil.copy2(child, dest_dir / child.name)
    return counts


def update_identity(source: Path, data_dir: Path, dry_run: bool) -> None:
    settings_path = data_dir / "settings.json"
    presets_path = data_dir / "presets.json"
    agents_md = source / "AGENTS.md"
    if not agents_md.is_file():
        raise FileNotFoundError(f"AGENTS.md not found: {agents_md}")
    full_prompt = agents_md.read_text(encoding="utf-8")
    settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.exists() else {}
    settings["agent_constitution"] = CONDENSED_CONSTITUTION
    settings["agent_constitution_version"] = "2"
    settings["agent_display_name"] = settings.get("agent_display_name") or "Hermes Orchestrator"
    presets = json.loads(presets_path.read_text(encoding="utf-8")) if presets_path.exists() else {}
    presets["hermes_orchestrator"] = {
        "name": "Hermes Orchestrator",
        "temperature": 0.3,
        "max_tokens": 16000,
        "system_prompt": full_prompt,
        "enabled": True,
    }
    if not dry_run:
        settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
        presets_path.write_text(json.dumps(presets, indent=2) + "\n", encoding="utf-8")


def import_mcp(data_dir: Path, dry_run: bool) -> int:
    db_path = data_dir / "app.db"
    if dry_run:
        return len(MCP_SERVERS)
    conn = sqlite3.connect(db_path)
    now = utc_now()
    try:
        for spec in MCP_SERVERS:
            name = spec["name"]
            row = conn.execute("SELECT id FROM mcp_servers WHERE name = ?", (name,)).fetchone()
            if row:
                server_id = row[0]
                conn.execute(
                    """
                    UPDATE mcp_servers SET
                        transport = ?, command = ?, args = ?, env = ?, url = ?,
                        is_enabled = 1, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        spec["transport"],
                        spec.get("command"),
                        json.dumps(spec.get("args") or []),
                        json.dumps(spec.get("env") or {}),
                        spec.get("url"),
                        now,
                        server_id,
                    ),
                )
            else:
                server_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO mcp_servers (
                        id, name, transport, command, args, env, url, is_enabled,
                        oauth_config, disabled_tools, oauth_tokens, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, NULL, NULL, NULL, ?, ?)
                    """,
                    (
                        server_id,
                        name,
                        spec["transport"],
                        spec.get("command"),
                        json.dumps(spec.get("args") or []),
                        json.dumps(spec.get("env") or {}),
                        spec.get("url"),
                        now,
                        now,
                    ),
                )
        conn.commit()
    finally:
        conn.close()
    return len(MCP_SERVERS)


def archive_sources(source: Path, data_dir: Path, dry_run: bool) -> int:
    archive_root = data_dir / "personal_docs" / "cursor-migration"
    count = 0
    if dry_run:
        return 8
    archive_root.mkdir(parents=True, exist_ok=True)
    for agent in (source / "agents").glob("*.md"):
        shutil.copy2(agent, archive_root / f"agent-{agent.name}")
        count += 1
    plugins_dest = archive_root / "plugins"
    plugins_dest.mkdir(exist_ok=True)
    for plugin in (source / "plugins").glob("*.ts"):
        shutil.copy2(plugin, plugins_dest / plugin.name)
        count += 1
    for doc in [
        source / "docs" / "superpowers" / "specs" / "2026-08-27-opencode-migration-design.md",
        source / "AGENTS.md",
    ]:
        if doc.is_file():
            shutil.copy2(doc, archive_root / doc.name)
            count += 1
    for cmd in (source / "commands").glob("*.md"):
        shutil.copy2(cmd, archive_root / f"command-{cmd.name}")
        count += 1
    return count


def build_manifest(source: Path, repo: Path, output: Path, dry_run: bool) -> None:
    if dry_run:
        return
    import subprocess

    cmd = [
        "python3",
        str(repo / "scripts" / "agent_migration_manifest.py"),
        "--source-name",
        "cursor-opencode",
        "--source-kind",
        "generic",
        "--skills-dir",
        str(source / "skills"),
        "--archive",
        str(source / "AGENTS.md"),
        "--archive",
        str(source / "agents"),
        "--include-archive-content",
        "--output",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Import Cursor/OpenCode bundle into Pandamonium")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_REPO / "data")
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sync", action="store_true", help="Re-import after opencode git pull")
    parser.add_argument("--manifest-out", type=Path, default=Path("/tmp/cursor-opencode-migration.v1.json"))
    args = parser.parse_args()

    if not args.source.is_dir():
        raise SystemExit(f"source not found: {args.source}")
    if not args.data_dir.is_dir():
        raise SystemExit(f"data dir not found: {args.data_dir}")

    skill_counts = import_skills(args.source, args.data_dir, args.dry_run)
    update_identity(args.source, args.data_dir, args.dry_run)
    mcp_count = import_mcp(args.data_dir, args.dry_run)
    archived = archive_sources(args.source, args.data_dir, args.dry_run)
    build_manifest(args.source, args.repo, args.manifest_out, args.dry_run)

    total_skills = sum(skill_counts.values())
    print(json.dumps({
        "dry_run": args.dry_run,
        "skills_imported": total_skills,
        "skill_categories": skill_counts,
        "mcp_servers": mcp_count,
        "archived_files": archived,
        "manifest": str(args.manifest_out),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
