import './main.js';
import { bootShared, fetchJSON, toast, $, on, toggleTheme } from './dom.js';
bootShared();
async function load() {
  try {
    const data = await fetchJSON('/api/settings');
    if (data.wpasec) $('#wpasec').value = data.wpasec;
    if (data.wigle) $('#wigle').value = data.wigle;
    if (data.pwnamap) $('#pwnamap').value = data.pwnamap;
  } catch (err) {
    toast(`Could not load settings: ${err.message}`, 'err');
  }
}
on('#credentials-form', 'submit', async (e) => {
  e.preventDefault();
  try {
    await fetchJSON('/api/settings', {
      method: 'POST',
      body: { wpasec: $('#wpasec').value.trim(), wigle: $('#wigle').value.trim() },
    });
    toast('Settings saved', 'ok');
  } catch (err) {
    toast(`Save failed: ${err.message}`, 'err');
  }
});
on('#theme-toggle', 'click', () => {
  toast(`Theme: ${toggleTheme()}`, 'info', 1500);
});
load();
