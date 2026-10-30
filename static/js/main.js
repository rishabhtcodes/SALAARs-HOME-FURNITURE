document.addEventListener("DOMContentLoaded", () => {
  // Dark / Light Theme Toggle
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  const sunIcon = document.getElementById("theme-icon-sun");
  const moonIcon = document.getElementById("theme-icon-moon");

  function updateThemeIcons() {
    const isDark = document.documentElement.classList.contains("dark");
    if (sunIcon && moonIcon) {
      if (isDark) {
        sunIcon.classList.remove("hidden");
        moonIcon.classList.add("hidden");
      } else {
        sunIcon.classList.add("hidden");
        moonIcon.classList.remove("hidden");
      }
    }
  }

  if (themeToggleBtn) {
    updateThemeIcons();
    themeToggleBtn.addEventListener("click", () => {
      const isDark = document.documentElement.classList.toggle("dark");
      localStorage.setItem("theme", isDark ? "dark" : "light");
      updateThemeIcons();
    });
  }

  // Mobile drawer controls
  const openMenuBtn = document.getElementById("open-menu-btn");
  const closeMenuBtn = document.getElementById("close-menu-btn");
  const mobileDrawer = document.getElementById("mobile-drawer");
  const drawerPanel = document.getElementById("mobile-menu");
  const drawerBackdrop = document.getElementById("drawer-backdrop");
  let lastDrawerTrigger = null;

  function openDrawer() {
    if (!mobileDrawer) return;
    lastDrawerTrigger = document.activeElement;
    mobileDrawer.classList.remove("opacity-0", "pointer-events-none");
    mobileDrawer.classList.add("opacity-100", "pointer-events-auto");
    mobileDrawer.setAttribute("aria-hidden", "false");
    mobileDrawer.removeAttribute("inert");
    if (drawerPanel) drawerPanel.classList.remove("-translate-x-full");
    if (openMenuBtn) openMenuBtn.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
  }

  function closeDrawer() {
    if (!mobileDrawer || mobileDrawer.getAttribute("aria-hidden") === "true") return;
    mobileDrawer.classList.add("opacity-0", "pointer-events-none");
    mobileDrawer.classList.remove("opacity-100", "pointer-events-auto");
    mobileDrawer.setAttribute("aria-hidden", "true");
    mobileDrawer.setAttribute("inert", "");
    if (drawerPanel) drawerPanel.classList.add("-translate-x-full");
    if (openMenuBtn) openMenuBtn.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
    if (lastDrawerTrigger) lastDrawerTrigger.focus();
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
  let lastSearchTrigger = null;

  function openSearch() {
    if (!searchModal) return;
    lastSearchTrigger = document.activeElement;
    searchModal.classList.remove("opacity-0", "pointer-events-none");
    searchModal.classList.add("opacity-100", "pointer-events-auto");
    searchModal.setAttribute("aria-hidden", "false");
    searchModal.removeAttribute("inert");
    document.body.style.overflow = "hidden";
    setTimeout(() => searchInput && searchInput.focus(), 50);
  }

  function closeSearch() {
    if (!searchModal || searchModal.getAttribute("aria-hidden") === "true") return;
    searchModal.classList.add("opacity-0", "pointer-events-none");
    searchModal.classList.remove("opacity-100", "pointer-events-auto");
    searchModal.setAttribute("aria-hidden", "true");
    searchModal.setAttribute("inert", "");
    document.body.style.overflow = "";
    if (lastSearchTrigger) lastSearchTrigger.focus();
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
  const searchSeeAllCount = document.getElementById("search-see-all-count");
  const escapeHtml = (value) =>
    String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");

  let searchTimer;
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      clearTimeout(searchTimer);
      const q = e.target.value.trim();
      if (q.length < 1) {
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
                  <a href="/product/${encodeURIComponent(p.slug)}/" class="group flex items-center gap-4 rounded-2xl p-3 transition-colors hover:bg-beige/70">
                    <span class="relative block h-14 w-14 shrink-0 overflow-hidden rounded-xl bg-beige">
                      <img src="/static/${p.image.replace(/^\//, '')}" alt="${escapeHtml(p.name)}" draggable="false" class="h-full w-full object-contain p-1">
                    </span>
                    <span class="min-w-0 flex-1">
                      <span class="block truncate text-sm font-semibold text-ink">${escapeHtml(p.name)}</span>
                      <span class="mt-0.5 block text-[11px] font-medium tracking-wide text-stone uppercase">${escapeHtml(p.category)}</span>
                    </span>
                    <span class="shrink-0 text-sm font-semibold text-gold-deep">${escapeHtml(p.price)}</span>
                  </a>
                `;
                searchResultsList.appendChild(li);
              });
            } else {
              const li = document.createElement("li");
              li.className = "rounded-2xl bg-cream px-5 py-4 text-sm text-stone";
              li.textContent = "No products match your search.";
              searchResultsList.appendChild(li);
            }
            if (searchSeeAllCount) searchSeeAllCount.textContent = data.total ?? data.results.length;
            searchResultsBox.classList.remove("hidden");
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

  // Product gallery + lightbox
  const mainImg = document.getElementById("main-product-img");
  const mainBtn = document.getElementById("gallery-main-btn");
  const galleryCounter = document.getElementById("gallery-counter");
  const gallerySources = Array.from(document.querySelectorAll("[data-gallery-src]")).map((el) => ({
    src: el.dataset.gallerySrc,
    alt: el.dataset.galleryAlt,
  }));
  const thumbs = Array.from(document.querySelectorAll(".gallery-thumb"));
  let galleryIndex = 0;

  function setGalleryIndex(index) {
    if (!gallerySources.length) return;
    galleryIndex = (index + gallerySources.length) % gallerySources.length;
    const current = gallerySources[galleryIndex];
    if (mainImg) {
      mainImg.src = current.src;
      mainImg.alt = current.alt;
    }
    if (galleryCounter) galleryCounter.textContent = `${galleryIndex + 1} / ${gallerySources.length}`;
    thumbs.forEach((thumb) => {
      const active = Number(thumb.dataset.index) === galleryIndex;
      thumb.setAttribute("aria-pressed", active ? "true" : "false");
      thumb.classList.toggle("ring-gold", active);
      thumb.classList.toggle("shadow-gold", active);
      thumb.classList.toggle("ring-transparent", !active);
      thumb.classList.toggle("opacity-60", !active);
    });
  }

  thumbs.forEach((thumb) => {
    thumb.addEventListener("click", () => setGalleryIndex(Number(thumb.dataset.index)));
  });

  const lightbox = document.getElementById("product-lightbox");
  const lightboxImg = document.getElementById("lightbox-img");
  const lightboxStage = document.getElementById("lightbox-stage");
  const lightboxCounter = document.getElementById("lightbox-counter");
  let zoom = 1;
  let panX = 0;
  let panY = 0;
  let dragging = false;
  let dragStart = null;

  function applyTransform() {
    if (lightboxImg) {
      lightboxImg.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom})`;
      lightboxImg.style.cursor = zoom > 1 ? "grab" : "default";
    }
  }

  function renderLightbox() {
    if (!lightboxImg) return;
    const current = gallerySources[galleryIndex];
    lightboxImg.src = current.src;
    lightboxImg.alt = current.alt;
    if (lightboxCounter) lightboxCounter.textContent = `${galleryIndex + 1} / ${gallerySources.length}`;
    zoom = 1;
    panX = 0;
    panY = 0;
    applyTransform();
  }

  function openLightbox() {
    if (!lightbox || !gallerySources.length) return;
    lightbox.classList.remove("hidden");
    document.body.style.overflow = "hidden";
    renderLightbox();
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.add("hidden");
    document.body.style.overflow = "";
  }

  if (mainBtn) mainBtn.addEventListener("click", openLightbox);
  const lightboxClose = document.getElementById("lightbox-close");
  const lightboxPrev = document.getElementById("lightbox-prev");
  const lightboxNext = document.getElementById("lightbox-next");
  if (lightboxClose) lightboxClose.addEventListener("click", closeLightbox);
  if (lightboxPrev) lightboxPrev.addEventListener("click", () => {
    setGalleryIndex(galleryIndex - 1);
    renderLightbox();
  });
  if (lightboxNext) lightboxNext.addEventListener("click", () => {
    setGalleryIndex(galleryIndex + 1);
    renderLightbox();
  });
  if (lightbox) {
    lightbox.addEventListener("click", (e) => {
      if (e.target === lightbox || e.target === lightboxStage) closeLightbox();
    });
    lightbox.addEventListener("wheel", (e) => {
      e.preventDefault();
      zoom = Math.min(4, Math.max(1, zoom - e.deltaY * 0.002));
      if (zoom === 1) {
        panX = 0;
        panY = 0;
      }
      applyTransform();
    }, { passive: false });
  }
  if (lightboxImg) {
    lightboxImg.addEventListener("pointerdown", (e) => {
      if (zoom <= 1) return;
      dragging = true;
      dragStart = { x: e.clientX - panX, y: e.clientY - panY };
      lightboxImg.setPointerCapture(e.pointerId);
      lightboxImg.style.cursor = "grabbing";
    });
    lightboxImg.addEventListener("pointermove", (e) => {
      if (!dragging) return;
      panX = e.clientX - dragStart.x;
      panY = e.clientY - dragStart.y;
      applyTransform();
    });
    lightboxImg.addEventListener("pointerup", () => {
      dragging = false;
      applyTransform();
    });
    lightboxImg.addEventListener("pointercancel", () => {
      dragging = false;
      applyTransform();
    });
  }
  document.addEventListener("keydown", (e) => {
    if (!lightbox || lightbox.classList.contains("hidden")) return;
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft") {
      setGalleryIndex(galleryIndex - 1);
      renderLightbox();
    }
    if (e.key === "ArrowRight") {
      setGalleryIndex(galleryIndex + 1);
      renderLightbox();
    }
  });

  // FAQ accordions
  document.querySelectorAll(".faq-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = btn.closest(".faq-item");
      const content = item.querySelector(".faq-content");
      const icon = item.querySelector(".faq-icon");
      const title = btn.querySelector("span");
      const isOpen = btn.getAttribute("aria-expanded") === "true";

      btn.setAttribute("aria-expanded", isOpen ? "false" : "true");
      content.classList.toggle("grid-rows-[1fr]", !isOpen);
      content.classList.toggle("opacity-100", !isOpen);
      content.classList.toggle("grid-rows-[0fr]", isOpen);
      content.classList.toggle("opacity-0", isOpen);
      icon.classList.toggle("rotate-180", !isOpen);
      icon.classList.toggle("border-gold", !isOpen);
      icon.classList.toggle("bg-gold", !isOpen);
      icon.classList.toggle("text-ink", !isOpen);
      icon.classList.toggle("border-ink/15", isOpen);
      icon.classList.toggle("text-gold-deep", isOpen);
      title.classList.toggle("text-gold-deep", !isOpen);
      title.classList.toggle("text-ink", isOpen);
    });
  });

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

  // Image protection – block right-click and drag-save on every image
  const blockImageAction = (e) => {
    if (e.target && e.target.tagName === "IMG") e.preventDefault();
  };
  document.addEventListener("contextmenu", blockImageAction, true);
  document.addEventListener("dragstart", blockImageAction, true);
  document.querySelectorAll("img").forEach((img) => {
    img.setAttribute("draggable", "false");
  });
});
