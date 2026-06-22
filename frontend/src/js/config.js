/**
 * vibecoded: runtime config — fetched from /api/config once.
 * User-configurable (tile server, app name) lives here.
 */
let cached = null;

export async function loadConfig() {
  if (cached) return cached;
  try {
    const r = await fetch('/api/config');
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    cached = await r.json();
  } catch {
    cached = {
      tile_url: null,
      tile_attribution: null,
      max_zoom: 19,
      default_center: [51.1657, 10.4515],
      default_zoom: 6,
    };
  }
  return cached;
}
