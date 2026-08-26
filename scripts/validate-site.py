#!/usr/bin/env python3
"""Validate the assembled static book website using only the standard library."""

from __future__ import annotations

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
    "styles.css",
    "app.js",
    "favicon.svg",
    "site.webmanifest",
    "data/book.json",
    "assets/cover-page-1.png",
    "editions/how-you-got-rich.pdf",
    "editions/how-you-got-rich-pocket-1.2x.pdf",
    "editions/v2/how-you-got-rich-v2.pdf",
    "editions/v2/how-you-got-rich-v2-pocket-1.2x.pdf",
    "editions/v3/how-you-got-rich-v3.pdf",
    "editions/v3/how-you-got-rich-v3-pocket-1.2x.pdf",
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
    for html_path in sorted(site_root.glob("*.html")):
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
                fail(errors, f"{html_path.name}: link escapes site root: {raw_link}")
                continue
            if not target.exists():
                fail(errors, f"{html_path.name}: missing local target: {raw_link}")


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
    validate_public_text(site_root, errors)

    if errors:
        print("Website validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Website validation passed: 5 parts, 23 chapters, 2 editions, local links intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
