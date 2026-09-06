const byId = (id) => document.getElementById(id);

const overlayState = {
  agentId: null,
  agent: null,
  messages: [],
  streamAbort: null,
  liveStreamEvents: [],
  sending: false,
};

function normalizeStreamEvent(raw) {
  if (!raw || typeof raw !== 'object') return null;
  const eventType = String(raw.type || '').toLowerCase();
  if (eventType === 'error') {
    const text = String(raw.text || raw.message || 'error').trim();
    return text ? { type: 'error', text } : null;
  }
  const message = raw.message;
  if (message && typeof message === 'object') {
    const nested = normalizeMessageDict(message);
    if (nested) return nested;
  }
  if (typeof message === 'string' && message.trim()) {
    return { type: 'text', text: message.trim() };
  }
  const update = raw.update;
  if (update && typeof update === 'object') {
    const nested = normalizeUpdateDict(update);
    if (nested) return nested;
  }
  if (['thinking', 'tool', 'shell', 'usage', 'artifact', 'status'].includes(eventType)) {
    return { ...raw, type: eventType };
  }
  return null;
}

function normalizeMessageDict(message) {
  const role = String(message.role || '').toLowerCase();
  const content = message.content;
  if (Array.isArray(content)) {
    const parts = [];
    for (const block of content) {
      if (!block || typeof block !== 'object') continue;
      const blockType = String(block.type || '');
      if (blockType === 'text') {
        const text = String(block.text || '');
        if (text) parts.push(text);
      } else if (blockType === 'tool_use') {
        return {
          type: 'tool',
          name: String(block.name || 'tool'),
          input: block.input && typeof block.input === 'object' ? block.input : {},
          summary: String(block.name || 'tool'),
          status: 'completed',
        };
      }
    }
    if (parts.length) return { type: 'text', text: parts.join('') };
  }
  if (role === 'assistant' && typeof message.text === 'string' && message.text.trim()) {
    return { type: 'text', text: message.text.trim() };
  }
  return null;
}

function normalizeUpdateDict(update) {
  const kind = String(update.type || update.updateType || '').toLowerCase();
  if (kind.includes('textdelta') || kind === 'text_delta') {
    const text = String(update.text || update.delta || '');
    return text ? { type: 'text', text } : null;
  }
  if (kind.includes('thinking')) {
    const text = String(update.text || update.delta || '');
    return text ? { type: 'thinking', text, collapsed: true } : null;
  }
  if (kind.includes('toolcallstarted') || kind === 'tool_call_started') {
    return {
      type: 'tool',
      name: String(update.name || update.toolName || 'tool'),
      input: update.input && typeof update.input === 'object' ? update.input : {},
      summary: String(update.name || update.toolName || 'tool'),
      status: 'running',
    };
  }
  if (kind.includes('toolcallcompleted') || kind === 'tool_call_completed') {
    return {
      type: 'tool',
      name: String(update.name || update.toolName || 'tool'),
      input: update.input && typeof update.input === 'object' ? update.input : {},
      output: update.output,
      summary: String(update.name || update.toolName || 'tool'),
      status: 'completed',
    };
  }
  if (kind.includes('shelloutput')) {
    return { type: 'shell', text: String(update.text || update.delta || update.output || '') };
  }
  if (kind.endsWith('usage') || kind.includes('usage')) {
    return { type: 'usage', usage: update.usage && typeof update.usage === 'object' ? update.usage : update };
  }
  if (kind.includes('artifact')) {
    return {
      type: 'artifact',
      name: String(update.name || 'artifact'),
      url: String(update.url || update.path || ''),
    };
  }
  if (kind.includes('status')) {
    return { type: 'status', text: String(update.text || update.status || '') };
  }
  return null;
}

