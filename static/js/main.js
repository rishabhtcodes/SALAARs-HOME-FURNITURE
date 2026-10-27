document.addEventListener("DOMContentLoaded", () => {
  // Mobile drawer controls
  const openMenuBtn = document.getElementById("open-menu-btn");
  const closeMenuBtn = document.getElementById("close-menu-btn");
  const mobileDrawer = document.getElementById("mobile-drawer");
  const drawerPanel = document.getElementById("drawer-panel");
  const drawerBackdrop = document.getElementById("drawer-backdrop");

  function openDrawer() {
    if (!mobileDrawer) return;
    mobileDrawer.classList.remove("opacity-0", "pointer-events-none");
    mobileDrawer.classList.add("opacity-100", "pointer-events-auto");
    drawerPanel.classList.remove("-translate-x-full");
    document.body.style.overflow = "hidden";
  }

  function closeDrawer() {
    if (!mobileDrawer) return;
    mobileDrawer.classList.add("opacity-0", "pointer-events-none");
    mobileDrawer.classList.remove("opacity-100", "pointer-events-auto");
    drawerPanel.classList.add("-translate-x-full");
    document.body.style.overflow = "";
  }

  if (openMenuBtn) openMenuBtn.addEventListener("click", openDrawer);
  if (closeMenuBtn) closeMenuBtn.addEventListener("click", closeDrawer);
  if (drawerBackdrop) drawerBackdrop.addEventListener("click", closeDrawer);

  // Search modal controls
  const openSearchBtn = document.getElementById("open-search-btn");
  const closeSearchBtn = document.getElementById("close-search-btn");
  const searchModal = document.getElementById("search-modal");
  const searchInput = document.getElementById("search-modal-input");
  const searchResultsBox = document.getElementById("search-results-box");
  const searchResultsList = document.getElementById("search-results-list");

  function openSearch() {
    if (!searchModal) return;
    searchModal.classList.remove("opacity-0", "pointer-events-none");
    searchModal.classList.add("opacity-100", "pointer-events-auto");
    document.body.style.overflow = "hidden";
    setTimeout(() => searchInput && searchInput.focus(), 50);
  }

  function closeSearch() {
    if (!searchModal) return;
    searchModal.classList.add("opacity-0", "pointer-events-none");
    searchModal.classList.remove("opacity-100", "pointer-events-auto");
    document.body.style.overflow = "";
  }

  if (openSearchBtn) openSearchBtn.addEventListener("click", openSearch);
  if (closeSearchBtn) closeSearchBtn.addEventListener("click", closeSearch);
  if (searchModal) {
    searchModal.addEventListener("click", (e) => {
      if (e.target === searchModal) closeSearch();
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeDrawer();
      closeSearch();
    }
  });

  // Instant Search debounce
  let searchTimer;
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      clearTimeout(searchTimer);
      const q = e.target.value.trim();
      if (q.length < 2) {
        if (searchResultsBox) searchResultsBox.classList.add("hidden");
        return;
      }
      searchTimer = setTimeout(() => {
        fetch(`/api/search/?q=${encodeURIComponent(q)}`)
          .then((res) => res.json())
          .then((data) => {
            if (!searchResultsList || !searchResultsBox) return;
            searchResultsList.innerHTML = "";
            if (data.results && data.results.length > 0) {
              data.results.forEach((p) => {
                const li = document.createElement("li");
                li.innerHTML = `
                  <a href="/product/${p.slug}/" class="group flex items-center gap-4 rounded-2xl p-3 transition-colors hover:bg-beige/70">
                    <span class="relative block h-14 w-14 shrink-0 overflow-hidden rounded-xl bg-beige">
                      <img src="/static/${p.image.replace(/^\//, '')}" alt="${p.name}" class="h-full w-full object-contain p-1">
                    </span>
                    <div class="min-w-0 flex-1">
                      <p class="truncate text-[10px] font-semibold tracking-[0.2em] text-stone uppercase">${p.category}</p>
                      <p class="truncate font-display text-base font-semibold text-ink group-hover:text-gold-deep">${p.name}</p>
                      <p class="text-xs font-semibold text-gold-deep">${p.price}</p>
                    </div>
                  </a>
                `;
                searchResultsList.appendChild(li);
              });
              searchResultsBox.classList.remove("hidden");
            } else {
              searchResultsList.innerHTML = `<li class="p-4 text-center text-sm text-stone">No pieces found matching "${q}"</li>`;
              searchResultsBox.classList.remove("hidden");
            }
          });
      }, 250);
    });
  }

  // Horizontal mouse scroll for Category Navigation Bar
  const categoryNav = document.getElementById("category-nav-scroller");
  if (categoryNav) {
    categoryNav.addEventListener("wheel", (e) => {
      if (categoryNav.scrollWidth > categoryNav.clientWidth + 1) {
        if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
          e.preventDefault();
          categoryNav.scrollLeft += e.deltaY;
        }
      }
    }, { passive: false });

    // Scroll active nav category item into view on load
    const activeNav = categoryNav.querySelector('[aria-current="page"]');
    if (activeNav) {
      activeNav.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    }
  }

  // Back to top button
  const backToTopBtn = document.getElementById("back-to-top-btn");
  if (backToTopBtn) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 600) {
        backToTopBtn.classList.remove("opacity-0", "pointer-events-none");
        backToTopBtn.classList.add("opacity-100", "pointer-events-auto");
      } else {
        backToTopBtn.classList.add("opacity-0", "pointer-events-none");
        backToTopBtn.classList.remove("opacity-100", "pointer-events-auto");
      }
    }, { passive: true });

    backToTopBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
});
