import './main.js';
import { bootShared, fetchJSON, toast } from './dom.js';
bootShared();
const liveLog = document.getElementById('live-results');
function appendLine(text, kind = '') {
  if (!liveLog) return;
  const line = document.createElement('div');
  line.className = 'live-log__line' + (kind ? ` live-log__line--${kind}` : '');
  line.textContent = text;
  liveLog.appendChild(line);
  liveLog.scrollTop = liveLog.scrollHeight;
}
window.runScript = async function runScript(name) {
  appendLine(`[${new Date().toLocaleTimeString()}] starting ${name}...`, 'info');
  try {
    const data = await fetchJSON(`/api/tools/${name}`, { method: 'POST' });
    appendLine(`[${new Date().toLocaleTimeString()}] ${name}: ok`, 'ok');
  } catch (err) {
    appendLine(`[${new Date().toLocaleTimeString()}] ${name}: ${err.message}`, 'err');
    toast(`${name} failed`, 'err');
  }
};
window.uploadFile = async function uploadFile(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const ext = file.name.split('.').pop().toLowerCase();
  if (!['22000', 'pot', 'potfile'].includes(ext)) {
    toast(`Unsupported file type: .${ext}`, 'err');
    return;
  }
  appendLine(`[${new Date().toLocaleTimeString()}] uploading ${file.name}...`, 'info');
  const form = new FormData();
  form.append('file', file);
  try {
    await fetch('/api/tools/upload_pot', { method: 'POST', body: form });
    appendLine(`[${new Date().toLocaleTimeString()}] upload ok`, 'ok');
    toast('Potfile uploaded', 'ok');
  } catch (err) {
    appendLine(`[${new Date().toLocaleTimeString()}] upload failed: ${err.message}`, 'err');
    toast('Upload failed', 'err');
  }
};
window.clearOutput = () => { if (liveLog) liveLog.innerHTML = ''; };
