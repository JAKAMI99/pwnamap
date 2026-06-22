import './main.js';
import { bootShared, $ } from './dom.js';
bootShared();
const search = $('#search');
const list = $('#file-list');
if (search && list) {
  search.addEventListener('input', () => {
    const q = search.value.toLowerCase().trim();
    let visible = 0;
    for (const row of list.querySelectorAll('.data-row')) {
      const name = row.dataset.name?.toLowerCase() || '';
      const match = !q || name.includes(q);
      row.hidden = !match;
      if (match) visible++;
    }
    const counter = $('#result-count');
    if (counter) counter.textContent = `${visible} file${visible === 1 ? '' : 's'}`;
  });
}
