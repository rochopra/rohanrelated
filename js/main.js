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

  // Dropdown menus: the caret button toggles a menu (touch and click).
  // Hover and keyboard focus are handled in CSS. Escape or an outside
  // click closes any open menu.
  var items = document.querySelectorAll(".nav-item.has-menu");
  function closeMenus(except) {
    items.forEach(function (it) {
      if (it === except) return;
      it.classList.remove("open");
      var b = it.querySelector(".nav-caret");
      if (b) b.setAttribute("aria-expanded", "false");
    });
  }
  items.forEach(function (it) {
    var b = it.querySelector(".nav-caret");
    if (!b) return;
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = !it.classList.contains("open");
      closeMenus(it);
      it.classList.toggle("open", open);
      b.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  document.addEventListener("click", function () { closeMenus(null); });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var openItem = document.querySelector(".nav-item.open");
    closeMenus(null);
    if (openItem) { var b = openItem.querySelector(".nav-caret"); if (b) b.focus(); }
    if (document.activeElement && document.activeElement.blur && document.activeElement.closest && document.activeElement.closest(".nav-menu")) document.activeElement.blur();
  });

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
