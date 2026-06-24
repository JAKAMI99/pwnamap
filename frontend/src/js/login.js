import './main.js';
import { bootShared, $, on, toast } from './dom.js';
bootShared();
on('#login-form', 'submit', (e) => {
  const u = $('#username').value.trim();
  const p = $('#password').value;
  if (!u || !p) { e.preventDefault(); toast('Username and password required', 'warn'); }
});
