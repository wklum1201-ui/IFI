/* Hook: Mickey Mouse IT assistant widget (bottom right).
   Clicking it speaks "I am your IT assistant, how can i help you?" via the
   browser's built-in speech synthesis, and shows the same text in a bubble. */
(function () {
  var GREETING = 'I am your IT assistant, how can i help you?';

  var svg =
    '<svg viewBox="0 0 100 100" width="64" height="64" aria-hidden="true">' +
    '<circle cx="22" cy="22" r="20" fill="#111"/><circle cx="78" cy="22" r="20" fill="#111"/>' +
    '<circle cx="50" cy="58" r="36" fill="#111"/>' +
    '<path d="M24 52c0-14 12-20 26-12 14-8 26-2 26 12 0 18-14 34-26 34S24 70 24 52z" fill="#f8d4a8"/>' +
    '<ellipse cx="41" cy="50" rx="7" ry="11" fill="#fff" stroke="#111" stroke-width="2"/>' +
    '<ellipse cx="59" cy="50" rx="7" ry="11" fill="#fff" stroke="#111" stroke-width="2"/>' +
    '<circle cx="43" cy="53" r="4" fill="#111"/><circle cx="57" cy="53" r="4" fill="#111"/>' +
    '<ellipse cx="50" cy="63" rx="6" ry="4.5" fill="#111"/>' +
    '<path d="M36 72q14 14 28 0" fill="#c62828" stroke="#111" stroke-width="2"/>' +
    '</svg>';

  function speak() {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(GREETING);
    u.lang = 'en-US';
    u.pitch = 1.6;  // higher, cartoon-like voice
    u.rate = 1.0;
    window.speechSynthesis.speak(u);
  }

  function init() {
    var wrap = document.createElement('div');
    wrap.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:9999;display:flex;flex-direction:column;align-items:flex-end;gap:8px;font-family:system-ui,sans-serif';

    var bubble = document.createElement('div');
    bubble.setAttribute('role', 'status');
    bubble.textContent = GREETING;
    bubble.style.cssText = 'display:none;max-width:220px;background:#fff;color:#1a1a1a;padding:10px 12px;border-radius:12px;font-size:14px;box-shadow:0 4px 16px rgba(0,0,0,.25)';

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.setAttribute('aria-label', 'Open IT assistant chatbot');
    btn.title = 'IT Assistant';
    btn.innerHTML = svg;
    btn.style.cssText = 'width:72px;height:72px;border-radius:50%;border:3px solid #1565c0;background:#fff;padding:0;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center';

    var hideTimer;
    btn.addEventListener('click', function () {
      bubble.style.display = 'block';
      speak();
      clearTimeout(hideTimer);
      hideTimer = setTimeout(function () { bubble.style.display = 'none'; }, 6000);
    });

    wrap.appendChild(bubble);
    wrap.appendChild(btn);
    document.body.appendChild(wrap);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
