const byId = (id) => document.getElementById(id);

const overlayState = {
  agentId: null,
  agent: null,
  messages: [],
  streamAbort: null,
  liveAssistantText: '',
};

function readJson(response) {
  return response.json().catch(() => ({})).then((body) => {
    if (!response.ok) {
      const detail = typeof body.detail === 'string' ? body.detail : (body.error || 'Cursor bridge request failed');
      throw new Error(detail);
    }
    return body;
  });
}

function sessionQuery(agent) {
  const params = new URLSearchParams();
  const source = String(agent?.source || 'bridge').toLowerCase();
  if (source) params.set('source', source);
  if (agent?.mirror_url) params.set('mirror_url', String(agent.mirror_url));
  const query = params.toString();
  return query ? `?${query}` : '';
}

function streamQuery(agent) {
  return sessionQuery(agent).replace(/^\?/, '') ? `?${sessionQuery(agent).slice(1)}` : '';
}

function blockText(blocks) {
  return (Array.isArray(blocks) ? blocks : [])
    .map((block) => {
      const type = String(block?.type || '');
      if (type === 'text') return String(block.text || '');
      if (type === 'thinking') return `[thinking] ${block.text || ''}`;
      if (type === 'tool') return `[tool] ${block.summary || block.name || 'tool'}`;
      if (type === 'shell') return `[shell] ${block.text || ''}`;
      if (type === 'usage') return `[usage] ${JSON.stringify(block.usage || {})}`;
      if (type === 'artifact') return `[artifact] ${block.name || ''} ${block.url || ''}`;
      if (type === 'error') return `[error] ${block.text || ''}`;
      if (type === 'status') return `[status] ${block.text || ''}`;
      return '';
    })
    .filter(Boolean)
    .join('\n\n');
}

function renderBlock(block) {
  const type = String(block?.type || 'text');
  const el = document.createElement('div');
  el.className = `cursor-overlay-block cursor-overlay-block-${type}`;
  if (type === 'thinking') {
    const details = document.createElement('details');
    details.open = false;
    const summary = document.createElement('summary');
    summary.textContent = 'Thinking';
    const body = document.createElement('div');
    body.className = 'cursor-overlay-block-body';
    body.textContent = String(block.text || '');
    details.append(summary, body);
    el.append(details);
    return el;
  }
  if (type === 'tool') {
    const details = document.createElement('details');
    const summary = document.createElement('summary');
    summary.textContent = String(block.summary || block.name || 'Tool');
    if (block.status === 'running') summary.dataset.state = 'running';
    const body = document.createElement('pre');
    body.className = 'cursor-overlay-block-body';
    body.textContent = JSON.stringify({ input: block.input, output: block.output }, null, 2);
    details.append(summary, body);
    el.append(details);
    return el;
  }
  const body = document.createElement('div');
  body.className = 'cursor-overlay-block-body';
  body.textContent = type === 'text' ? String(block.text || '') : blockText([block]);
  el.append(body);
  return el;
}

function renderMessage(message, liveText = '') {
  const role = message?.role === 'user' ? 'user' : 'assistant';
  const wrap = document.createElement('article');
  wrap.className = `cursor-overlay-msg cursor-overlay-msg-${role}`;
  const label = document.createElement('div');
  label.className = 'cursor-overlay-msg-role';
  label.textContent = role === 'user' ? 'You' : 'Agent';
  const body = document.createElement('div');
  body.className = 'cursor-overlay-msg-body';
  const blocks = Array.isArray(message?.blocks) ? message.blocks : [];
  if (message?.live && liveText) {
    const p = document.createElement('div');
    p.className = 'cursor-overlay-block-body';
    p.textContent = liveText || 'Thinking…';
    body.append(p);
  } else if (blocks.length) {
    blocks.forEach((block) => body.append(renderBlock(block)));
  } else {
    body.textContent = blockText(blocks);
  }
  wrap.append(label, body);
  return wrap;
}

function renderPanel(messages, liveText = '') {
  const panel = byId('cursor-agent-overlay-panel');
  if (!panel) return;
  panel.replaceChildren();
  const rows = Array.isArray(messages) ? messages : [];
  if (!rows.length && !liveText) {
    const empty = document.createElement('div');
    empty.className = 'cursor-overlay-empty';
    empty.textContent = 'Loading session…';
    panel.appendChild(empty);
    return;
  }
  rows.forEach((message) => panel.appendChild(renderMessage(message, message?.live ? liveText : '')));
  panel.scrollTop = panel.scrollHeight;
}

function setHeader(session) {
  const title = byId('cursor-agent-overlay-title');
  const sourceBadge = byId('cursor-agent-overlay-source');
  const nodeBadge = byId('cursor-agent-overlay-node');
  const modelBadge = byId('cursor-agent-overlay-model');
  if (title) title.textContent = session?.title || 'Cursor agent';
  if (sourceBadge) sourceBadge.textContent = String(session?.source || 'bridge').toUpperCase();
  if (nodeBadge) nodeBadge.textContent = session?.execution_host ? `Running on ${session.execution_host}` : '';
  if (modelBadge) modelBadge.textContent = 'Composer 2.5 · local · fast off';
  const compose = byId('cursor-agent-overlay-compose');
  if (compose) compose.hidden = session?.can_send === false;
}

async function loadSession(agentId, agent) {
  const query = sessionQuery(agent);
  const session = await readJson(await fetch(`/api/cursor/agents/${encodeURIComponent(agentId)}/session${query}`, {
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
  }));
  overlayState.agent = { ...(agent || {}), ...session };
  overlayState.messages = Array.isArray(session.messages) ? session.messages : [];
  setHeader(overlayState.agent);
  renderPanel(overlayState.messages, overlayState.liveAssistantText);
  return session;
}

