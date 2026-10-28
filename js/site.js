(function () {
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".site-nav");
  var main = document.querySelector("main");
  var footer = document.querySelector(".site-footer");

  if (header && !header.classList.contains("is-solid")) {
    var onScroll = function () {
      header.classList.toggle("is-solid", window.scrollY > 12);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  function setOpen(open) {
    if (!nav || !toggle) return;
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.classList.toggle("nav-open", open);
    var label = toggle.querySelector(".visually-hidden");
    if (label) label.textContent = open ? "Close menu" : "Menu";
    if (main) main.inert = open;
    if (footer) footer.inert = open;
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      setOpen(!nav.classList.contains("is-open"));
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setOpen(false);
      });
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") setOpen(false);
    });
    window.addEventListener("resize", function () {
      if (window.matchMedia("(min-width: 1180px)").matches) setOpen(false);
    });
  }

  if (nav && "IntersectionObserver" in window) {
    var pairs = [];
    nav.querySelectorAll('a[href^="#"]').forEach(function (link) {
      var id = link.getAttribute("href").slice(1);
      var section = document.getElementById(id);
      if (section) pairs.push({ link: link, section: section });
    });
    if (pairs.length) {
      var current = null;
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          current = entry.target;
        });
        pairs.forEach(function (item) {
          if (item.section === current) item.link.setAttribute("aria-current", "true");
          else item.link.removeAttribute("aria-current");
        });
      }, { rootMargin: "-45% 0px -45% 0px", threshold: 0 });
      pairs.forEach(function (item) { observer.observe(item.section); });
    }
  }

  document.querySelectorAll("[data-youtube]").forEach(function (trigger) {
    trigger.addEventListener("click", function (event) {
      event.preventDefault();
      var id = trigger.getAttribute("data-youtube") || "";
      if (!/^[A-Za-z0-9_-]{6,}$/.test(id)) return;
      var frame = trigger.closest(".frame");
      if (!frame) return;
      var iframe = document.createElement("iframe");
      iframe.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
      iframe.title = "STRINGS official trailer";
      iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
      iframe.allowFullscreen = true;
      iframe.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
      frame.replaceChildren(iframe);
    });
  });

  var dialog = document.querySelector(".lightbox");
  if (!dialog || typeof dialog.showModal !== "function") return;
  var full = dialog.querySelector("img");

  document.querySelectorAll("[data-lightbox]").forEach(function (button) {
    button.addEventListener("click", function () {
      var source = button.querySelector("img");
      if (!source) return;
      full.src = source.currentSrc || source.src;
      full.alt = source.alt || "";
      dialog.showModal();
    });
  });

  dialog.addEventListener("click", function (event) {
    if (event.target === dialog || event.target.closest("[data-close]")) dialog.close();
  });

  dialog.addEventListener("close", function () {
    full.removeAttribute("src");
    full.alt = "";
  });
})();
