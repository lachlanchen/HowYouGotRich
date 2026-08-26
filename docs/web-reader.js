"use strict";

const READING_STATE_KEY = "how-you-got-rich:web-reading-state";

function setupSiteMenu() {
  const button = document.querySelector(".menu-button");
  const navigation = document.querySelector(".site-nav");
  if (!button || !navigation) return;

  button.addEventListener("click", () => {
    const open = navigation.classList.toggle("open");
    button.setAttribute("aria-expanded", String(open));
  });
}

function setupContents() {
  const contents = document.querySelector("#web-reader-toc");
  const openButton = document.querySelector("#web-toc-toggle");
  const closeButton = document.querySelector("#web-toc-close");
  if (!contents || !openButton) return;

  const setOpen = (open) => {
    contents.classList.toggle("open", open);
    document.body.classList.toggle("contents-open", open);
    openButton.setAttribute("aria-expanded", String(open));
  };

  openButton.addEventListener("click", () => setOpen(!contents.classList.contains("open")));
  closeButton?.addEventListener("click", () => setOpen(false));
  contents.addEventListener("click", (event) => {
    if (event.target.closest("a")) setOpen(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setOpen(false);
  });
}

function setupContentsFilter() {
  const input = document.querySelector("#web-toc-search");
  if (!input) return;

  input.addEventListener("input", () => {
    const query = input.value.trim().toLocaleLowerCase();
    for (const group of document.querySelectorAll("[data-toc-group]")) {
      let visible = 0;
      for (const entry of group.querySelectorAll(".web-toc-entry")) {
        const matches = !query || entry.dataset.search.includes(query);
        entry.hidden = !matches;
        if (matches) visible += 1;
      }
      group.hidden = visible === 0;
    }
  });
}

function setupReadingProgress() {
  const bar = document.querySelector("#reading-progress-bar");
  if (!bar) return;

  let scheduled = false;
  const update = () => {
    const root = document.documentElement;
    const maximum = root.scrollHeight - root.clientHeight;
    const progress = maximum > 0 ? root.scrollTop / maximum : 0;
    bar.style.transform = `scaleX(${Math.min(1, Math.max(0, progress))})`;
    scheduled = false;
  };
  const requestUpdate = () => {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(update);
  };

  update();
  window.addEventListener("scroll", requestUpdate, { passive: true });
  window.addEventListener("resize", requestUpdate);
}

function rememberReadingPosition() {
  const title = document.querySelector(".chapter-masthead h1")?.textContent?.trim();
  if (!title) return;
  const state = {
    path: window.location.pathname,
    title,
    savedAt: new Date().toISOString(),
  };
  try {
    window.localStorage.setItem(READING_STATE_KEY, JSON.stringify(state));
  } catch {
    // Reading remains fully usable when storage is disabled.
  }
}

function setupSectionTracking() {
  const links = [...document.querySelectorAll(".web-on-this-page a")];
  const sections = links
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);
  if (!sections.length || !("IntersectionObserver" in window)) return;

  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((left, right) => left.boundingClientRect.top - right.boundingClientRect.top)[0];
      if (!visible) return;
      for (const link of links) {
        link.classList.toggle("active", link.hash === `#${visible.target.id}`);
      }
    },
    { rootMargin: "-18% 0px -70% 0px", threshold: [0, 1] },
  );
  sections.forEach((section) => observer.observe(section));
}

setupSiteMenu();
setupContents();
setupContentsFilter();
setupReadingProgress();
setupSectionTracking();
rememberReadingPosition();
