/* rohanrelated.com — main.js
   One job: subtle scroll reveals. Everything on this site works
   with JavaScript disabled; this file only adds polish.
   - <html> gets .js so CSS only hides .reveal elements when JS runs
   - prefers-reduced-motion users get no movement at all */
(function () {
  // Draft mode: append ?draft to any URL to see [TODO] placeholder blocks.
  if (new URLSearchParams(location.search).has("draft")) {
    document.documentElement.classList.add("show-drafts");
  }

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce || !("IntersectionObserver" in window)) return;

  document.documentElement.classList.add("js");

  var io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }
  );

  document.querySelectorAll(".reveal").forEach(function (el) {
    io.observe(el);
  });
})();