function eventsToParityBlocks(events) {
  const blocks = [];
  const textBuffer = [];
  const thinkingBuffer = [];
  const displayTypes = new Set(['text', 'thinking', 'tool', 'shell', 'artifact', 'error']);
  const flushText = () => {
    if (!textBuffer.length) return;
    const text = textBuffer.join('').trim();
    textBuffer.length = 0;
    if (text) blocks.push({ type: 'text', text });
  };
  const flushThinking = () => {
    if (!thinkingBuffer.length) return;
    const text = thinkingBuffer.join('').trim();
    thinkingBuffer.length = 0;
    if (text) blocks.push({ type: 'thinking', text, collapsed: true });
  };
  for (const raw of Array.isArray(events) ? events : []) {
    const block = normalizeStreamEvent(raw);
    if (!block) continue;
    const kind = String(block.type || '');
    if (kind === 'text') {
      const delta = String(block.text || '');
      if (delta) textBuffer.push(delta);
      continue;
    }
    if (kind === 'thinking') {
      const delta = String(block.text || block.delta || '');
      if (delta) thinkingBuffer.push(delta);
      continue;
    }
    flushText();
    flushThinking();
    if (displayTypes.has(kind)) blocks.push(block);
  }
  flushText();
  flushThinking();
  return blocks;
}

function readJson(response) {
  return response.json().catch(() => ({})).then((body) => {
    if (!response.ok) {
      const detail = typeof body.detail === 'string' ? body.detail : (body.error || 'Cursor bridge request failed');
      throw new Error(detail);
    }
    return body;
  });
}

function inferAgentSource(agent, agentId = null) {
  const explicit = String(agent?.source || '').toLowerCase();
  if (explicit) return explicit;
  const id = String(agentId || agent?.agent_id || '');
  if (id.startsWith('agent-')) return 'bridge';
  return 'ide';
}

