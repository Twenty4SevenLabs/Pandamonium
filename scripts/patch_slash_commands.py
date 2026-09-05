#!/usr/bin/env python3
"""Patch slashCommands.js with /kanban and /trinity commands."""

from pathlib import Path

REPO = Path("/mnt/dev-env/projects/pandamonium")
TARGET = REPO / "static/js/slashCommands.js"

HANDLERS = '''
// ── Hermes Kanban / Trinity (Cursor migration) ──

async function _cmdKanbanParent(args, ctx) {
  const title = args.join(' ').trim();
  if (!title) { slashReply('Usage: /kanban parent <title>'); return true; }
  const msg = [
    `Create one Hermes Kanban parent card assigned to Morpheus (default) for: ${title}`,
    '',
    'Follow hermes-orchestrator skill and AGENTS.md session protocol.',
    'Confirm /mnt/dev-env is mounted. Include Superpowers spec paths, GitLab URL, taste skill if UI, success criteria.',
    'Do not implement project code unless an exception applies.',
  ].join('\\n');
  if (!_submitComposedMessage(msg)) slashReply('Could not submit kanban dispatch prompt.');
  return true;
}

async function _cmdTrinityCheck(args, ctx) {
  const context = args.join(' ').trim() || '(current session)';
  const msg = [
    'Audit Trinity compliance for this session:',
    '1. Superpowers: spec/plan in docs/superpowers/',
    '2. Taste: taste-skills-router for UI work',
    '3. Context7: queried for each library in scope',
    '',
    `Context: ${context}`,
    '',
    'Report gaps and next actions.',
  ].join('\\n');
  if (!_submitComposedMessage(msg)) slashReply('Could not submit trinity audit prompt.');
  return true;
}
'''

COMMANDS_BLOCK = '''
  kanban: {
    alias: [],
    category: 'Agent',
    help: 'Hermes Kanban dispatch helpers',
    default: 'parent',
    subs: {
      parent: { handler: _cmdKanbanParent, help: 'Create Morpheus parent card', usage: '/kanban parent <title>' },
    },
  },
  trinity: {
    alias: [],
    category: 'Agent',
    help: 'Trinity compliance audit',
    default: 'check',
    subs: {
      check: { handler: _cmdTrinityCheck, help: 'Audit Superpowers+Taste+Context7', usage: '/trinity check [context]' },
    },
  },
'''


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if "_cmdKanbanParent" in text:
        print("slash commands already patched")
        return 0
    marker = "async function _cmdSkills(args, ctx) {"
    if marker not in text:
        raise SystemExit("could not find _cmdSkills marker")
    text = text.replace(marker, HANDLERS + "\n" + marker, 1)
    anchor = "  mcp: {"
    if anchor not in text:
        raise SystemExit("could not find mcp command anchor")
    text = text.replace(anchor, COMMANDS_BLOCK + anchor, 1)
    TARGET.write_text(text, encoding="utf-8")
    print(f"patched {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
