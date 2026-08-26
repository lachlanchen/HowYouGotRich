#!/usr/bin/env python3
"""Build the native HTML edition from the accepted V3 LaTeX manuscript."""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
import shutil
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path

from multilingual_common import load_entry
from multilingual_render import annotate_html, render_html_blocks


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BOOK_ROOT = ROOT / "source" / "book"
MANUSCRIPT = BOOK_ROOT / "manuscript"
CHAPTER_OUTPUT = DOCS / "chapters"
FIGURE_OUTPUT = DOCS / "assets" / "figures"
BOOK_DATA_PATH = DOCS / "data" / "book.json"
WEB_MANIFEST_PATH = DOCS / "data" / "web-edition.json"
SEARCH_INDEX_PATH = DOCS / "data" / "search-index.json"
SITE_URL = "https://lachlanchen.github.io/HowYouGotRich"
LANGUAGES = ("en", "ja", "zh")
LANGUAGE_LABELS = {"en": "EN", "ja": "日本語", "zh": "中文"}


@dataclass(frozen=True)
class Entry:
    slug: str
    title: str
    question: str
    source_path: Path
    source_text: str
    label: str
    number: int | None = None
    part_number: str | None = None
    part_title: str | None = None


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def digest_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def digest_text(content: str) -> str:
    return digest_bytes(content.encode("utf-8"))


