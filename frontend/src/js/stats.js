import './main.js';
import { bootShared, fetchJSON, toast, $$ } from './dom.js';
bootShared();
async function load() {
  try {
    const data = await fetchJSON('/api/stats/summary');
    for (const el of $$('[data-stat]')) {
      const key = el.dataset.stat;
      const value = data?.[key];
      if (value === undefined) continue;
      animateNumber(el, Number(value) || 0);
    }
  } catch (err) {
    toast(`Could not load stats: ${err.message}`, 'err');
  }
}
function animateNumber(el, target) {
  const duration = 600;
  const start = performance.now();
  function tick(now) {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = Math.round(target * eased).toLocaleString();
    if (t < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
load();
