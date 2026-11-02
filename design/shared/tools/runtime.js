(function () {
  "use strict";
  const root = document.querySelector(".hp[data-hp]");
  if (!root || root.dataset.ready) return;
  root.dataset.ready = "1";
  const find = selector => root.querySelector(selector);

  // Static files keep working on disk; the hosted mirror uses the Tilda routes.
  if (location.protocol === "https:" || location.protocol === "http:") {
    root.querySelectorAll('a[href*="index.html"]').forEach(link => {
      const url = new URL(link.href);
      if (url.origin !== location.origin || !url.pathname.endsWith("/index.html")) return;
      url.pathname = url.pathname.slice(0, -"/index.html".length) || "/";
      link.href = url.href;
    });
  }

  const burger = find(".burger");
  const nav = find(".nav");
  function menu(open) {
    burger.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("open", open);
  }
  burger.addEventListener("click", () => menu(!nav.classList.contains("open")));
  nav.addEventListener("click", () => menu(false));
  document.addEventListener("click", e => {
    if (!e.target.closest(".hp .bar")) menu(false);
  });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && nav.classList.contains("open")) {
      menu(false);
      burger.focus();
    }
  });

  const cookie = find(".cookie-box");
  const analytics = find('[name="analytics"]');
  const ads = find('[name="ads"]');
  const prefsKey = "hp.cookie.v1";
  const counter = Number(root.dataset.counter);
  let prefs;
  try { prefs = JSON.parse(localStorage.getItem(prefsKey)); } catch (_) {}
  let running = false;
  function meter(enabled) {
    if (location.protocol === "file:") return;
    if (!enabled && running) {
      window.ym(counter, "destruct");
      running = false;
    } else if (enabled && !running) {
      if (!window.ym) {
        window.ym = function () { (window.ym.a = window.ym.a || []).push(arguments); };
        window.ym.l = Date.now();
        const tag = document.createElement("script");
        tag.src = "https://mc.yandex.ru/metrika/tag.js";
        tag.async = true;
        document.head.appendChild(tag);
      }
      window.ym(counter, "init", {clickmap:true, trackLinks:true, accurateTrackBounce:true});
      running = true;
    }
  }
  if (prefs && typeof prefs.analytics === "boolean" && typeof prefs.ads === "boolean") {
    analytics.checked = prefs.analytics;
    ads.checked = prefs.ads;
    meter(prefs.analytics);
  } else { cookie.hidden = false; }
  const reopen = find("[data-cookie-open]");
  reopen.addEventListener("click", () => {
    cookie.hidden = false;
    cookie.querySelector("details").open = true;
    cookie.querySelector("summary").focus();
  });
  cookie.addEventListener("submit", e => {
    e.preventDefault();
    if (e.submitter && e.submitter.name === "essential") {
      analytics.checked = ads.checked = false;
    }
    prefs = {analytics:analytics.checked, ads:ads.checked};
    try { localStorage.setItem(prefsKey, JSON.stringify(prefs)); } catch (_) {}
    meter(prefs.analytics);
    cookie.hidden = true;
    if (reopen.getBoundingClientRect().top < innerHeight) reopen.focus({preventScroll:true});
  });

  const feedback = find("[data-feedback]");
  if (feedback) feedback.addEventListener("submit", e => {
    e.preventDefault();
    const body = Array.from(new FormData(feedback), ([key, value]) => key + ": " + value).join("\n");
    location.href = "mailto:" + feedback.dataset.feedback + "?subject=" +
      encodeURIComponent(feedback.dataset.subject) + "&body=" + encodeURIComponent(body);
  });

  const gate = find("[data-widget-form]");
  if (!gate) return;
  const host = find(".mobi");
  const check = gate.querySelector("input");
  const cfg = host.dataset;
  const address = new URL(cfg.url);
  function accessible() {
    host.inert = !check.checked;
    host.style.pointerEvents = check.checked ? "" : "none";
  }
  function mount() {
    if (host.dataset.mounted) return;
    host.dataset.mounted = "1";
    if (location.protocol === "https:") {
      const script = document.createElement("script");
      script.id = "mobifitness_personal_widget_script";
      Object.assign(script.dataset, {code:cfg.code, club:cfg.club, domain:address.hostname,
        div:host.id, type:cfg.type, language:"ru"});
      if (cfg.section) script.dataset.section = cfg.section;
      script.src = address.origin + "/personal-widget/js/code.js";
      const observer = new MutationObserver(() => {
        const frame = host.querySelector("iframe");
        if (frame) { frame.title = cfg.title; observer.disconnect(); }
      });
      observer.observe(host, {subtree:true, childList:true});
      host.after(script);
    } else {
      // Vendor bootstrap selects http:// on file:// and http:// pages.
      // Use the same HTTPS widget directly for the local preview.
      const frame = document.createElement("iframe");
      const parent = location.href.split("#")[0].split("?")[0] + "?mfw";
      address.searchParams.set("parent", parent);
      frame.src = address.href;
      frame.title = cfg.title;
      frame.height = cfg.type === "schedule" ? "640" : "520";
      window.addEventListener("message", e => {
        if (e.origin !== address.origin || e.source !== frame.contentWindow) return;
        let data = e.data;
        if (typeof data === "string") { try { data = JSON.parse(data); } catch (_) { return; } }
        if (data && data.parent === parent && Number(data.height) > 0) frame.height = Number(data.height);
      });
      host.appendChild(frame);
    }
    accessible();
  }
  check.addEventListener("change", accessible);
  gate.addEventListener("submit", e => {
    e.preventDefault();
    mount();
    host.scrollIntoView({block:"start"});
  });
  if (cfg.type === "schedule") mount();
})();
