/* Runs before the first paint (plain, not deferred).
 * 1. Old deep links (index.html#/explorer ...) go to the app page, which now lives in app.html.
 * 2. The landing page's entrance and moment guards (taste-skill kit: the hero's words wait for motion.js,
 *    and show anyway after 700 ms if it is late; moments show their finished state after 2.5 s). */
(function () {
  /* The app page's address, built from this document's own URL (never from a <base> tag). */
  function appUrl(rest) {
    var here = location.href.split("#")[0];
    if (/index\.html(?=[^\/]*$)/.test(here)) return here.replace(/index\.html(?=[^\/]*$)/, "app.html") + rest;
    var u = new URL(here);
    u.pathname = u.pathname.replace(/[^\/]*$/, "") + "app.html";   /* a directory address such as https://site/ */
    return u.toString() + rest;
  }
  function toApp() {
    var deep = /^#\/.+/.test(location.hash), preview = /[?&]preview=/.test(location.search);
    if (!deep && !preview) return false;
    location.replace(appUrl(deep ? location.hash : ""));
    return true;
  }
  if (toApp()) return;
  window.addEventListener("hashchange", toApp);
  var d = document.documentElement;
  d.classList.add("m-enter"); setTimeout(function () { d.classList.add("m-enter-done"); }, 700);
  d.classList.add("mo-js"); setTimeout(function () { d.classList.add("mo-safe"); }, 2500);
  /* Links to the app page are resolved against this document's own URL, so they also work when a previewer
   * injects a <base> tag. In that case in-page links (#records ...) are handled here too. */
  document.addEventListener("click", function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
    if (!a) return;
    var href = a.getAttribute("href");
    if (href.indexOf("app.html") === 0) { e.preventDefault(); location.href = appUrl(href.slice("app.html".length)); return; }
    if (href.charAt(0) === "#" && href.length > 1 && document.querySelector("base")) {
      var t = document.getElementById(href.slice(1));
      if (t) { e.preventDefault(); t.scrollIntoView(); }
    }
  });
})();
