const CANVAS_PATH_RE = /(?:~\/[^\s"'<>]+|\/[^\s"'<>]+|\b[\w.-]+(?:\/[\w.-]+)+)\.canvas\.tsx/g;
const canvasWindows = new Map();
const autoOpenedPaths = new Set();

function hashPath(path) {
  let hash = 0;
  for (let i = 0; i < path.length; i += 1) {
    hash = ((hash << 5) - hash + path.charCodeAt(i)) | 0;
  }
  return Math.abs(hash).toString(36);
}

export function normalizeCanvasPath(value) {
  const path = String(value || '').trim();
  if (!path || !path.endsWith('.canvas.tsx')) return '';
  return path;
}

function canvasWindowName(path) {
  return `panda-cursor-canvas-${hashPath(path)}`;
}

function canvasPopupFeatures() {
  return 'popup=yes,width=1280,height=900,resizable=yes,scrollbars=yes';
}

function sessionAutoKey(path) {
  return `panda-canvas-auto:${path}`;
}

function rememberCanvasPath(path, meta = {}) {
  const normalized = normalizeCanvasPath(path);
  if (!normalized) return '';
  try {
    const raw = sessionStorage.getItem('panda-canvas-paths');
    const store = raw ? JSON.parse(raw) : {};
    store[normalized] = {
      title: String(meta.title || store[normalized]?.title || 'Canvas'),
      updated_at: Date.now(),
    };
    sessionStorage.setItem('panda-canvas-paths', JSON.stringify(store));
  } catch (_error) {
    /* ignore storage failures */
  }
  return normalized;
}

export function listKnownCanvasPaths() {
  try {
    const raw = sessionStorage.getItem('panda-canvas-paths');
    const store = raw ? JSON.parse(raw) : {};
    return Object.entries(store)
      .map(([path, meta]) => ({ path, title: meta?.title || 'Canvas' }))
      .sort((a, b) => String(a.path).localeCompare(String(b.path)));
  } catch (_error) {
    return [];
  }
}

export function extractCanvasPathsFromText(text) {
  const found = new Set();
  const source = String(text || '');
  CANVAS_PATH_RE.lastIndex = 0;
  let match = CANVAS_PATH_RE.exec(source);
  while (match) {
    const normalized = normalizeCanvasPath(match[0]);
    if (normalized) found.add(normalized);
    match = CANVAS_PATH_RE.exec(source);
  }
  return [...found];
}

export function registerCanvasPaths(paths, meta = {}) {
  const normalized = [];
  for (const raw of Array.isArray(paths) ? paths : []) {
    const path = rememberCanvasPath(raw, meta);
    if (path) normalized.push(path);
  }
  return normalized;
}

export function openCursorCanvasPopup(payload = {}, options = {}) {
  const path = rememberCanvasPath(payload?.path, payload);
  if (!path) return null;

  const force = options.force === true;
  const auto = options.auto === true;

  const existing = canvasWindows.get(path);
  if (existing && !existing.closed) {
    try {
      existing.focus();
    } catch (_error) {
      /* ignore focus failures */
    }
    return existing;
  }

  if (auto) {
    if (autoOpenedPaths.has(path)) return null;
    try {
      if (sessionStorage.getItem(sessionAutoKey(path))) return null;
      // Mark before window.open so SSE replays do not spam popups when blocked.
      sessionStorage.setItem(sessionAutoKey(path), String(Date.now()));
    } catch (_error) {
      /* ignore storage failures */
    }
    autoOpenedPaths.add(path);
  }

  const popupUrl = String(
    payload?.popup_url || `/static/cursor-canvas-popup.html?path=${encodeURIComponent(path)}`,
  );
  const win = window.open(popupUrl, canvasWindowName(path), canvasPopupFeatures());
  if (!win) return null;

  canvasWindows.set(path, win);
  return win;
}

export function handleCanvasOpenEvent(payload = {}) {
  if (String(payload?.type || '') !== 'canvas_open') return null;
  return openCursorCanvasPopup(payload, { auto: true });
}

export function isCanvasPath(value) {
  return Boolean(normalizeCanvasPath(value));
}

export function renderCanvasOpenButton(payload, label = 'Open Canvas') {
  const path = normalizeCanvasPath(payload?.path || payload?.url);
  if (!path) return null;
  rememberCanvasPath(path, payload);
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'cursor-overlay-canvas-open-btn';
  button.textContent = label;
  button.addEventListener('click', () => {
    openCursorCanvasPopup({ ...payload, path }, { force: true });
  });
  return button;
}

export function renderCanvasArtifactActions(block) {
  const path = normalizeCanvasPath(block?.url || block?.path);
  if (!path) return null;
  const wrap = document.createElement('div');
  wrap.className = 'cursor-overlay-canvas-actions';
  wrap.append(renderCanvasOpenButton({ ...block, path }, 'Open Canvas'));
  return wrap;
}

export function renderCanvasActionsBar(paths, { title = 'Canvas ready' } = {}) {
  const normalized = [...new Set((Array.isArray(paths) ? paths : []).map(normalizeCanvasPath).filter(Boolean))];
  if (!normalized.length) return null;
  const wrap = document.createElement('div');
  wrap.className = 'cursor-overlay-canvas-bar';
  const label = document.createElement('div');
  label.className = 'cursor-overlay-canvas-bar-label';
  label.textContent = normalized.length === 1 ? title : `${title} (${normalized.length})`;
  wrap.append(label);
  normalized.forEach((path) => {
    wrap.append(renderCanvasOpenButton({ path, title: path.split('/').pop() }, 'Open Canvas'));
  });
  return wrap;
}
