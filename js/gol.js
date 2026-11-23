/* Gift of Lights plugin settings page (content.php). FPP loads every file in js/ on this plugin's pages. */
document.addEventListener('DOMContentLoaded', function () {
  if (!document.getElementById('golPage')) return;
  var API = '/api/plugin/fpp-plugin-GiftOfLights/';
  function el(id) { return document.getElementById(id); }
  // FPP 10 can switch jGrowl popups off (js/jquery.jgrowl.disabled.js only logs them), so every message is ALSO written
  // on the page under the buttons, where it cannot be suppressed.
  function toast(msg, ok) {
    var m = el('golMsg');
    if (m) { m.textContent = msg; m.className = 'mt-2 fw-semibold ' + (ok ? 'text-success' : 'text-danger'); }
    if (window.jQuery && jQuery.jGrowl) jQuery.jGrowl(msg, { themeState: ok ? 'success' : 'danger' });
    else if (!m) alert(msg);
  }
  function when(t) { return t ? new Date(t * 1000).toLocaleString() : ''; }

  function load() {
    fetch(API + 'config').then(function (r) { return r.json(); }).then(function (s) {
      el('golEnabled').checked = !!s.enabled;
      el('golUrl').value = s.backendUrl || '';
      el('golNames').value = s.showNames || '';
      el('golKeyNote').textContent = s.keySet
        ? 'A key is saved (ends ' + s.keyEnd + '). Type a new one only to replace it.'
        : 'No key saved yet. It must match the website\'s LIGHTSHOW_FEED_KEY setting.';
    }).catch(function () { toast('Could not read the saved settings from FPP (' + API + 'config).', false); });
  }

  function status() {
    fetch(API + 'status').then(function (r) { return r.json(); }).then(function (s) {
      var st = s.status || {};
      el('golRunning').textContent = s.running ? 'Running' : 'Not running (it starts with fppd; restart fppd to start it)';
      el('golLast').textContent = st.lastSent
        ? [st.lastSent.title || '(nothing playing)', st.lastSent.artist, st.lastSent.show].filter(Boolean).join(' / ') + ' - ' + when(st.lastSentAt)
        : 'Nothing yet';
      el('golError').textContent = st.lastError ? st.lastError + ' - ' + when(st.lastErrorAt) : 'None';
      el('golWaiting').textContent = String(s.waiting || 0);
    }).catch(function () {});
  }

  // The key's length as it is typed: the website refuses a key under 16 characters, and so does Save.
  function keyLen() {
    var n = el('golKey').value.trim().length, out = el('golKeyLen');
    if (!out) return;
    out.textContent = n ? n + ' characters' + (n < 16 ? ' - needs at least 16' : '') : '';
    out.className = 'form-text mb-1' + (n && n < 16 ? ' text-danger' : '');
  }
  el('golKey').addEventListener('input', keyLen);

  el('golSave').addEventListener('click', function () {
    var body = { enabled: el('golEnabled').checked, backendUrl: el('golUrl').value.trim(), showNames: el('golNames').value, key: el('golKey').value.trim() };
    fetch(API + 'config', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      // A reply that is not JSON (an FPP error page, a missing route) still says what happened.
      .then(function (r) { return r.text().then(function (t) { var j = null; try { j = JSON.parse(t); } catch (e) {} return { ok: r.ok && !!j, status: r.status, j: j || {} }; }); })
      .then(function (x) {
        if (!x.ok) { toast(x.j.error || ('Not saved: FPP answered HTTP ' + x.status + ' to ' + API + 'settings.'), false); return; }
        el('golKey').value = ''; keyLen();
        toast('Saved.', true);
        load();
      }).catch(function (e) { toast('Not saved: ' + (e && e.message ? e.message : 'no answer from FPP') + '.', false); });
  });

  el('golTest').addEventListener('click', function () {
    fetch(API + 'test', { method: 'POST' }).then(function (r) {
      toast(r.ok ? 'Test song queued. It shows on the website only while the stream is on air.' : 'Could not queue the test.', r.ok);
      setTimeout(status, 2000);
    });
  });

  load(); status(); setInterval(status, 5000);
});
