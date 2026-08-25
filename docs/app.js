"use strict";

const BOOK_DATA = "data/book.json";

function setupMenu() {
  const button = document.querySelector(".menu-button");
  const navigation = document.querySelector(".site-nav");
  if (!button || !navigation) return;

  button.addEventListener("click", () => {
    const open = navigation.classList.toggle("open");
    button.setAttribute("aria-expanded", String(open));
  });

  navigation.addEventListener("click", () => {
    navigation.classList.remove("open");
    button.setAttribute("aria-expanded", "false");
  });
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function readerUrl(chapter, edition = "full") {
  const page = edition === "pocket" ? chapter.pagePocket : chapter.pageFull;
  const chapterValue = chapter.number === undefined ? "intro" : chapter.number;
  const params = new URLSearchParams({ edition, page, chapter: chapterValue });
  return `reader.html?${params.toString()}`;
}

function renderLanding(book) {
  const grid = document.querySelector("#part-grid");
  if (!grid) return;

  for (const part of book.parts) {
    const card = element("a", "part-card");
    card.href = `book.html#part-${part.number.toLowerCase()}`;
    card.append(element("span", "part-number", `PART ${part.number}`));
    card.append(element("h3", "", part.title));
    card.append(element("p", "", part.question));
    card.append(element("small", "", `${part.chapters.length} CHAPTERS`));
    grid.append(card);
  }
}

function renderWebBook(book) {
  const outline = document.querySelector("#book-outline");
  if (!outline) return;

  for (const part of book.parts) {
    const section = element("section", "book-part");
    section.id = `part-${part.number.toLowerCase()}`;

    const heading = element("header", "book-part-heading");
    heading.append(element("span", "", `PART ${part.number}`));
    heading.append(element("h3", "", part.title));
    heading.append(element("p", "", part.question));

    const chapters = element("div", "chapter-list");
    for (const chapter of part.chapters) {
      const link = element("a", "chapter-card");
      link.href = readerUrl(chapter);
      link.append(element("span", "chapter-number", String(chapter.number).padStart(2, "0")));
      link.append(element("h4", "", chapter.title));
      link.append(element("p", "", chapter.question));
      link.append(element("span", "open-mark", "↗"));
      chapters.append(link);
    }

    section.append(heading, chapters);
    outline.append(section);
  }
}

function allReaderEntries(book) {
  return [
    { ...book.introduction, number: undefined, part: "Introduction" },
    ...book.parts.flatMap((part) =>
      part.chapters.map((chapter) => ({ ...chapter, part: part.title, partNumber: part.number })),
    ),
  ];
}

function renderReader(book) {
  const frame = document.querySelector("#pdf-frame");
  const toc = document.querySelector("#reader-toc");
  const editionSelect = document.querySelector("#edition-select");
  if (!frame || !toc || !editionSelect) return;

  const location = document.querySelector("#reader-location");
  const download = document.querySelector("#download-link");
  const external = document.querySelector("#external-pdf-link");
  const outline = document.querySelector("#reader-outline");
  const outlineToggle = document.querySelector("#outline-toggle");
  const entries = allReaderEntries(book);
  const query = new URL(window.location.href).searchParams;
  const initialEdition = query.get("edition") === "pocket" ? "pocket" : "full";
  const requestedChapter = query.get("chapter");
  const requestedPage = Number.parseInt(query.get("page") || "1", 10);
  let edition = initialEdition;
  let active = entries.find((entry) =>
    requestedChapter === "intro"
      ? entry.number === undefined
      : String(entry.number) === requestedChapter,
  );

  editionSelect.value = edition;

  const introButton = element("button", "toc-introduction");
  introButton.type = "button";
  introButton.dataset.entry = "intro";
  introButton.append(element("span", "toc-number", "00"));
  introButton.append(element("span", "toc-title", book.introduction.title));
  toc.append(introButton);

  for (const part of book.parts) {
    toc.append(element("p", "toc-part", `PART ${part.number} · ${part.title}`));
    for (const chapter of part.chapters) {
      const button = element("button", "toc-chapter");
      button.type = "button";
      button.dataset.entry = String(chapter.number);
      button.append(element("span", "toc-number", String(chapter.number).padStart(2, "0")));
      button.append(element("span", "toc-title", chapter.title));
      toc.append(button);
    }
  }

  function editionFile() {
    return book.editions[edition].file;
  }

  function pageFor(entry) {
    return edition === "pocket" ? entry.pagePocket : entry.pageFull;
  }

  function updateButtons() {
    for (const button of toc.querySelectorAll("button")) {
      const key = active?.number === undefined ? "intro" : String(active?.number || "");
      button.classList.toggle("active", button.dataset.entry === key);
    }
  }

  function openPage(page, entry, replace = false) {
    const boundedPage = Math.max(1, Math.min(page, book.editions[edition].pages));
    const pdf = editionFile();
    // A changing query forces embedded browser PDF viewers to honor each new
    // page fragment instead of retaining the first document view.
    frame.src = `${pdf}?readerPage=${boundedPage}#page=${boundedPage}&view=FitH`;
    download.href = pdf;
    external.href = `${pdf}#page=${boundedPage}&view=FitH`;
    active = entry || null;
    location.textContent = active
      ? `${book.editions[edition].label} · ${active.title}`
      : `${book.editions[edition].label} · page ${boundedPage}`;
    updateButtons();

    const params = new URLSearchParams({ edition, page: String(boundedPage) });
    if (active) params.set("chapter", active.number === undefined ? "intro" : String(active.number));
    const method = replace ? "replaceState" : "pushState";
    window.history[method](null, "", `?${params.toString()}`);
  }

  toc.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-entry]");
    if (!button) return;
    const entry = button.dataset.entry === "intro"
      ? entries[0]
      : entries.find((candidate) => String(candidate.number) === button.dataset.entry);
    if (!entry) return;
    openPage(pageFor(entry), entry);
    outline?.classList.remove("open");
    outlineToggle?.setAttribute("aria-expanded", "false");
  });

  editionSelect.addEventListener("change", () => {
    edition = editionSelect.value === "pocket" ? "pocket" : "full";
    openPage(active ? pageFor(active) : 1, active);
  });

  outlineToggle?.addEventListener("click", () => {
    const open = outline?.classList.toggle("open") || false;
    outlineToggle.setAttribute("aria-expanded", String(open));
  });

  const initialPage = active ? pageFor(active) : Number.isFinite(requestedPage) ? requestedPage : 1;
  openPage(initialPage, active, true);
}

async function start() {
  setupMenu();
  try {
    const response = await fetch(BOOK_DATA);
    if (!response.ok) throw new Error(`Book manifest returned ${response.status}`);
    const book = await response.json();
    renderLanding(book);
    renderWebBook(book);
    renderReader(book);
  } catch (error) {
    const target = document.querySelector("#part-grid, #book-outline, #reader-toc");
    if (target) {
      const message = element("p", "load-error", "The book navigation could not be loaded. Use the direct PDF link instead.");
      target.append(message);
    }
    console.error(error);
  }
}

start();
