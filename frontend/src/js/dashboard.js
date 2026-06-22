import './main.js';
import { bootShared, fetchJSON, toast } from './dom.js';
bootShared();
async function loadStats() {
  try {
    const stats = await fetchJSON('/api/stats/summary');
    for (const [key, value] of Object.entries(stats || {})) {
      const card = document.querySelector(`[data-stat="${key}"]`);
      if (card) card.textContent = value;
    }
  } catch (err) {
    toast(`Could not load stats: ${err.message}`, 'err');
  }
}
loadStats();
