/**
 * vibecoded: tiny DOM helpers — no framework, no jQuery.
 */
export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

export function on(target, event, handler, opts) {
  const el = typeof target === 'string' ? $(target) : target;
  if (!el) return () => {};
  el.addEventListener(event, handler, opts);
  return () => el.removeEventListener(event, handler, opts);
}

export function debounce(fn, wait = 200) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

export async function fetchJSON(url, opts = {}) {
  const headers = { Accept: 'application/json', ...(opts.headers || {}) };
  if (opts.body && typeof opts.body !== 'string') {
    headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(opts.body);
  }
  const apiKey = localStorage.getItem('pwnamap:apikey');
  if (apiKey && !headers['X-API-KEY']) headers['X-API-KEY'] = apiKey;
  const resp = await fetch(url, { ...opts, headers });
  if (!resp.ok) {
    const text = await resp.text().catch(() => '');
    throw new Error(`HTTP ${resp.status}: ${text || resp.statusText}`);
  }
  const ct = resp.headers.get('content-type') || '';
  return ct.includes('application/json') ? resp.json() : resp.text();
}

let toastHost = null;
function ensureToastHost() {
  if (toastHost) return toastHost;
  toastHost = document.createElement('div');
  toastHost.className = 'toast-host';
  toastHost.setAttribute('aria-live', 'polite');
  document.body.appendChild(toastHost);
  return toastHost;
}

export function toast(message, variant = 'info', ttl = 3500) {
  const host = ensureToastHost();
  const el = document.createElement('div');
  el.className = `toast toast--${variant}`;
  el.textContent = message;
  host.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 200);
  }, ttl);
}

export function initTheme() {
  const stored = localStorage.getItem('pwnamap:theme');
  const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
  const theme = stored || (prefersLight ? 'light' : 'dark');
  document.documentElement.dataset.theme = theme;
}

export function toggleTheme() {
  const current = document.documentElement.dataset.theme || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('pwnamap:theme', next);
  return next;
}

export function initNav() {
  const toggle = $('.app-header__nav-toggle');
  const nav = $('.app-nav');
  if (!toggle || !nav) return;
  on(toggle, 'click', () => {
    const isOpen = nav.dataset.open === 'true';
    nav.dataset.open = String(!isOpen);
    toggle.setAttribute('aria-expanded', String(!isOpen));
  });
}

export function highlightCurrentNav() {
  const current = document.body.dataset.page;
  if (!current) return;
  $$('.app-nav__link').forEach((a) => {
    if (a.dataset.page === current) a.setAttribute('aria-current', 'page');
  });
}

export function bootShared() {
  initTheme();
  initNav();
  highlightCurrentNav();
}
