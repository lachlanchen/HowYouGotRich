#!/usr/bin/env python3
"""Validate the assembled static book website using only the standard library."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


EXPECTED_FILES = {
    "index.html",
    "reader.html",
    "book.html",
    "web-reader.js",
    "styles.css",
    "app.js",
    "favicon.svg",
    "site.webmanifest",
    "data/book.json",
    "data/web-edition.json",
    "data/search-index.json",
    "assets/cover-page-1.png",
    "editions/how-you-got-rich.pdf",
    "editions/how-you-got-rich-pocket-1.2x.pdf",
    "editions/v2/how-you-got-rich-v2.pdf",
    "editions/v2/how-you-got-rich-v2-pocket-1.2x.pdf",
    "editions/v3/how-you-got-rich-v3.pdf",
    "editions/v3/how-you-got-rich-v3-pocket-1.2x.pdf",
    "editions/languages/how-you-got-rich-en.pdf",
    "editions/languages/how-you-got-rich-en-pocket-1.2x.pdf",
    "editions/languages/how-you-got-rich-ja.pdf",
    "editions/languages/how-you-got-rich-ja-pocket-1.2x.pdf",
    "editions/languages/how-you-got-rich-zh.pdf",
    "editions/languages/how-you-got-rich-zh-pocket-1.2x.pdf",
    "editions/languages/how-you-got-rich-en-ja-zh.pdf",
    "editions/languages/how-you-got-rich-en-ja-zh-pocket-1.2x.pdf",
    "assets/figures/ch01-tony-stephens-ribbon.jpg",
    "assets/figures/ch20-carlton-dennis-tax-board.jpg",
}
PUBLIC_LEAK_PATTERNS = (
    re.compile(r"\bcodex\b", re.IGNORECASE),
    re.compile(r"\btmux\b", re.IGNORECASE),
    re.compile(r"/home/lachlan", re.IGNORECASE),
    re.compile(r"private conversation", re.IGNORECASE),
    re.compile(r"prompt tool", re.IGNORECASE),
)


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for name in ("href", "src"):
            value = values.get(name)
            if value:
                self.links.append(value)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pdf_pages(path: Path) -> int | None:
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    match = re.search(r"^Pages:\s+(\d+)$", result.stdout, re.MULTILINE)
    return int(match.group(1)) if match else None


def validate_links(site_root: Path, errors: list[str]) -> None:
    for html_path in sorted(site_root.rglob("*.html")):
        parser = LinkCollector()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for raw_link in parser.links:
            parsed = urlparse(raw_link)
            if parsed.scheme or parsed.netloc or raw_link.startswith(("#", "mailto:")):
                continue
            clean = unquote(parsed.path)
            if not clean:
                continue
            target = (html_path.parent / clean).resolve()
            try:
                target.relative_to(site_root.resolve())
            except ValueError:
                fail(errors, f"{html_path.relative_to(site_root)}: link escapes site root: {raw_link}")
                continue
            if not target.exists():
                fail(errors, f"{html_path.relative_to(site_root)}: missing local target: {raw_link}")


def validate_manifest(site_root: Path, errors: list[str]) -> None:
    manifest_path = site_root / "data/book.json"
    try:
        book = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"invalid book manifest: {exc}")
        return

    parts = book.get("parts", [])
    if len(parts) != 5:
        fail(errors, f"expected 5 parts, found {len(parts)}")

    chapters = [chapter for part in parts for chapter in part.get("chapters", [])]
    numbers = [chapter.get("number") for chapter in chapters]
    if numbers != list(range(1, 24)):
        fail(errors, f"chapter sequence is not 1 through 23: {numbers}")

    web_edition = book.get("webEdition", {})
    if web_edition.get("status") != "complete":
        fail(errors, "native web edition is not marked complete")
    if web_edition.get("readings") != 25:
        fail(errors, f"expected 25 native readings, found {web_edition.get('readings')}")
    if web_edition.get("alignedBlocks") != 1164:
        fail(errors, f"expected 1164 aligned web blocks, found {web_edition.get('alignedBlocks')}")
    if web_edition.get("languages") != ["en", "ja", "zh"]:
        fail(errors, f"book manifest languages are incorrect: {web_edition.get('languages')}")
    if web_edition.get("modes") != ["en", "ja", "zh", "all"]:
        fail(errors, f"book manifest language modes are incorrect: {web_edition.get('modes')}")

    editions = book.get("editions", {})
    for key, page_field in (("full", "pageFull"), ("pocket", "pagePocket")):
        edition = editions.get(key, {})
        file_name = edition.get("file")
        declared_pages = edition.get("pages")
        if not isinstance(file_name, str):
            fail(errors, f"edition {key} has no file")
            continue
        pdf_path = site_root / file_name
        actual_pages = pdf_pages(pdf_path)
        if actual_pages is not None and actual_pages != declared_pages:
            fail(errors, f"{key} page count: manifest {declared_pages}, PDF {actual_pages}")

        targets = [book.get("introduction", {}).get(page_field)] + [
            chapter.get(page_field) for chapter in chapters
        ]
        if not all(isinstance(page, int) for page in targets):
            fail(errors, f"{key} contains a non-integer chapter page target")
        elif targets != sorted(targets):
            fail(errors, f"{key} chapter page targets are not increasing")
        elif declared_pages and targets[-1] > declared_pages:
            fail(errors, f"{key} chapter page target exceeds edition length")


def validate_web_edition(site_root: Path, errors: list[str]) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = site_root / "data/web-edition.json"
    search_path = site_root / "data/search-index.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        search = json.loads(search_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"invalid native web data: {exc}")
        return

    entries = manifest.get("entries", [])
    if manifest.get("entryCount") != 25 or len(entries) != 25:
        fail(errors, f"native edition must contain 25 readings, found {len(entries)}")
    if manifest.get("languages") != ["en", "ja", "zh"]:
        fail(errors, f"native edition languages are incorrect: {manifest.get('languages')}")
    if manifest.get("languageModes") != ["en", "ja", "zh", "all"]:
        fail(errors, f"native language modes are incorrect: {manifest.get('languageModes')}")
    if manifest.get("alignedBlocks") != 1164:
        fail(errors, f"expected 1164 aligned blocks, found {manifest.get('alignedBlocks')}")
    slugs = [entry.get("slug") for entry in entries]
    expected_slugs = ["note-on-the-conversations", "introduction"] + [
        f"ch{number:02d}" for number in range(1, 24)
    ]
    if slugs != expected_slugs:
        fail(errors, f"native reading sequence is incorrect: {slugs}")

    calculated_words = 0
    calculated_blocks = 0
    for index, entry in enumerate(entries):
        output_name = entry.get("output")
        source_name = entry.get("source")
        if not isinstance(output_name, str) or not isinstance(source_name, str):
            fail(errors, f"native entry {index + 1} lacks source or output path")
            continue
        output = site_root / output_name
        source = repo_root / source_name
        if not output.is_file():
            fail(errors, f"missing native reading: {output_name}")
            continue
        if not source.is_file():
            fail(errors, f"missing canonical source: {source_name}")
        elif sha256(source) != entry.get("sourceSha256"):
            fail(errors, f"stale native reading source checksum: {entry.get('slug')}")
        if sha256(output) != entry.get("outputSha256"):
            fail(errors, f"native reading output checksum mismatch: {entry.get('slug')}")

        content = output.read_text(encoding="utf-8")
        if '<div class="chapter-body">' not in content:
            fail(errors, f"native reading has no chapter body: {output_name}")
        if 'class="language-switcher"' not in content:
            fail(errors, f"native reading has no language selector: {output_name}")
        aligned_blocks = content.count('data-block-id="')
        if aligned_blocks != entry.get("alignedBlocks"):
            fail(
                errors,
                f"aligned block count mismatch in {output_name}: "
                f"{aligned_blocks} vs {entry.get('alignedBlocks')}",
            )
        else:
            calculated_blocks += aligned_blocks
        for language in ("en", "ja", "zh"):
            if f'data-language="{language}"' not in content:
                fail(errors, f"native reading lacks {language} content: {output_name}")
        if "<ruby>" not in content or "<rt>" not in content:
            fail(errors, f"native reading lacks semantic ruby annotations: {output_name}")
        if "<iframe" in content.lower():
            fail(errors, f"native reading embeds an iframe instead of HTML: {output_name}")
        if re.search(r"\\(?:ifdim|paperwidth|else|fi)\b", content):
            fail(errors, f"responsive TeX command leaked into HTML: {output_name}")

        words = entry.get("words")
        minimum = 900 if index >= 2 else 300
        if not isinstance(words, int) or words < minimum:
            fail(errors, f"native reading is unexpectedly short: {entry.get('slug')} ({words})")
        else:
            calculated_words += words

    if manifest.get("totalWords") != calculated_words:
        fail(
            errors,
            f"native word total does not reconcile: {manifest.get('totalWords')} vs {calculated_words}",
        )
    if calculated_words < 45000:
        fail(errors, f"native edition is too short to contain the complete book: {calculated_words} words")
    if calculated_blocks != 1164:
        fail(errors, f"native aligned block total does not reconcile: {calculated_blocks}")
    if sum(int(entry.get("figures", 0)) for entry in entries) != 2:
        fail(errors, "native edition must retain exactly two accepted documentary figures")

    records = search.get("records", [])
    if search.get("recordCount") != len(records) or len(records) < 220:
        fail(errors, f"native search index is incomplete: {len(records)} records")
    language_counts = {
        language: sum(record.get("language") == language for record in records)
        for language in ("en", "ja", "zh")
    }
    if language_counts["ja"] != 25 or language_counts["zh"] != 25:
        fail(errors, f"multilingual search coverage is incomplete: {language_counts}")
    for record in records:
        href = record.get("href")
        text = record.get("text")
        target = site_root / urlparse(href).path if isinstance(href, str) else None
        if target is None or not target.is_file():
            fail(errors, f"search record has invalid target: {href}")
        if not isinstance(text, str) or len(text) < 40:
            fail(errors, f"search record has insufficient text: {href}")

    book_page = (site_root / "book.html").read_text(encoding="utf-8")
    if "<iframe" in book_page.lower() or "COMPLETE NATIVE WEB EDITION" not in book_page:
        fail(errors, "book.html is not the complete native edition gateway")


def validate_multilingual_pdfs(site_root: Path, errors: list[str]) -> None:
    names = (
        "how-you-got-rich-en.pdf",
        "how-you-got-rich-en-pocket-1.2x.pdf",
        "how-you-got-rich-ja.pdf",
        "how-you-got-rich-ja-pocket-1.2x.pdf",
        "how-you-got-rich-zh.pdf",
        "how-you-got-rich-zh-pocket-1.2x.pdf",
        "how-you-got-rich-en-ja-zh.pdf",
        "how-you-got-rich-en-ja-zh-pocket-1.2x.pdf",
    )
    for name in names:
        path = site_root / "editions" / "languages" / name
        pages = pdf_pages(path) if path.is_file() else None
        if pages is None or pages < 100:
            fail(errors, f"multilingual PDF is missing or unexpectedly short: {name}")
            continue
        result = subprocess.run(
            ["qpdf", "--check", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            fail(errors, f"qpdf rejected multilingual PDF: {name}")


def validate_public_text(site_root: Path, errors: list[str]) -> None:
    for suffix in ("*.html", "*.json", "*.md"):
        for path in site_root.rglob(suffix):
            text = path.read_text(encoding="utf-8")
            for pattern in PUBLIC_LEAK_PATTERNS:
                if pattern.search(text):
                    fail(errors, f"reader-facing process leak in {path.relative_to(site_root)}: {pattern.pattern}")


def main() -> int:
    site_root = Path(sys.argv[1] if len(sys.argv) > 1 else "build/site").resolve()
    errors: list[str] = []
    if not site_root.is_dir():
        print(f"site root does not exist: {site_root}", file=sys.stderr)
        return 2

    present = {
        str(path.relative_to(site_root))
        for path in site_root.rglob("*")
        if path.is_file()
    }
    for missing in sorted(EXPECTED_FILES - present):
        fail(errors, f"missing required file: {missing}")

    validate_links(site_root, errors)
    validate_manifest(site_root, errors)
    validate_web_edition(site_root, errors)
    validate_multilingual_pdfs(site_root, errors)
    validate_public_text(site_root, errors)

    if errors:
        print("Website validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Website validation passed: 25 native readings, 5 parts, 23 chapters, "
        "1,164 EN-JA-ZH blocks, 10 PDF editions, checksums and local links intact."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
