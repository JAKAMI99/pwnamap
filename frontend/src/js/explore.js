import './main.js';
import { bootShared, fetchJSON, toast, $, debounce } from './dom.js';
import { initMap, renderMarkers, clearMarkers } from './map.js';
bootShared();

const state = {
  networkType: '',
  encryption: '',
  name: '',
  networkId: '',
  excludeNoSSID: true,
  dateFrom: '',
  dateTo: '',
};

async function boot() {
  await initMap();
  bindControls();
  // vibecoded: hydrate from URL params so links are shareable
  hydrateFromUrl();
  syncControlsFromState();
  doSearch();
}

function bindControls() {
  const form = $('#explore-filters');
  if (!form) return;
  $('#networkType', form).addEventListener('change', (e) => { state.networkType = e.target.value; });
  $('#encryption', form).addEventListener('change', (e) => { state.encryption = e.target.value; });
  $('#searchInputName', form).addEventListener('input', debounce((e) => { state.name = e.target.value; }, 250));
  $('#searchInputNetworkId', form).addEventListener('input', debounce((e) => { state.networkId = e.target.value; }, 250));
  $('#excludeNoSSID', form).addEventListener('change', (e) => { state.excludeNoSSID = e.target.checked; });
  $('#dateFrom', form).addEventListener('change', (e) => { state.dateFrom = e.target.value; });
  $('#dateTo', form).addEventListener('change', (e) => { state.dateTo = e.target.value; });
  $('#searchButton', form).addEventListener('click', doSearch);
  $('#clearButton', form).addEventListener('click', clearFilters);
  form.addEventListener('submit', (e) => { e.preventDefault(); doSearch(); });

  // vibecoded: quick-preset buttons
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
  else { from.setTime(0); } // 'all' = no lower bound
  if (preset === 'all') {
    state.dateFrom = '';
    state.dateTo = '';
  } else {
    state.dateFrom = fmt(from);
    state.dateTo = fmt(today);
  }
  syncControlsFromState();
  doSearch();
}

function buildQuery() {
  const params = new URLSearchParams();
  if (state.networkType) params.set('network_type', state.networkType);
  if (state.encryption) params.set('encryption', state.encryption);
  if (state.name) params.set('name', state.name);
  if (state.networkId) params.set('network_id', state.networkId);
  if (state.excludeNoSSID) params.set('exclude_no_ssid', 'true');
  if (state.dateFrom) params.set('date_from', state.dateFrom);
  if (state.dateTo) params.set('date_to', state.dateTo);
  // vibecoded: keep URL in sync so the page is bookmarkable / shareable
  const qs = params.toString();
  const url = qs ? `?${qs}` : window.location.pathname;
  if (url !== window.location.search && url !== window.location.pathname) {
    window.history.replaceState({}, '', url);
  }
  return qs;
}

async function doSearch() {
  try {
    clearMarkers();
    const qs = buildQuery();
    const data = await fetchJSON(`/api/explore${qs ? '?' + qs : ''}`);
    renderMarkers(Array.isArray(data) ? data : []);
  } catch (err) {
    toast(`Search failed: ${err.message}`, 'err');
  }
}

function clearFilters() {
  state.networkType = ''; state.encryption = ''; state.name = '';
  state.networkId = ''; state.excludeNoSSID = true;
  state.dateFrom = ''; state.dateTo = '';
  const form = $('#explore-filters');
  form.reset();
  $('#excludeNoSSID', form).checked = true;
  window.history.replaceState({}, '', window.location.pathname);
  clearMarkers();
}

function hydrateFromUrl() {
  const p = new URLSearchParams(window.location.search);
  state.networkType = p.get('network_type') || '';
  state.encryption = p.get('encryption') || '';
  state.name = p.get('name') || '';
  state.networkId = p.get('network_id') || '';
  state.excludeNoSSID = p.get('exclude_no_ssid') !== 'false';
  state.dateFrom = p.get('date_from') || '';
  state.dateTo = p.get('date_to') || '';
}

function syncControlsFromState() {
  const form = $('#explore-filters');
  if (!form) return;
  $('#networkType', form).value = state.networkType;
  $('#encryption', form).value = state.encryption;
  $('#searchInputName', form).value = state.name;
  $('#searchInputNetworkId', form).value = state.networkId;
  $('#excludeNoSSID', form).checked = state.excludeNoSSID;
  $('#dateFrom', form).value = state.dateFrom;
  $('#dateTo', form).value = state.dateTo;
}

boot();
