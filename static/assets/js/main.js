(function () {
  "use strict";

  /* Preloader — fade out once the page has loaded */
  window.addEventListener("load", function () {
    const preloader = document.getElementById("preloader");
    if (preloader) {
      preloader.style.opacity = "0";
      setTimeout(() => preloader.remove(), 400);
    }
  });

  /* Mobile nav toggle */
  const navToggle = document.querySelector(".mobile-nav-toggle");
  const navMenu = document.getElementById("navmenu");
  if (navToggle && navMenu) {
    navToggle.addEventListener("click", function () {
      navMenu.classList.toggle("nav-open");
      navToggle.classList.toggle("bi-list");
      navToggle.classList.toggle("bi-x");
    });
    // Close menu after clicking a link (mobile)
    navMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => navMenu.classList.remove("nav-open"));
    });
  }

  /* Scroll-to-top button */
  const scrollTop = document.getElementById("scroll-top");
  if (scrollTop) {
    const toggleScrollTop = () => {
      scrollTop.classList.toggle("active", window.scrollY > 100);
    };
    window.addEventListener("scroll", toggleScrollTop);
    toggleScrollTop();
    scrollTop.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* Portfolio filtering (vanilla replacement for isotope) */
  const filters = document.querySelectorAll(".portfolio-filters li");
  const items = document.querySelectorAll(".portfolio-item");
  if (filters.length && items.length) {
    filters.forEach((btn) => {
      btn.addEventListener("click", function () {
        filters.forEach((b) => b.classList.remove("filter-active"));
        this.classList.add("filter-active");
        const filter = this.getAttribute("data-filter");
        items.forEach((item) => {
          if (filter === "*" || item.classList.contains(filter.replace(".", ""))) {
            item.hidden = false;
          } else {
            item.hidden = true;
          }
        });
      });
    });
  }
})();