def plain_text(fragment: str) -> str:
    parser = TextExtractor()
    parser.feed(fragment)
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def word_count(fragment: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", plain_text(fragment), re.UNICODE))


@lru_cache(maxsize=None)
def aligned_entry(slug: str) -> dict:
    return load_entry(slug)


def localized_inline(value: str, language: str) -> str:
    escaped = html.escape(value, quote=False)
    return escaped if language == "en" else annotate_html(escaped, language)


def localized_layers(values: dict[str, str], *, element: str = "span") -> str:
    return "".join(
        f'<{element} class="localized-layer" data-language="{language}" '
        f'lang="{language}">{localized_inline(values[language], language)}</{element}>'
        for language in LANGUAGES
    )


def figure_with_translated_captions(rendered: dict[str, str]) -> str:
    figure = rendered["en"]
    captions: list[str] = []
    for language in ("ja", "zh"):
        match = re.search(r"<figcaption>(.*?)</figcaption>", rendered[language], re.DOTALL)
        if match:
            captions.append(
                f'<p class="translated-caption" lang="{language}" '
                f'data-language="{language}"><strong>{LANGUAGE_LABELS[language]}</strong> '
                f'{match.group(1)}</p>'
            )
    if captions and "</figure>" in figure:
        figure = figure.rsplit("</figure>", 1)[0]
        figure += '<div class="figure-caption-translations">' + "".join(captions)
        figure += "</div></figure>"
    return figure


def multilingual_fragment(entry_data: dict) -> tuple[str, dict[str, dict[str, str]]]:
    rendered = {
        language: render_html_blocks(entry_data, language) for language in LANGUAGES
    }
    units: list[str] = []
    for block in entry_data["blocks"]:
        block_id = str(block["id"])
        fragments = {language: rendered[language][block_id] for language in LANGUAGES}
        protected = {str(item.get("type")) for item in block.get("protected", [])}
        classes = ["aligned-block", f'aligned-{str(block["kind"]).lower()}']
        anchor = ""
        heading = re.search(r'<h[1-6] id="([^"]+)"', fragments["en"])
        if heading:
            anchor = f' id="{html.escape(heading.group(1), quote=True)}"'
            fragments = {
                language: re.sub(r'(<h[1-6]) id="[^"]+"', r"\1", fragment, count=1)
                for language, fragment in fragments.items()
            }

        if "image" in protected:
            classes.append("aligned-figure")
            content = (
                '<div class="language-layer language-shared" data-language="shared">'
                + figure_with_translated_captions(fragments)
                + "</div>"
            )
        elif protected == {"math"} and len({block[code]["markdown"] for code in LANGUAGES}) == 1:
            classes.append("aligned-shared")
            content = (
                '<div class="language-layer language-shared" data-language="shared">'
                + fragments["en"]
                + "</div>"
            )
        else:
            content = "".join(
                f'<div class="language-layer language-{language}" '
                f'data-language="{language}" data-label="{LANGUAGE_LABELS[language]}" '
                f'lang="{language}">{fragments[language]}</div>'
                for language in LANGUAGES
            )
        units.append(
            f'<section class="{" ".join(classes)}" data-block-id="{block_id}"{anchor}>'
            f"{content}</section>"
        )
    return "\n".join(units), rendered


def choose_responsive_tex(source: str) -> str:
    """Choose the accepted narrow-page equation branch for responsive HTML."""

    pattern = re.compile(
        r"\\ifdim\\paperwidth<450pt(?P<narrow>.*?)\\else(?P<wide>.*?)\\fi",
        re.DOTALL,
    )
    result = source
    while pattern.search(result):
        result = pattern.sub(lambda match: match.group("narrow"), result)
    if re.search(r"\\(?:ifdim|else|fi)\b", result):
        raise ValueError("unsupported TeX conditional remains after preprocessing")
    return result


def prepare_tex(source: str) -> str:
    result = choose_responsive_tex(source)
    result = re.sub(r"\\addcontentsline\{[^{}]*\}\{[^{}]*\}\{[^{}]*\}", "", result)
    result = re.sub(r"\\(?:chaptermark|markboth)\{[^{}]*\}(?:\{[^{}]*\})?", "", result)
    result = re.sub(r"\\enlargethispage\{[^{}]*\}", "", result)
    result = re.sub(r"\\vspace\*?\{[^{}]*\}", "", result)
    result = re.sub(r"\\(?:clearpage|cleardoublepage|newpage|pagebreak)\b", "", result)
    return result.strip() + "\n"


def pandoc_fragment(source: str) -> str:
    if not shutil.which("pandoc"):
        raise SystemExit("pandoc is required to build the native web edition")
    result = subprocess.run(
        [
            "pandoc",
            "--from=latex",
            "--to=html5",
            "--mathjax",
            "--wrap=none",
        ],
        input=prepare_tex(source),
        text=True,
        capture_output=True,
        check=True,
    )
    if result.stderr.strip():
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def polish_fragment(fragment: str, figure_names: set[str]) -> str:
    fragment = re.sub(r"^\s*<h1\b[^>]*>.*?</h1>", "", fragment, count=1, flags=re.DOTALL)
    fragment = fragment.replace(' aria-hidden="true"', "")

    def replace_image(match: re.Match[str]) -> str:
        source = match.group(1)
        name = Path(source).name
        if name not in figure_names:
            raise ValueError(f"HTML references an unrecognized figure: {source}")
        return f'src="../assets/figures/{html.escape(name, quote=True)}" loading="lazy" decoding="async"'

    fragment = re.sub(r'src="([^"]+\.(?:jpg|jpeg|png|webp))"', replace_image, fragment)
    return fragment.strip()


def heading_sections(fragment: str, entry: Entry) -> list[dict[str, str]]:
    marker = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.DOTALL)
    matches = list(marker.finditer(fragment))
    records: list[dict[str, str]] = []

    opening_end = matches[0].start() if matches else len(fragment)
    opening = plain_text(fragment[:opening_end])
    if opening:
        records.append(
            {
                "chapter": entry.title,
                "section": "Opening",
                "href": f"chapters/{entry.slug}.html",
                "text": opening,
                "language": "en",
            }
        )

    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(fragment)
        records.append(
            {
                "chapter": entry.title,
                "section": plain_text(match.group(2)),
                "href": f"chapters/{entry.slug}.html#{match.group(1)}",
                "text": plain_text(fragment[match.end() : end]),
                "language": "en",
            }
        )
    return records


def section_navigation(fragment: str) -> str:
    links = []
    for section_id, section_html in re.findall(
        r'<h2 id="([^"]+)">(.*?)</h2>', fragment, flags=re.DOTALL
    ):
        title = plain_text(section_html)
        links.append(
            f'<a href="#{html.escape(section_id, quote=True)}">{html.escape(title)}</a>'
        )
    if not links:
        return "<!-- This reading has no internal section headings. -->"
    return (
        '<div class="web-on-this-page">'
        '<p>IN THIS CHAPTER</p>'
        + "".join(links)
        + "</div>"
    )


def entry_href(entry: Entry) -> str:
    return f"{entry.slug}.html"