function sessionQuery(agent, agentId = null) {
  const params = new URLSearchParams();
  const source = inferAgentSource(agent, agentId);
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

function toolActivityLabel(block) {
  const name = String(block?.summary || block?.name || 'Tool');
  if (block?.type === 'shell') {
    const text = String(block?.text || '').trim();
    return text ? `Shell ${text.split('\n')[0].slice(0, 120)}` : 'Shell';
  }
  return name;
}

function partitionAssistantBlocks(blocks) {
  const text = [];
  const thinking = [];
  const activity = [];
  const visible = [];
  for (const block of Array.isArray(blocks) ? blocks : []) {
    const type = String(block?.type || '');
    if (type === 'text') text.push(block);
    else if (type === 'thinking') thinking.push(block);
    else if (type === 'tool' || type === 'shell') activity.push(block);
    else if (type === 'error' || type === 'artifact') visible.push(block);
  }
  return { text, thinking, activity, visible };
}

function renderActivityItem(block) {
  const item = document.createElement('div');
  item.className = 'cursor-overlay-activity-item';
  const title = document.createElement('div');
  title.className = 'cursor-overlay-activity-item-title';
  title.textContent = toolActivityLabel(block);
  if (block?.status === 'running') title.dataset.state = 'running';
  item.append(title);
  const detail = document.createElement('pre');
  detail.className = 'cursor-overlay-activity-item-detail';
  if (block?.type === 'shell') {
    detail.textContent = String(block.text || '');
  } else {
    detail.textContent = JSON.stringify({ input: block.input, output: block.output }, null, 2);
  }
  item.append(detail);
  return item;
}

function renderCollapsedGroup(className, summaryText, blocks, renderItem) {
  if (!blocks.length) return null;
  const wrap = document.createElement('details');
  wrap.className = className;
  wrap.open = false;
  const summary = document.createElement('summary');
  summary.textContent = summaryText;
  if (blocks.some((block) => block?.status === 'running')) summary.dataset.state = 'running';
  const list = document.createElement('div');
  list.className = `${className}-list`;
  blocks.forEach((block) => list.append(renderItem(block)));
  wrap.append(summary, list);
  return wrap;
}

function renderThinkingGroup(blocks) {
  if (!blocks.length) return null;
  const combined = blocks.map((block) => String(block.text || '').trim()).filter(Boolean).join('\n\n');
  if (!combined) return null;
  return renderCollapsedGroup(
    'cursor-overlay-thinking-box',
    blocks.length > 1 ? `Thinking (${blocks.length})` : 'Thinking',
    [{ text: combined }],
    (block) => {
      const item = document.createElement('div');
      item.className = 'cursor-overlay-thinking-body';
      item.textContent = String(block.text || '');
      return item;
    },
  );
}

function renderActivityGroup(blocks) {
  if (!blocks.length) return null;
  const running = blocks.some((block) => block?.status === 'running');
  const label = running
    ? `Tool activity (${blocks.length})…`
    : `Tool activity (${blocks.length})`;
  return renderCollapsedGroup('cursor-overlay-activity-box', label, blocks, renderActivityItem);
}

function renderTextBlock(block) {
  const el = document.createElement('div');
  el.className = 'cursor-overlay-block cursor-overlay-block-text';
  const body = document.createElement('div');
  body.className = 'cursor-overlay-block-body cursor-overlay-reply-text';
  body.textContent = String(block.text || '');
  el.append(body);
  return el;
}

function renderBlock(block) {
  const type = String(block?.type || 'text');
  if (type === 'usage' || type === 'status' || type === 'thinking' || type === 'tool' || type === 'shell') {
    return null;
  }
  if (type === 'text') return renderTextBlock(block);
  const el = document.createElement('div');
  el.className = `cursor-overlay-block cursor-overlay-block-${type}`;
  const body = document.createElement('div');
  body.className = 'cursor-overlay-block-body';
  body.textContent = blockText([block]);
  el.append(body);
  return el;
}

function renderAssistantBody(blocks) {
  const body = document.createElement('div');
  body.className = 'cursor-overlay-msg-body';
  const { text, thinking, activity, visible } = partitionAssistantBlocks(blocks);
  const thinkingBox = renderThinkingGroup(thinking);
  const activityBox = renderActivityGroup(activity);
  if (thinkingBox) body.append(thinkingBox);
  if (activityBox) body.append(activityBox);
  if (text.length) {
    text.forEach((block) => body.append(renderTextBlock(block)));
  } else if (!thinkingBox && !activityBox && !visible.length) {
    body.textContent = '';
  }
  visible.forEach((block) => {
    const node = renderBlock(block);
    if (node) body.append(node);
  });
  return body;
}

function renderMessage(message, liveBlocks = null) {
  const role = message?.role === 'user' ? 'user' : 'assistant';
  const wrap = document.createElement('article');
  wrap.className = `cursor-overlay-msg cursor-overlay-msg-${role}`;
  const label = document.createElement('div');
  label.className = 'cursor-overlay-msg-role';
  label.textContent = role === 'user' ? 'You' : 'Agent';
  const blocks = message?.live && Array.isArray(liveBlocks) ? liveBlocks : (Array.isArray(message?.blocks) ? message.blocks : []);
  if (role === 'user') {
    const body = document.createElement('div');
    body.className = 'cursor-overlay-msg-body';
    const text = blocks
      .filter((block) => String(block?.type || '') === 'text')
      .map((block) => String(block.text || '').trim())
      .filter(Boolean)
      .join('\n\n');
    body.textContent = text || '(empty message)';
    wrap.append(label, body);
  } else {
    wrap.append(label, renderAssistantBody(blocks));
  }
  return wrap;
}

function renderPanel(messages, liveBlocks = null) {
  const panel = byId('cursor-agent-overlay-panel');
  if (!panel) return;
  panel.replaceChildren();
  const rows = Array.isArray(messages) ? messages : [];
  if (!rows.length && !liveBlocks?.length) {
    const empty = document.createElement('div');
    empty.className = 'cursor-overlay-empty';
    empty.textContent = 'Loading session…';
    panel.appendChild(empty);
    return;
  }
  rows.forEach((message) => panel.appendChild(renderMessage(message, message?.live ? liveBlocks : null)));
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
  const query = sessionQuery(agent, agentId);
  const session = await readJson(await fetch(`/api/cursor/agents/${encodeURIComponent(agentId)}/session${query}`, {
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
  }));
  overlayState.agent = {
    ...(agent || {}),
    ...session,
    agent_id: agentId,
    source: session?.source || agent?.source || inferAgentSource(agent, agentId),
    mirror_url: session?.mirror_url || agent?.mirror_url,
  };
  overlayState.messages = Array.isArray(session.messages) ? session.messages : [];
  setHeader(overlayState.agent);
  renderPanel(overlayState.messages, null);
  return session;
}

function parseSsePayload(line) {
  if (!line.startsWith('data: ')) return null;
  try {
    return JSON.parse(line.slice(6));
  } catch (_error) {
    return null;
  }
}

async function streamRun(agentId, runId, agent) {
  if (!agentId || !runId) return;
  if (overlayState.streamAbort) overlayState.streamAbort.abort();
  const controller = new AbortController();
  overlayState.streamAbort = controller;
  overlayState.liveStreamEvents = [];
  const liveMessage = { role: 'assistant', live: true, blocks: [] };
  const renderLive = () => {
    const liveBlocks = eventsToParityBlocks(overlayState.liveStreamEvents);
    const messages = [...overlayState.messages];
    if (!messages.length || !messages[messages.length - 1]?.live) messages.push(liveMessage);
    renderPanel(messages, liveBlocks);
  };
  renderLive();
  const q = sessionQuery(agent);
  let sseBuffer = '';
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
      sseBuffer += decoder.decode(value, { stream: true });
      const lines = sseBuffer.split('\n');
      sseBuffer = lines.pop() || '';
      for (const line of lines) {
        const payload = parseSsePayload(line.trim());
        if (!payload) continue;
        overlayState.liveStreamEvents.push(payload);
        renderLive();
      }
    }
    if (sseBuffer.trim()) {
      const payload = parseSsePayload(sseBuffer.trim());
      if (payload) {
        overlayState.liveStreamEvents.push(payload);
        renderLive();
      }
    }
  } catch (error) {
    if (!(error instanceof DOMException && error.name === 'AbortError')) {
      overlayState.liveStreamEvents.push({
        type: 'error',
        text: error instanceof Error ? error.message : 'stream error',
      });
      renderLive();
    }
  } finally {
    if (overlayState.streamAbort === controller) overlayState.streamAbort = null;
    overlayState.liveStreamEvents = [];
    await loadSession(agentId, overlayState.agent).catch(() => {});
  }
}

