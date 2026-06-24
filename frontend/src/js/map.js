/**
 * vibecoded: Leaflet map with marker clustering.
 * Vendored Leaflet + markercluster — bundled into the same JS chunk.
 */
import L from 'leaflet';
import 'leaflet.markercluster';
import { loadConfig } from './config.js';
import { $, toast } from './dom.js';

let map = null;
let cluster = null;

export async function initMap(opts = {}) {
  const cfg = await loadConfig();
  const container = opts.container || $('#map');
  if (!container) return null;

  map = L.map(container, {
    center: opts.center || cfg.default_center,
    zoom: opts.zoom ?? cfg.default_zoom,
    maxZoom: cfg.max_zoom ?? 19,
    zoomControl: true,
    preferCanvas: true,
  });

  if (cfg.tile_url) {
    L.tileLayer(cfg.tile_url, {
      maxZoom: cfg.max_zoom ?? 19,
      attribution: cfg.tile_attribution || '&copy; OpenStreetMap contributors',
      crossOrigin: true,
    }).addTo(map);
  } else {
    showTileBanner(container);
  }

  cluster = L.markerClusterGroup({
    chunkedLoading: true,
    chunkInterval: 100,
    chunkDelay: 50,
    maxClusterRadius: 60,
    showCoverageOnHover: false,
    spiderfyOnMaxZoom: true,
  });
  map.addLayer(cluster);

  L.control.locate({
    position: 'topright',
    setView: 'untilPan',
    flyTo: true,
    keepCurrentZoomLevel: true,
    drawCircle: true,
    showPopup: false,
  }).addTo(map);

  return map;
}

function showTileBanner(container) {
  const banner = document.createElement('div');
  banner.className = 'tile-banner';
  banner.innerHTML = '<strong>Map tiles not configured.</strong> Set <code>tile_url</code> in Settings, or accept the default OpenStreetMap. Markers will still display.';
  banner.style.cssText = 'position:absolute;top:12px;left:12px;right:12px;z-index:1000;padding:12px 16px;background:var(--bg-elev);border:1px solid var(--border);border-radius:var(--radius-md);box-shadow:var(--shadow-md);color:var(--text);font-size:var(--fs-sm);';
  container.style.position = 'relative';
  container.appendChild(banner);
  setTimeout(() => banner.remove(), 8000);
}

export function clearMarkers() {
  if (cluster) cluster.clearLayers();
}

export function renderMarkers(networks) {
  if (!cluster) return;
  cluster.clearLayers();
  if (!networks?.length) {
    toast('No networks found', 'warn');
    return;
  }
  const markers = networks
    .filter((n) => Number.isFinite(n.lat) && Number.isFinite(n.lon))
    .map((n) => {
      const m = L.marker([n.lat, n.lon]);
      m.bindPopup(buildPopup(n));
      return m;
    });
  cluster.addLayers(markers);
  if (markers.length) {
    const group = L.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(0.2), { maxZoom: 16 });
  }
}

function buildPopup(n) {
  const enc = n.encryption || '—';
  const sig = Number.isFinite(n.signal) ? `${n.signal} dBm` : '—';
  const time = n.time ? new Date(n.time).toLocaleString() : '—';
  return `<div class="popup"><div class="popup__name">${escapeHtml(n.name || '(no SSID)')}</div><dl class="popup__meta"><dt>Encryption</dt><dd>${escapeHtml(enc)}</dd><dt>Signal</dt><dd>${sig}</dd><dt>MAC</dt><dd>${escapeHtml(n.network_id || '—')}</dd><dt>Seen</dt><dd>${escapeHtml(time)}</dd></dl></div>`;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

export function invalidateSize() {
  if (map) map.invalidateSize();
}
