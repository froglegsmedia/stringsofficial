(function () {
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".site-nav");

  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-solid", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  function setOpen(open) {
    if (!nav || !toggle) return;
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.classList.toggle("nav-open", open);
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
  }

  var dialog = document.querySelector(".lightbox");
  if (!dialog || typeof dialog.showModal !== "function") return;
  var full = dialog.querySelector("img");

  document.querySelectorAll("[data-lightbox]").forEach(function (button) {
    button.addEventListener("click", function () {
      var source = button.querySelector("img");
      if (!source) return;
      full.src = source.currentSrc || source.src;
      full.alt = source.alt;
      dialog.showModal();
    });
  });

  dialog.addEventListener("click", function (event) {
    if (event.target === dialog || event.target.closest("[data-close]")) {
      dialog.close();
    }
  });

  dialog.addEventListener("close", function () {
    full.removeAttribute("src");
  });
})();
