import { closeCursorAgentOverlay, initCursorAgentOverlay, openCursorAgentOverlay } from './cursorBridgeOverlay.js';

const byId = (id) => document.getElementById(id);

const state = {
  selectedAgentId: null,
  selectedAgent: null,
  pollTimer: null,
  streamAbort: null,
  agents: [],
  sessionMessages: [],
  liveAssistantText: '',
};

function relativeTime(unix) {
  const seconds = Math.max(0, Math.floor(Date.now() / 1000) - Number(unix || 0));
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 86400)}d`;
}

function setCapabilitiesLine(status) {
  const line = byId('cursor-bridge-capabilities');
  if (!line) return;
  const caps = status?.capabilities;
  if (!caps || status?.connected !== true) {
    line.hidden = true;
    line.textContent = '';
    return;
  }
  const mcpCount = Array.isArray(caps.mcp_servers) ? caps.mcp_servers.length : 0;
  const skillCount = Number(caps.skill_count || 0);
  const sources = Array.isArray(caps.setting_sources) ? caps.setting_sources.join(', ') : '';
  line.hidden = false;
  line.textContent = `Skills ${skillCount} · MCP ${mcpCount}${sources ? ` · ${sources}` : ''}`;
}

function setStatusPill(status) {
  const pill = byId('cursor-bridge-sidebar-status');
  if (!pill) return;
  const connected = status?.connected === true;
  const configured = status?.configured === true;
  pill.dataset.state = connected ? 'connected' : configured ? 'warning' : 'disconnected';
  pill.setAttribute('aria-label', connected ? 'Connected' : configured ? 'Reconnect needed' : 'Disconnected');
  setCapabilitiesLine(status);
}

function persistSectionExpanded() {
  try {
    const saved = JSON.parse(localStorage.getItem('section-collapsed') || '{}');
    saved['cursor-bridge-section'] = false;
    localStorage.setItem('section-collapsed', JSON.stringify(saved));
  } catch (_error) {
    /* ignore storage failures */
  }
}

async function readJson(response) {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof body.detail === 'string' ? body.detail : (body.error || 'Cursor bridge request failed');
    throw new Error(detail);
  }
  return body;
}

function statusDot(status) {
  const dot = document.createElement('span');
  dot.className = 'cursor-agent-status-dot';
  dot.dataset.state = status === 'running' ? 'running' : status === 'failed' ? 'failed' : 'idle';
  dot.setAttribute('aria-hidden', 'true');
  return dot;
}

function buildRemoveButton(agent) {
  const removeBtn = document.createElement('button');
  removeBtn.type = 'button';
  removeBtn.className = 'cursor-agent-remove-btn';
  removeBtn.title = 'Remove agent';
  removeBtn.setAttribute('aria-label', `Remove ${agent.title || 'Cursor agent'}`);
  removeBtn.innerHTML = '<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>';
  removeBtn.addEventListener('click', (event) => {
    event.preventDefault();
    event.stopPropagation();
    removeAgent(agent).catch((error) => {
      window.alert(error instanceof Error ? error.message : 'Could not remove agent.');
    });
  });
  return removeBtn;
}

function renderAgentList(items) {
  const list = byId('cursor-agent-list');
  if (!list) return;
  list.replaceChildren();
  if (!items.length) {
    const empty = document.createElement('div');
    empty.className = 'cursor-agent-empty';
    empty.textContent = 'No Cursor agents yet.';
    list.appendChild(empty);
    return;
  }
  items.forEach((agent) => {
    const agentId = String(agent.agent_id || '');
    const row = document.createElement('div');
    row.className = 'cursor-agent-row';
    if (state.selectedAgentId === agentId) row.classList.add('is-selected');

    const main = document.createElement('button');
    main.type = 'button';
    main.className = 'cursor-agent-row-main';
    main.dataset.agentId = agentId;
    const title = document.createElement('span');
    title.className = 'cursor-agent-title';
    title.textContent = String(agent.title || 'Cursor agent');
    const meta = document.createElement('span');
    meta.className = 'cursor-agent-meta';
    const badge = document.createElement('span');
    badge.className = 'cursor-agent-source-badge';
    badge.textContent = String(agent.source || 'bridge').toUpperCase();
    const time = document.createElement('span');
    time.className = 'cursor-agent-time';
    time.textContent = relativeTime(agent.updated_at);
    meta.append(badge, time);
    main.append(statusDot(agent.status), title, meta);
    main.addEventListener('click', () => selectAgent(agentId));

    row.append(main, buildRemoveButton(agent));
    list.appendChild(row);
  });
}

function messageText(blocks) {
  return (Array.isArray(blocks) ? blocks : [])
    .filter((block) => block?.type === 'text' && block.text)
    .map((block) => String(block.text))
    .join('\n\n')
    .trim();
}

function renderMessageNode(message, index, liveText = '') {
  const role = message?.role === 'user' ? 'user' : 'assistant';
  const wrap = document.createElement('article');
  wrap.className = `cursor-agent-msg cursor-agent-msg-${role}`;
  wrap.dataset.messageIndex = String(index);

  const label = document.createElement('div');
  label.className = 'cursor-agent-msg-role';
  label.textContent = role === 'user' ? 'You' : 'Agent';

  const body = document.createElement('div');
  body.className = 'cursor-agent-msg-body';
  let text = messageText(message?.blocks);
  if (message?.live && liveText) text = liveText;
  body.textContent = text || (role === 'assistant' && message?.live ? 'Thinking…' : '');

  const tools = document.createElement('div');
  tools.className = 'cursor-agent-tool-list';
  (Array.isArray(message?.blocks) ? message.blocks : []).forEach((block) => {
    if (block?.type !== 'tool') return;
    const chip = document.createElement('span');
    chip.className = 'cursor-agent-tool-chip';
    chip.textContent = String(block.summary || block.name || 'tool');
    tools.appendChild(chip);
  });

  wrap.append(label, body);
  if (tools.childElementCount) wrap.append(tools);
  return wrap;
}

function renderAgentPanel(messages, liveText = '') {
  const panel = byId('cursor-agent-panel');
  if (!panel) return;
  panel.replaceChildren();
  const rows = Array.isArray(messages) ? messages : [];
  if (!rows.length && !liveText) {
    const empty = document.createElement('div');
    empty.className = 'cursor-agent-panel-empty';
    empty.textContent = 'Select an agent to load its Cursor session.';
    panel.appendChild(empty);
    return;
  }
  rows.forEach((message, index) => {
    panel.appendChild(renderMessageNode(message, index, message?.live ? liveText : ''));
  });
  panel.scrollTop = panel.scrollHeight;
}

function setDetailChrome(agent) {
  const detail = byId('cursor-agent-detail');
  const title = byId('cursor-agent-detail-title');
  const badge = byId('cursor-agent-detail-badge');
  const readonlyNote = byId('cursor-agent-readonly-note');
  const readOnly = agent?.read_only === true || String(agent?.source || '').toLowerCase() === 'ide';
  if (title) title.textContent = agent?.title || 'Cursor agent';
  if (badge) badge.textContent = String(agent?.source || 'bridge').toUpperCase();
  if (detail) detail.classList.toggle('is-readonly', readOnly);
  if (readonlyNote) readonlyNote.hidden = !readOnly;
}

async function loadSession(agentId) {
  const agent = state.agents.find((row) => row.agent_id === agentId) || state.selectedAgent;
  const source = String(agent?.source || 'bridge').toLowerCase();
  const query = source === 'ide' ? '?source=ide' : '';
  const session = await readJson(await fetch(`/api/cursor/agents/${encodeURIComponent(agentId)}/session${query}`, {
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
  }));
  state.sessionMessages = Array.isArray(session.messages) ? session.messages : [];
  state.selectedAgent = { ...(agent || {}), ...session };
  setDetailChrome(state.selectedAgent);
  renderAgentPanel(state.sessionMessages, state.liveAssistantText);
  return session;
}

async function refreshStatus() {
  const response = await fetch('/api/cursor/status', { credentials: 'same-origin', headers: { Accept: 'application/json' } });
  const status = await readJson(response);
  setStatusPill(status);
  const connectPanel = byId('cursor-bridge-connect');
  if (connectPanel) connectPanel.hidden = status.configured === true;
  return status;
}

async function refreshAgents() {
  const status = await refreshStatus();
  if (!status.configured) {
    state.agents = [];
    renderAgentList([]);
    return;
  }
  const response = await fetch('/api/cursor/agents?source=all', { credentials: 'same-origin', headers: { Accept: 'application/json' } });
  const payload = await readJson(response);
  state.agents = Array.isArray(payload.items) ? payload.items : [];
  renderAgentList(state.agents);
  if (state.selectedAgentId) {
    const selected = state.agents.find((row) => row.agent_id === state.selectedAgentId);
    if (selected) state.selectedAgent = selected;
  }
}

function startPolling() {
  stopPolling();
  state.pollTimer = window.setInterval(() => {
    refreshAgents().catch(() => {});
    if (state.selectedAgentId && state.selectedAgent?.status === 'running') {
      loadSession(state.selectedAgentId).catch(() => {});
    }
  }, 5000);
}

function stopPolling() {
  if (state.pollTimer) {
    window.clearInterval(state.pollTimer);
    state.pollTimer = null;
  }
}

async function connectBridge(event) {
  event.preventDefault();
  const input = byId('cursor-bridge-api-key');
  const button = byId('cursor-bridge-connect-btn');
  const apiKey = String(input?.value || '').trim();
  if (!apiKey) return;
  if (button) button.disabled = true;
  try {
    await readJson(await fetch('/api/cursor/connect', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ api_key: apiKey }),
    }));
    if (input) input.value = '';
    await refreshAgents();
    startPolling();
  } catch (error) {
    const errorEl = byId('cursor-bridge-connect-error');
    if (errorEl) errorEl.textContent = error instanceof Error ? error.message : 'Connect failed.';
  } finally {
    if (button) button.disabled = false;
  }
}

async function disconnectBridge() {
  if (!window.confirm('Disconnect Cursor bridge and remove the saved API key?')) return;
  await readJson(await fetch('/api/cursor/connect', {
    method: 'DELETE',
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
  }));
  state.selectedAgentId = null;
  state.selectedAgent = null;
  state.sessionMessages = [];
  renderAgentPanel([]);
  await refreshAgents();
}

async function removeAgent(agent) {
  const agentId = String(agent?.agent_id || '').trim();
  if (!agentId) return;
  const label = String(agent?.title || 'this Cursor agent').trim();
  if (!window.confirm(`Remove "${label}" from the list?`)) return;
  const source = String(agent?.source || 'bridge').toLowerCase();
  const query = source === 'ide' ? '?source=ide' : '';
  await readJson(await fetch(`/api/cursor/agents/${encodeURIComponent(agentId)}${query}`, {
    method: 'DELETE',
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
  }));
  if (state.selectedAgentId === agentId) {
    state.selectedAgentId = null;
    state.selectedAgent = null;
    state.sessionMessages = [];
    renderAgentPanel([]);
  }
  if (state.streamAbort) {
    state.streamAbort.abort();
    state.streamAbort = null;
  }
  await refreshAgents();
}

async function createAgent() {
  const prompt = window.prompt('What should this Cursor agent work on?');
  if (!prompt || !prompt.trim()) return;
  const payload = await readJson(await fetch('/api/cursor/agents', {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ prompt: prompt.trim(), workspace: 'pandamonium' }),
  }));
  await refreshAgents();
  const agentId = payload?.agent?.agent_id;
  if (agentId) selectAgent(agentId, payload.run_id);
}

async function sendFollowUp() {
  if (!state.selectedAgentId) return;
  const input = byId('cursor-agent-prompt');
  const prompt = String(input?.value || '').trim();
  if (!prompt) return;
  const payload = await readJson(await fetch(`/api/cursor/agents/${encodeURIComponent(state.selectedAgentId)}/send`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ prompt }),
  }));
  if (input) input.value = '';
  await loadSession(state.selectedAgentId);
  await streamRun(state.selectedAgentId, payload.run_id);
}

async function selectAgent(agentId, runId = null) {
  state.selectedAgentId = agentId;
  state.liveAssistantText = '';
  renderAgentList(state.agents);
  const agent = state.agents.find((row) => row.agent_id === agentId) || null;
  state.selectedAgent = agent;
  await openCursorAgentOverlay(agentId, agent, runId);
}

async function streamRun(agentId, runId) {
  if (!agentId || !runId) return;
  if (state.streamAbort) state.streamAbort.abort();
  const controller = new AbortController();
  state.streamAbort = controller;
  state.liveAssistantText = '';
  const liveMessage = { role: 'assistant', live: true, blocks: [{ type: 'text', text: '' }] };
  const renderLive = () => {
    const messages = [...state.sessionMessages];
    if (!messages.length || !messages[messages.length - 1]?.live) messages.push(liveMessage);
    renderAgentPanel(messages, state.liveAssistantText);
  };
  renderLive();
  try {
    const response = await fetch(`/api/cursor/agents/${encodeURIComponent(agentId)}/runs/${encodeURIComponent(runId)}/stream`, {
      credentials: 'same-origin',
      signal: controller.signal,
      headers: { Accept: 'text/event-stream' },
    });
    if (!response.ok || !response.body) throw new Error('Cursor stream unavailable');
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      chunk.split('\n').forEach((line) => {
        if (!line.startsWith('data: ')) return;
        try {
          const payload = JSON.parse(line.slice(6));
          const message = payload.message;
          if (message && Array.isArray(message.content)) {
            message.content.forEach((block) => {
              if (block?.type === 'text' && block.text) state.liveAssistantText += block.text;
            });
          } else if (payload.text) {
            state.liveAssistantText += payload.text;
          }
          renderLive();
        } catch (_error) {
          /* ignore malformed chunks */
        }
      });
    }
  } catch (error) {
    if (!(error instanceof DOMException && error.name === 'AbortError')) {
      state.liveAssistantText = `${state.liveAssistantText}\n\n[stream ended: ${error instanceof Error ? error.message : 'error'}]`.trim();
      renderLive();
    }
  } finally {
    if (state.streamAbort === controller) state.streamAbort = null;
    await loadSession(agentId).catch(() => {});
    refreshAgents().catch(() => {});
  }
}

function expandSection() {
  const section = byId('cursor-bridge-section');
  if (!section) return;
  section.classList.remove('collapsed', 'section-just-collapsing');
  section.classList.add('section-just-expanded');
  window.setTimeout(() => section.classList.remove('section-just-expanded'), 700);
  persistSectionExpanded();
  const chevron = section.querySelector('.section-collapse-btn');
  chevron?.setAttribute('aria-expanded', 'true');
  refreshAgents().catch(() => {});
  startPolling();
}

function init() {
  initCursorAgentOverlay();
  byId('cursor-bridge-new-agent')?.addEventListener('click', (event) => {
    event.stopPropagation();
    createAgent().catch((error) => {
      window.alert(error instanceof Error ? error.message : 'Could not create agent.');
    });
  });
  byId('cursor-bridge-connect-form')?.addEventListener('submit', connectBridge);
  byId('cursor-bridge-disconnect-btn')?.addEventListener('click', () => disconnectBridge().catch((error) => {
    window.alert(error instanceof Error ? error.message : 'Disconnect failed.');
  }));
  refreshAgents().catch(() => {});
  startPolling();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init, { once: true });
} else {
  init();
}

export { expandSection, refreshAgents };
