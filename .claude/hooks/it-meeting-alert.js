/* Hook: after the visitor has been on the site for more than 10 seconds,
   show a modal alert about the mandatory IT meeting. Shown once per page load. */
(function () {
  var DELAY_MS = 10000;
  var MESSAGE = {
    title: 'IT Meeting Notice',
    body: 'There is an IT meeting next Wednesday at PDD TOWER 80 at 2:00 AM.',
    note: 'Attendance is mandatory.'
  };

  function show() {
    if (document.getElementById('it-meeting-overlay')) return;
    var overlay = document.createElement('div');
    overlay.id = 'it-meeting-overlay';
    overlay.setAttribute('role', 'alertdialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-labelledby', 'it-meeting-title');
    overlay.setAttribute('aria-describedby', 'it-meeting-body');
    overlay.style.cssText = 'position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(0,0,0,.55);font-family:system-ui,sans-serif';

    var box = document.createElement('div');
    box.style.cssText = 'background:#fff;color:#1a1a1a;max-width:420px;width:100%;border-radius:12px;padding:24px;box-shadow:0 10px 40px rgba(0,0,0,.35);border-top:6px solid #c62828';

    var h = document.createElement('h2');
    h.id = 'it-meeting-title';
    h.textContent = '⚠️ ' + MESSAGE.title;
    h.style.cssText = 'margin:0 0 12px;font-size:20px';

    var p = document.createElement('p');
    p.id = 'it-meeting-body';
    p.style.cssText = 'margin:0 0 8px;font-size:16px;line-height:1.5';
    p.textContent = MESSAGE.body;

    var n = document.createElement('p');
    n.textContent = MESSAGE.note;
    n.style.cssText = 'margin:0 0 20px;font-weight:700;color:#c62828';

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = 'OK, understood';
    btn.style.cssText = 'background:#1565c0;color:#fff;border:0;border-radius:8px;padding:10px 20px;font-size:15px;cursor:pointer';
    btn.addEventListener('click', function () {
      overlay.remove();
      document.removeEventListener('keydown', onKey);
    });
    function onKey(e) { if (e.key === 'Escape') btn.click(); }
    document.addEventListener('keydown', onKey);

    box.appendChild(h); box.appendChild(p); box.appendChild(n); box.appendChild(btn);
    overlay.appendChild(box);
    document.body.appendChild(overlay);
    btn.focus();
  }

  setTimeout(show, DELAY_MS);
})();