async function streamRun(agentId, runId, agent) {
  if (!agentId || !runId) return;
  if (overlayState.streamAbort) overlayState.streamAbort.abort();
  const controller = new AbortController();
  overlayState.streamAbort = controller;
  overlayState.liveAssistantText = '';
  const liveMessage = { role: 'assistant', live: true, blocks: [{ type: 'text', text: '' }] };
  const renderLive = () => {
    const messages = [...overlayState.messages];
    if (!messages.length || !messages[messages.length - 1]?.live) messages.push(liveMessage);
    renderPanel(messages, overlayState.liveAssistantText);
  };
  renderLive();
  const q = sessionQuery(agent);
  try {
    const response = await fetch(
      `/api/cursor/agents/${encodeURIComponent(agentId)}/runs/${encodeURIComponent(runId)}/stream${q}`,
      { credentials: 'same-origin', signal: controller.signal, headers: { Accept: 'text/event-stream' } },
    );
    if (!response.ok || !response.body) throw new Error('Cursor stream unavailable');
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      decoder.decode(value, { stream: true }).split('\n').forEach((line) => {
        if (!line.startsWith('data: ')) return;
        try {
          const payload = JSON.parse(line.slice(6));
          const message = payload.message;
          if (message && Array.isArray(message.content)) {
            message.content.forEach((block) => {
              if (block?.type === 'text' && block.text) overlayState.liveAssistantText += block.text;
            });
          } else if (payload.text) {
            overlayState.liveAssistantText += payload.text;
          } else if (payload.block?.text) {
            overlayState.liveAssistantText += payload.block.text;
          }
          renderLive();
        } catch (_error) {
          /* ignore malformed chunks */
        }
      });
    }
  } catch (error) {
    if (!(error instanceof DOMException && error.name === 'AbortError')) {
      overlayState.liveAssistantText = `${overlayState.liveAssistantText}\n\n[stream ended: ${error instanceof Error ? error.message : 'error'}]`.trim();
      renderLive();
    }
  } finally {
    if (overlayState.streamAbort === controller) overlayState.streamAbort = null;
    await loadSession(agentId, overlayState.agent).catch(() => {});
  }
}

async function sendFollowUp() {
  const agentId = overlayState.agentId;
  const agent = overlayState.agent;
  if (!agentId) return;
  const input = byId('cursor-agent-overlay-prompt');
  const prompt = String(input?.value || '').trim();
  if (!prompt) return;
  const body = {
    prompt,
    source: agent?.source,
    mirror_url: agent?.mirror_url,
    workspace: agent?.workspace || 'pandamonium',
    title: agent?.title,
  };
  const q = sessionQuery(agent);
  const payload = await readJson(await fetch(`/api/cursor/agents/${encodeURIComponent(agentId)}/send${q}`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(body),
  }));
  if (input) input.value = '';
  await loadSession(agentId, overlayState.agent);
  await streamRun(agentId, payload.run_id, overlayState.agent);
}

async function stopRun() {
  const agent = overlayState.agent;
  const agentId = overlayState.agentId;
  const runId = agent?.run_id;
  if (!agentId || !runId) return;
  const q = sessionQuery(agent);
  await readJson(await fetch(`/api/cursor/agents/${encodeURIComponent(agentId)}/runs/${encodeURIComponent(runId)}/cancel${q}`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
  }));
  if (overlayState.streamAbort) {
    overlayState.streamAbort.abort();
    overlayState.streamAbort = null;
  }
  await loadSession(agentId, agent);
}

export function closeCursorAgentOverlay() {
  const overlay = byId('cursor-agent-overlay');
  if (!overlay) return;
  overlay.hidden = true;
  document.body.classList.remove('cursor-agent-overlay-open');
  if (overlayState.streamAbort) {
    overlayState.streamAbort.abort();
    overlayState.streamAbort = null;
  }
  overlayState.agentId = null;
  overlayState.agent = null;
  overlayState.messages = [];
  overlayState.liveAssistantText = '';
}

export async function openCursorAgentOverlay(agentId, agent, runId = null) {
  const overlay = byId('cursor-agent-overlay');
  if (!overlay) return;
  overlayState.agentId = agentId;
  overlayState.agent = agent || null;
  overlay.hidden = false;
  document.body.classList.add('cursor-agent-overlay-open');
  renderPanel([], '');
  setHeader(agent || {});
  try {
    const session = await loadSession(agentId, agent);
    const activeRunId = runId || session?.run_id || agent?.run_id;
    if (activeRunId && (session?.status === 'running' || runId)) {
      await streamRun(agentId, activeRunId, overlayState.agent);
    }
  } catch (error) {
    renderPanel([], '');
    const panel = byId('cursor-agent-overlay-panel');
    if (panel) {
      panel.replaceChildren();
      const empty = document.createElement('div');
      empty.className = 'cursor-overlay-empty';
      empty.textContent = error instanceof Error ? error.message : 'Could not load session.';
      panel.appendChild(empty);
    }
  }
}

function onKeyDown(event) {
  if (event.key === 'Escape') closeCursorAgentOverlay();
}

export function initCursorAgentOverlay() {
  byId('cursor-agent-overlay-close')?.addEventListener('click', closeCursorAgentOverlay);
  byId('cursor-agent-overlay-send')?.addEventListener('click', () => sendFollowUp().catch((error) => window.alert(error.message)));
  byId('cursor-agent-overlay-stop')?.addEventListener('click', () => stopRun().catch((error) => window.alert(error.message)));
  byId('cursor-agent-overlay-backdrop')?.addEventListener('click', closeCursorAgentOverlay);
  document.addEventListener('keydown', onKeyDown);
}
