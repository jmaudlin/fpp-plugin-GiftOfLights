/* Gift of Lights plugin settings page (content.php). FPP loads every file in js/ on this plugin's pages. */
document.addEventListener('DOMContentLoaded', function () {
  if (!document.getElementById('golPage')) return;
  var API = '/api/plugin/fpp-plugin-GiftOfLights/';
  function el(id) { return document.getElementById(id); }
  function toast(msg, ok) { window.jQuery && jQuery.jGrowl ? jQuery.jGrowl(msg, { themeState: ok ? 'success' : 'danger' }) : alert(msg); }
  function when(t) { return t ? new Date(t * 1000).toLocaleString() : ''; }

  function load() {
    fetch(API + 'settings').then(function (r) { return r.json(); }).then(function (s) {
      el('golEnabled').checked = !!s.enabled;
      el('golUrl').value = s.backendUrl || '';
      el('golNames').value = s.showNames || '';
      el('golKeyNote').textContent = s.keySet
        ? 'A key is saved (ends ' + s.keyEnd + '). Type a new one only to replace it.'
        : 'No key saved yet. It must match the website\'s LIGHTSHOW_FEED_KEY setting.';
    });
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

  el('golSave').addEventListener('click', function () {
    var body = { enabled: el('golEnabled').checked, backendUrl: el('golUrl').value.trim(), showNames: el('golNames').value, key: el('golKey').value.trim() };
    fetch(API + 'settings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (x) {
        if (!x.ok) { toast(x.j.error || 'Not saved.', false); return; }
        el('golKey').value = '';
        toast('Saved.', true);
        load();
      }).catch(function () { toast('Not saved.', false); });
  });

  el('golTest').addEventListener('click', function () {
    fetch(API + 'test', { method: 'POST' }).then(function (r) {
      toast(r.ok ? 'Test song queued. It shows on the website only while the stream is on air.' : 'Could not queue the test.', r.ok);
      setTimeout(status, 2000);
    });
  });

  load(); status(); setInterval(status, 5000);
});