async function sendFollowUp() {
  const agentId = overlayState.agentId;
  const agent = overlayState.agent;
  if (!agentId || overlayState.sending) return;
  const input = byId('cursor-agent-overlay-prompt');
  const prompt = String(input?.value || '').trim();
  if (!prompt) return;
  overlayState.sending = true;
  if (input) {
    input.value = '';
    input.disabled = true;
  }
  const sendBtn = byId('cursor-agent-overlay-send');
  if (sendBtn) sendBtn.disabled = true;
  try {
    const source = inferAgentSource(agent, agentId);
    const body = {
      prompt,
      source,
      mirror_url: agent?.mirror_url,
      workspace: agent?.workspace || 'pandamonium',
      title: agent?.title,
    };
    const q = sessionQuery({ ...(agent || {}), source }, agentId);
    const payload = await readJson(await fetch(`/api/cursor/agents/${encodeURIComponent(agentId)}/send${q}`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(body),
    }));
    await loadSession(agentId, overlayState.agent);
    await streamRun(agentId, payload.run_id, overlayState.agent);
  } finally {
    overlayState.sending = false;
    if (input) input.disabled = false;
    if (sendBtn) sendBtn.disabled = false;
  }
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
  overlayState.liveStreamEvents = [];
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

function onPromptKeyDown(event) {
  if (event.key !== 'Enter' || event.shiftKey) return;
  event.preventDefault();
  sendFollowUp().catch((error) => window.alert(error.message));
}

export function initCursorAgentOverlay() {
  byId('cursor-agent-overlay-close')?.addEventListener('click', closeCursorAgentOverlay);
  byId('cursor-agent-overlay-send')?.addEventListener('click', () => sendFollowUp().catch((error) => window.alert(error.message)));
  byId('cursor-agent-overlay-stop')?.addEventListener('click', () => stopRun().catch((error) => window.alert(error.message)));
  byId('cursor-agent-overlay-backdrop')?.addEventListener('click', closeCursorAgentOverlay);
  byId('cursor-agent-overlay-prompt')?.addEventListener('keydown', onPromptKeyDown);
  document.addEventListener('keydown', onKeyDown);
}