def build_contents(entries: list[Entry], current: Entry, parts: list[dict]) -> str:
    by_number = {entry.number: entry for entry in entries if entry.number is not None}
    preface = next(entry for entry in entries if entry.slug == "note-on-the-conversations")
    introduction = next(entry for entry in entries if entry.slug == "introduction")

    def link(entry: Entry, number: str) -> str:
        active = entry.slug == current.slug
        active_class = " active" if active else ""
        current_attr = ' aria-current="page"' if active else ""
        metadata = aligned_entry(entry.slug)["metadata"]
        search = html.escape(
            " ".join(metadata["title"].values()).lower()
            + " "
            + " ".join(metadata["question"].values()).lower(),
            quote=True,
        )
        return (
            f'<a class="web-toc-entry{active_class}" href="{entry_href(entry)}"'
            f' data-search="{search}"{current_attr}>'
            f'<span>{number}</span><strong>{localized_layers(metadata["title"])}</strong></a>'
        )

    groups = [
        '<div class="web-toc-group" data-toc-group="opening">'
        '<p class="web-toc-part">OPENING</p>'
        + link(preface, "N")
        + link(introduction, "00")
        + "</div>"
    ]
    for part in parts:
        chapter_links = "".join(
            link(by_number[chapter["number"]], str(chapter["number"]).zfill(2))
            for chapter in part["chapters"]
        )
        groups.append(
            f'<div class="web-toc-group" data-toc-group="part-{part["number"].lower()}">'
            f'<p class="web-toc-part">PART {html.escape(part["number"])} · '
            f'{html.escape(part["title"])}</p>{chapter_links}</div>'
        )
    return "".join(groups)


