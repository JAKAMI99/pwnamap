import './main.js';
import { bootShared, fetchJSON, toast, $ } from './dom.js';
import { initMap, renderMarkers } from './map.js';
import QRCode from 'qrcode';
bootShared();
async function boot() {
  await initMap();
  await loadNetworks();
  await renderApiQR();
}
async function loadNetworks() {
  try {
    const data = await fetchJSON('/api/explore?network_type=WIFI');
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
boot();
