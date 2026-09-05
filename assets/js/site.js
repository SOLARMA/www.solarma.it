/* SOLARMA S.N.C. — site behaviour
   Vanilla JS, no dependencies. Two jobs:
   1. mobile navigation toggle
   2. consent-gated analytics (GA4 is loaded only after explicit opt-in) */
(function () {
  'use strict';

  /* ---------------- Mobile navigation ---------------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('primary-nav');

  function isMobile() { return window.matchMedia('(max-width: 900px)').matches; }

  function setNav(open) {
    if (!nav || !toggle) return;
    nav.hidden = !open;
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  function syncNav() {
    if (!nav || !toggle) return;
    if (isMobile()) { setNav(false); } else { nav.hidden = false; toggle.setAttribute('aria-expanded', 'false'); }
  }

  if (toggle && nav) {
    syncNav();
    window.addEventListener('resize', syncNav);
    toggle.addEventListener('click', function () {
      setNav(nav.hidden);
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A' && isMobile()) setNav(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isMobile() && !nav.hidden) { setNav(false); toggle.focus(); }
    });
  }

  /* ---------------- Consent-gated analytics ----------------
     No cookie is written and no request is made to Google until the
     visitor actively accepts. Declining stores the refusal only. */
  var GA_ID = 'G-2ZJF0K1SZL';
  var KEY = 'solarma.consent.v1';
  var bar = document.getElementById('cookie-bar');

  function readConsent() {
    try { return window.localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function writeConsent(value) {
    try { window.localStorage.setItem(KEY, value); } catch (e) { /* storage blocked — session only */ }
  }

  function loadAnalytics() {
    if (window.__solarmaGaLoaded) return;
    window.__solarmaGaLoaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', GA_ID, { anonymize_ip: true });
  }

  var consent = readConsent();
  if (consent === 'granted') {
    loadAnalytics();
  } else if (consent !== 'denied' && bar) {
    bar.hidden = false;
  }

  if (bar) {
    bar.addEventListener('click', function (e) {
      var action = e.target.getAttribute && e.target.getAttribute('data-consent');
      if (!action) return;
      writeConsent(action === 'accept' ? 'granted' : 'denied');
      bar.hidden = true;
      if (action === 'accept') loadAnalytics();
    });
  }

  /* Re-open the banner from the legal pages ("gestisci le preferenze") */
  var reopen = document.querySelectorAll('[data-consent-reset]');
  Array.prototype.forEach.call(reopen, function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      try { window.localStorage.removeItem(KEY); } catch (err) { /* ignore */ }
      if (bar) { bar.hidden = false; bar.scrollIntoView({ block: 'nearest' }); }
    });
  });
})();
