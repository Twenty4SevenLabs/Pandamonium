const params = new URLSearchParams(window.location.search);
const path = params.get('path') || '';
const titleEl = document.getElementById('canvas-title');
const pathEl = document.getElementById('canvas-path');
const frame = document.getElementById('canvas-frame');
const fallback = document.getElementById('canvas-fallback');
const statusEl = document.getElementById('canvas-status');
const fallbackTitle = document.getElementById('canvas-fallback-title');
const fallbackCopy = document.getElementById('canvas-fallback-copy');
const copyBtn = document.getElementById('copy-path');
const reloadBtn = document.getElementById('reload-canvas');
const openPandaBtn = document.getElementById('open-panda');

function setStatus(text) {
  if (statusEl) statusEl.textContent = text;
}

function showFatal(title, copy, status) {
  if (fallbackTitle) fallbackTitle.textContent = title;
  if (fallbackCopy) fallbackCopy.textContent = copy;
  setStatus(status);
}

function canvasTitleFromPath(value) {
  return value.split('/').pop()?.replace(/\.canvas\.tsx$/, '').replace(/[-_]+/g, ' ') || 'Cursor Canvas';
}

async function fetchCanvasPayload() {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch('/api/cursor/canvas/open', {
      method: 'POST',
      credentials: 'same-origin',
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ path }),
    });
    const payload = await response.json().catch(() => ({}));
    if (response.status === 401 || response.status === 403) {
      throw new Error('Panda session expired. Reload the main Panda tab and sign in again.');
    }
    if (!response.ok) {
      const detail = payload?.detail || payload?.error || 'Could not register this canvas.';
      throw new Error(typeof detail === 'string' ? detail : 'Could not register this canvas.');
    }
    return payload;
  } finally {
    window.clearTimeout(timer);
  }
}

async function loadCanvas() {
  setStatus('Registering canvas…');
  const payload = await fetchCanvasPayload();
  if (payload.title && titleEl) titleEl.textContent = payload.title;
  const embedUrl = String(payload.embed_url || '').trim();
  if (embedUrl) {
    setStatus('Live canvas connected');
    fallback?.classList.add('hidden');
    frame.src = embedUrl;
    frame?.classList.remove('hidden');
    return;
  }
  const registration = payload.registration;
  const registrationHint = registration && registration.registered === false
    ? ` Canvas server: ${registration.reason || 'register failed'}.`
    : '';
  showFatal(
    `${payload.title || canvasTitleFromPath(path)} is ready`,
    `The canvas file is saved.${registrationHint} Reload the Cursor window once if live embed stays unavailable, then click Open Canvas again.`,
    payload.canvas_server ? 'Saved — waiting for live server' : 'Saved — live server not configured',
  );
}

function bindButtons() {
  copyBtn?.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(path);
      copyBtn.textContent = 'Copied';
      window.setTimeout(() => { copyBtn.textContent = 'Copy path'; }, 1200);
    } catch (_error) {
      window.prompt('Copy canvas path', path);
    }
  });

  reloadBtn?.addEventListener('click', () => {
    frame?.classList.add('hidden');
    frame?.removeAttribute('src');
    fallback?.classList.remove('hidden');
    loadCanvas().catch((error) => {
      showFatal('Canvas load failed', error instanceof Error ? error.message : 'Canvas load failed', 'Load failed');
    });
  });

  openPandaBtn?.addEventListener('click', () => {
    if (window.opener && !window.opener.closed) {
      try {
        window.opener.focus();
      } catch (_error) {
        /* ignore cross-window focus failures */
      }
      return;
    }
    window.open('/', 'panda-main');
  });
}

function boot() {
  bindButtons();
  if (!path) {
    showFatal(
      'No canvas path supplied',
      'Return to Panda and use the Open Canvas button on the agent reply.',
      'Missing path',
    );
    return;
  }
  if (pathEl) pathEl.textContent = path;
  if (titleEl) titleEl.textContent = canvasTitleFromPath(path);
  loadCanvas().catch((error) => {
    const message = error instanceof Error ? error.message : 'Canvas load failed';
    showFatal('Canvas registration failed', message, 'Registration failed');
  });
}

boot();
