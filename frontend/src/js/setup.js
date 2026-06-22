import './main.js';
import { bootShared, $, on, toast } from './dom.js';
bootShared();
on('#setup-form', 'submit', (e) => {
  const u = $('#username').value.trim();
  const p = $('#password').value;
  if (u.length < 3) { e.preventDefault(); toast('Username too short', 'warn'); return; }
  if (p.length < 8) { e.preventDefault(); toast('Password must be at least 8 characters', 'warn'); return; }
});