def page_template(
    entry: Entry,
    fragment: str,
    navigation_fragment: str,
    entries: list[Entry],
    parts: list[dict],
) -> str:
    index = entries.index(entry)
    previous = entries[index - 1] if index else None
    following = entries[index + 1] if index + 1 < len(entries) else None
    words = word_count(navigation_fragment)
    minutes = max(1, math.ceil(words / 230))
    position = index + 1
    eyebrow = entry.label
    if entry.part_number:
        eyebrow = f"PART {entry.part_number} · {entry.part_title}"

    previous_title = (
        localized_layers(aligned_entry(previous.slug)["metadata"]["title"])
        if previous
        else ""
    )
    following_title = (
        localized_layers(aligned_entry(following.slug)["metadata"]["title"])
        if following
        else ""
    )
    previous_link = (
        f'<a class="chapter-nav-link previous" href="{entry_href(previous)}">'
        f'<span>PREVIOUS</span><strong>{previous_title}</strong></a>'
        if previous
        else '<span class="chapter-nav-spacer"></span>'
    )
    next_link = (
        f'<a class="chapter-nav-link next" href="{entry_href(following)}">'
        f'<span>NEXT</span><strong>{following_title}</strong></a>'
        if following
        else (
            '<a class="chapter-nav-link next" href="../book.html">'
            '<span>FINISHED</span><strong>Return to the book map</strong></a>'
        )
    )
    continue_link = (
        f'<a href="{entry_href(following)}"><span>CONTINUE READING</span>'
        f'<strong>{following_title}</strong><b aria-hidden="true">→</b></a>'
        if following
        else (
            '<a href="../book.html"><span>THE END</span>'
            '<strong>Return to the complete argument</strong><b aria-hidden="true">→</b></a>'
        )
    )
    metadata = aligned_entry(entry.slug)["metadata"]
    question = f'<p class="chapter-question">{localized_layers(metadata["question"])}</p>'
    description = entry.question or "Read the native HTML edition of How You Got Rich."
    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Chapter",
            "name": entry.title,
            "isPartOf": {
                "@type": "Book",
                "name": "How You Got Rich",
                "author": {"@type": "Organization", "name": "LazyingArt · LazyLearn"},
            },
            "position": position,
            "url": f"{SITE_URL}/chapters/{entry.slug}.html",
        },
        ensure_ascii=False,
    )

    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#f5efdf">
    <meta name="description" content="{html.escape(description, quote=True)}">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{html.escape(entry.title, quote=True)} · How You Got Rich">
    <meta property="og:description" content="{html.escape(description, quote=True)}">
    <meta property="og:image" content="{SITE_URL}/assets/cover-page-1.png">
    <title>{html.escape(entry.title)} · How You Got Rich</title>
    <link rel="canonical" href="{SITE_URL}/chapters/{entry.slug}.html">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Literata:opsz,wght@7..72,400;7..72,600;7..72,700&family=Noto+Serif+JP:wght@400;600&family=Noto+Serif+SC:wght@400;600&family=Public+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../styles.css">
    <link rel="icon" href="../favicon.svg" type="image/svg+xml">
    <script type="application/ld+json">{schema}</script>
    <script>
      window.MathJax = {{
        tex: {{ tags: "ams", inlineMath: [["\\\\(", "\\\\)"]], displayMath: [["\\\\[", "\\\\]"]] }},
        chtml: {{ scale: 0.96 }},
        options: {{ skipHtmlTags: ["script", "noscript", "style", "textarea", "pre", "code"] }}
      }};
    </script>
    <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
    <script src="../web-reader.js" defer></script>
  </head>
  <body class="native-reader-page" data-page="{html.escape(entry.slug, quote=True)}" data-language-mode="en">
    <a class="skip-link" href="#chapter-main">Skip to the chapter</a>
    <div class="reading-progress" aria-hidden="true"><span id="reading-progress-bar"></span></div>
    <header class="site-header compact reading-site-header">
      <a class="wordmark" href="../index.html"><span>HOW YOU</span><strong>GOT RICH</strong></a>
      <button id="web-toc-toggle" class="web-toc-toggle" type="button" aria-expanded="false" aria-controls="web-reader-toc">Contents</button>
      <button class="menu-button" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
      <nav id="site-nav" class="site-nav" aria-label="Primary navigation">
        <a href="../book.html">Book map</a>
        <a href="../reader.html">PDF editions</a>
        <a href="https://github.com/lachlanchen/HowYouGotRich">GitHub</a>
      </nav>
    </header>

    <div class="web-reader-shell">
      <aside id="web-reader-toc" class="web-reader-toc" aria-label="Book contents">
        <header class="web-toc-head">
          <div><span>WEB EDITION</span><strong>25 readings · V3</strong></div>
          <button id="web-toc-close" type="button" aria-label="Close contents">Close</button>
          <label for="web-toc-search">Find a chapter</label>
          <input id="web-toc-search" type="search" placeholder="Value, risk, enough…" autocomplete="off">
        </header>
        {section_navigation(navigation_fragment)}
        <nav class="web-toc-list" aria-label="Chapters">
          {build_contents(entries, entry, parts)}
        </nav>
      </aside>

      <main id="chapter-main" class="web-reader-main">
        <article class="native-chapter">
          <header class="chapter-masthead">
            <p class="eyebrow">{html.escape(eyebrow)}</p>
            <h1>{localized_layers(metadata["title"])}</h1>
            {question}
            <div class="chapter-meta">
              <span>{minutes} MIN READ</span>
              <span>{position} OF {len(entries)}</span>
              <span>V3 WEB EDITION</span>
            </div>
            <div class="language-switcher" role="group" aria-label="Reading language">
              <span>READ IN</span>
              <button type="button" data-language-option="en" aria-pressed="true">EN</button>
              <button type="button" data-language-option="ja" aria-pressed="false">日本語</button>
              <button type="button" data-language-option="zh" aria-pressed="false">中文</button>
              <button type="button" data-language-option="all" aria-pressed="false">Together</button>
            </div>
          </header>
          <div class="chapter-body">
            {fragment}
          </div>
          <footer class="chapter-end">
            {continue_link}
          </footer>
        </article>

        <nav class="chapter-pagination" aria-label="Chapter navigation">
          {previous_link}
          <a class="chapter-map-link" href="../book.html">ALL CHAPTERS</a>
          {next_link}
        </nav>

        <footer class="site-footer web-reader-footer">
          <div><strong>How You Got Rich</strong><p>Written and curated by <a href="https://lazying.art">LazyingArt</a> · <a href="https://learn.lazying.art">LazyLearn</a></p></div>
          <nav aria-label="Footer navigation"><a href="../book.html">Book map</a><a href="../reader.html">PDF editions</a><a href="https://github.com/lachlanchen/HowYouGotRich">Contribute</a></nav>
        </footer>
      </main>
    </div>
  </body>
