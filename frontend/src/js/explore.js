import './main.js';
import { bootShared, fetchJSON, toast, $, debounce } from './dom.js';
import { initMap, renderMarkers, clearMarkers } from './map.js';
bootShared();

const state = {
  networkType: '', encryption: '', name: '', networkId: '', excludeNoSSID: true,
};

async function boot() {
  await initMap();
  bindControls();
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
  $('#searchButton', form).addEventListener('click', doSearch);
  $('#clearButton', form).addEventListener('click', clearFilters);
  form.addEventListener('submit', (e) => { e.preventDefault(); doSearch(); });
}

function buildQuery() {
  const params = new URLSearchParams();
  if (state.networkType) params.set('network_type', state.networkType);
  if (state.encryption) params.set('encryption', state.encryption);
  if (state.name) params.set('name', state.name);
  if (state.networkId) params.set('network_id', state.networkId);
  if (state.excludeNoSSID) params.set('exclude_no_ssid', 'true');
  return params.toString();
}

async function doSearch() {
  try {
    clearMarkers();
    const data = await fetchJSON(`/api/explore?${buildQuery()}`);
    renderMarkers(Array.isArray(data) ? data : []);
  } catch (err) {
    toast(`Search failed: ${err.message}`, 'err');
  }
}

function clearFilters() {
  state.networkType = ''; state.encryption = ''; state.name = '';
  state.networkId = ''; state.excludeNoSSID = true;
  const form = $('#explore-filters');
  form.reset();
  $('#excludeNoSSID', form).checked = true;
  clearMarkers();
}

boot();
