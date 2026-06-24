import './main.js';
import { bootShared, fetchJSON, toast, $ } from './dom.js';
import { initMap, renderMarkers } from './map.js';
import QRCode from 'qrcode';
bootShared();

const state = { dateFrom: '', dateTo: '' };

async function boot() {
  await initMap();
  bindControls();
  hydrateFromUrl();
  syncControlsFromState();
  await loadNetworks();
  await renderApiQR();
}

function bindControls() {
  const form = $('#map-filters');
  if (!form) return;
  $('#dateFrom', form).addEventListener('change', (e) => { state.dateFrom = e.target.value; loadNetworks(); });
  $('#dateTo', form).addEventListener('change', (e) => { state.dateTo = e.target.value; loadNetworks(); });
  $('#clearButton', form)?.addEventListener('click', clearFilters);
  form.querySelectorAll('[data-preset]').forEach((btn) => {
    btn.addEventListener('click', () => applyPreset(btn.dataset.preset));
  });
}

function applyPreset(preset) {
  const today = new Date();
  const fmt = (d) => d.toISOString().slice(0, 10);
  const from = new Date(today);
  if (preset === '24h') from.setDate(from.getDate() - 1);
  else if (preset === '7d') from.setDate(from.getDate() - 7);
  else if (preset === '30d') from.setDate(from.getDate() - 30);
  if (preset === 'all') {
    state.dateFrom = '';
    state.dateTo = '';
  } else {
    state.dateFrom = fmt(from);
    state.dateTo = fmt(today);
  }
  syncControlsFromState();
  loadNetworks();
}

function buildQuery() {
  const params = new URLSearchParams();
  if (state.dateFrom) params.set('date_from', state.dateFrom);
  if (state.dateTo) params.set('date_to', state.dateTo);
  const qs = params.toString();
  const url = qs ? `?${qs}` : window.location.pathname;
  window.history.replaceState({}, '', url);
  return qs;
}

async function loadNetworks() {
  try {
    const qs = buildQuery();
    const data = await fetchJSON(`/api/pwnamap${qs ? '?' + qs : ''}`);
    renderMarkers(Array.isArray(data) ? data : []);
  } catch (err) {
    toast(`Could not load networks: ${err.message}`, 'err');
  }
}

async function renderApiQR() {
  const target = $('#api-qr');
  if (!target) return;
  try {
    const apiInfo = await fetchJSON('/api/info');
    if (!apiInfo?.url || !apiInfo?.key) { target.textContent = 'API not configured'; return; }
    await QRCode.toCanvas(target, `${apiInfo.url}?key=${apiInfo.key}`, {
      width: 220, margin: 1, color: { dark: '#ececf1', light: '#16161c' },
    });
  } catch (err) {
    target.textContent = 'QR unavailable';
  }
}

function clearFilters() {
  state.dateFrom = ''; state.dateTo = '';
  syncControlsFromState();
  window.history.replaceState({}, '', window.location.pathname);
  loadNetworks();
}

function hydrateFromUrl() {
  const p = new URLSearchParams(window.location.search);
  state.dateFrom = p.get('date_from') || '';
  state.dateTo = p.get('date_to') || '';
}

function syncControlsFromState() {
  const form = $('#map-filters');
  if (!form) return;
  $('#dateFrom', form).value = state.dateFrom;
  $('#dateTo', form).value = state.dateTo;
}

boot();