</html>
'''


def build_entries(book: dict) -> list[Entry]:
    frontmatter_path = MANUSCRIPT / "frontmatter.tex"
    frontmatter = frontmatter_path.read_text(encoding="utf-8")
    marker = r"\chapter*{A Note on the Conversations}"
    marker_index = frontmatter.find(marker)
    if marker_index < 0:
        raise ValueError("could not locate the conversations note in frontmatter.tex")

    entries = [
        Entry(
            slug="note-on-the-conversations",
            title="A Note on the Conversations",
            question="How should success stories be read without turning experience into law?",
            source_path=frontmatter_path,
            source_text=frontmatter[marker_index:],
            label="A NOTE ON THE SOURCES",
        ),
        Entry(
            slug="introduction",
            title=book["introduction"]["title"],
            question=book["introduction"]["question"],
            source_path=MANUSCRIPT / "introduction.tex",
            source_text=(MANUSCRIPT / "introduction.tex").read_text(encoding="utf-8"),
            label="INTRODUCTION",
        ),
    ]
    for part in book["parts"]:
        for chapter in part["chapters"]:
            number = chapter["number"]
            path = MANUSCRIPT / "chapters" / f"ch{number:02d}.tex"
            entries.append(
                Entry(
                    slug=f"ch{number:02d}",
                    title=chapter["title"],
                    question=chapter["question"],
                    source_path=path,
                    source_text=path.read_text(encoding="utf-8"),
                    label=f"CHAPTER {number}",
                    number=number,
                    part_number=part["number"],
                    part_title=part["title"],
                )
            )
    return entries


def main() -> int:
    book = json.loads(BOOK_DATA_PATH.read_text(encoding="utf-8"))
    entries = build_entries(book)
    figure_source = MANUSCRIPT / "figures"
    figure_names = {path.name for path in figure_source.iterdir() if path.is_file()}

    CHAPTER_OUTPUT.mkdir(parents=True, exist_ok=True)
    FIGURE_OUTPUT.mkdir(parents=True, exist_ok=True)
    for stale in CHAPTER_OUTPUT.glob("*.html"):
        stale.unlink()
    for stale in FIGURE_OUTPUT.iterdir():
        if stale.is_file():
            stale.unlink()
    for figure in figure_source.iterdir():
        if figure.is_file():
            shutil.copy2(figure, FIGURE_OUTPUT / figure.name)

    manifest_entries: list[dict] = []
    search_records: list[dict[str, str]] = []
    for entry in entries:
        entry_data = aligned_entry(entry.slug)
        fragment, rendered = multilingual_fragment(entry_data)
        english_fragment = "\n".join(
            rendered["en"][str(block["id"])] for block in entry_data["blocks"]
        )
        page = page_template(entry, fragment, english_fragment, entries, book["parts"])
        output_path = CHAPTER_OUTPUT / f"{entry.slug}.html"
        output_path.write_text(page, encoding="utf-8")
        sections = heading_sections(english_fragment, entry)
        search_records.extend(sections)
        for language in ("ja", "zh"):
            search_records.append(
                {
                    "chapter": entry_data["metadata"]["title"][language],
                    "section": "全文",
                    "href": f"chapters/{entry.slug}.html?lang={language}",
                    "text": plain_text(" ".join(rendered[language].values())),
                    "language": language,
                }
            )
        manifest_entries.append(
            {
                "slug": entry.slug,
                "title": entry.title,
                "source": str(entry.source_path.relative_to(ROOT)),
                "sourceSha256": digest_bytes(entry.source_path.read_bytes()),
                "output": str(output_path.relative_to(DOCS)),
                "outputSha256": digest_text(page),
                "words": word_count(english_fragment),
                "alignedBlocks": len(entry_data["blocks"]),
                "sections": len(sections),
                "displayMath": english_fragment.count('class="math display"'),
                "inlineMath": english_fragment.count('class="math inline"'),
                "figures": len(re.findall(r'src="\.\./assets/figures/[^"]+"', english_fragment)),
                "tables": english_fragment.count("<table>"),
            }
        )

    manifest = {
        "title": book["title"],
        "bookVersion": book["version"],
        "generator": "scripts/build-web-edition.py",
        "sourceFormat": "aligned Markdown derived from accepted V3 LaTeX",
        "languages": list(LANGUAGES),
        "languageModes": ["en", "ja", "zh", "all"],
        "entryCount": len(entries),
        "totalWords": sum(entry["words"] for entry in manifest_entries),
        "alignedBlocks": sum(entry["alignedBlocks"] for entry in manifest_entries),
        "entries": manifest_entries,
        "figures": sorted(figure_names),
    }
    search_index = {
        "title": book["title"],
        "bookVersion": book["version"],
        "recordCount": len(search_records),
        "records": search_records,
    }
    WEB_MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    SEARCH_INDEX_PATH.write_text(
        json.dumps(search_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"Built native web edition: {len(entries)} readings, "
        f"{manifest['totalWords']:,} words, {len(search_records)} searchable sections."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
