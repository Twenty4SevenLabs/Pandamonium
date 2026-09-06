const byId = (id) => document.getElementById(id);

const state = {
  selectedAgentId: null,
  pollTimer: null,
  streamAbort: null,
  agents: [],
};

function relativeTime(unix) {
  const seconds = Math.max(0, Math.floor(Date.now() / 1000) - Number(unix || 0));
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 86400)}d`;
}

function setStatusPill(status) {
  const pill = byId('cursor-bridge-sidebar-status');
  if (!pill) return;
  const connected = status?.connected === true;
  const configured = status?.configured === true;
  pill.dataset.state = connected ? 'connected' : configured ? 'warning' : 'disconnected';
  pill.setAttribute('aria-label', connected ? 'Connected' : configured ? 'Reconnect needed' : 'Disconnected');
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

function renderStreamText(text) {
  const stream = byId('cursor-agent-stream');
  if (!stream) return;
  stream.textContent = text || '';
}

async function refreshStatus() {
  const response = await fetch('/api/cursor/status', { credentials: 'same-origin', headers: { Accept: 'application/json' } });
  const status = await readJson(response);
  setStatusPill(status);
  const connectPanel = byId('cursor-bridge-connect');
  const detail = byId('cursor-agent-detail');
  if (connectPanel) connectPanel.hidden = status.configured === true;
  if (detail) detail.hidden = status.configured !== true;
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
}

function startPolling() {
  stopPolling();
  state.pollTimer = window.setInterval(() => {
    refreshAgents().catch(() => {});
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
  renderStreamText('');
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
    renderStreamText('');
    const detail = byId('cursor-agent-detail');
    if (detail) detail.hidden = false;
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
  await streamRun(state.selectedAgentId, payload.run_id);
}

function selectAgent(agentId, runId = null) {
  state.selectedAgentId = agentId;
  renderAgentList(state.agents);
  const agent = state.agents.find((row) => row.agent_id === agentId);
  const title = byId('cursor-agent-detail-title');
  const detail = byId('cursor-agent-detail');
  if (detail) detail.hidden = false;
  if (title) title.textContent = agent?.title || 'Cursor agent';
  renderStreamText('');
  if (runId || agent?.run_id) streamRun(agentId, runId || agent.run_id);
}

async function streamRun(agentId, runId) {
  if (!agentId || !runId) return;
  if (state.streamAbort) state.streamAbort.abort();
  const controller = new AbortController();
  state.streamAbort = controller;
  let buffer = '';
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
              if (block?.type === 'text' && block.text) buffer += block.text;
            });
          } else if (payload.text) {
            buffer += payload.text;
          }
          renderStreamText(buffer);
        } catch (_error) {
          /* ignore malformed chunks */
        }
      });
    }
  } catch (error) {
    if (!(error instanceof DOMException && error.name === 'AbortError')) {
      renderStreamText(`${buffer}\n\n[stream ended: ${error instanceof Error ? error.message : 'error'}]`.trim());
    }
  } finally {
    if (state.streamAbort === controller) state.streamAbort = null;
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
  byId('cursor-agent-send-btn')?.addEventListener('click', () => sendFollowUp().catch((error) => {
    window.alert(error instanceof Error ? error.message : 'Send failed.');
  }));
  refreshAgents().catch(() => {});
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init, { once: true });
} else {
  init();
}

export { expandSection, refreshAgents };
