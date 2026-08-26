#!/usr/bin/env python3
"""Shared primitives for the aligned English-Japanese-Chinese editions."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import jieba
import pykakasi
import unidic_lite
from fugashi import GenericTagger
from pypinyin import Style, pinyin


ROOT = Path(__file__).resolve().parents[1]
BOOK_ROOT = ROOT / "source" / "book"
MANUSCRIPT = BOOK_ROOT / "manuscript"
BOOK_DATA_PATH = ROOT / "docs" / "data" / "book.json"
MULTILINGUAL_ROOT = ROOT / "multilingual"
ENTRY_ROOT = MULTILINGUAL_ROOT / "entries"
MANIFEST_PATH = MULTILINGUAL_ROOT / "manifest.json"
PANDOC_MARKDOWN = "markdown+tex_math_dollars+raw_tex+raw_html"

HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
EN_TOKEN_RE = re.compile(
    r"\s+|[A-Za-z]+(?:['’-][A-Za-z]+)*|\d+(?:[.,]\d+)*|[^\sA-Za-z0-9]+"
)
KAKASI = pykakasi.kakasi()
MECAB = GenericTagger(f"-r /dev/null -d {unidic_lite.DICDIR}")
jieba.setLogLevel(logging.WARNING)


@dataclass(frozen=True)
class EntrySpec:
    slug: str
    kind: str
    title: str
    question: str
    source_path: Path
    source_text: str
    number: int | None = None
    part_number: str | None = None
    part_title: str | None = None


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def run_pandoc(source: str, source_format: str, target_format: str) -> str:
    command = [
        "pandoc",
        f"--from={source_format}",
        f"--to={target_format}",
        "--wrap=none",
    ]
    completed = subprocess.run(
        command,
        input=source,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"pandoc failed ({source_format} -> {target_format}): {detail}")
    return completed.stdout


def choose_responsive_tex(source: str) -> str:
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


def latex_document(source: str) -> dict[str, Any]:
    return json.loads(run_pandoc(prepare_tex(source), "latex", "json"))


def markdown_document(source: str) -> dict[str, Any]:
    return json.loads(run_pandoc(source, PANDOC_MARKDOWN, "json"))


def block_to_markdown(
    block: dict[str, Any], meta: dict[str, Any], api_version: list[int]
) -> str:
    document = {"pandoc-api-version": api_version, "meta": meta, "blocks": [block]}
    return run_pandoc(
        json.dumps(document, ensure_ascii=False), "json", PANDOC_MARKDOWN
    ).strip()


def metadata_inline_text(value: Any) -> str:
    if isinstance(value, str):
        return ""
    if isinstance(value, list):
        return "".join(metadata_inline_text(item) for item in value)
    if not isinstance(value, dict):
        return ""
    node_type = value.get("t")
    content = value.get("c")
    if node_type == "Str":
        return str(content)
    if node_type in {"Space", "SoftBreak", "LineBreak"}:
        return " "
    if node_type == "Code" and isinstance(content, list):
        return str(content[-1])
    if node_type == "Header" and isinstance(content, list):
        return metadata_inline_text(content[2])
    if node_type == "Div" and isinstance(content, list):
        return metadata_inline_text(content[1])
    if node_type == "Math" and isinstance(content, list):
        return ""
    if node_type in {"Image", "Link"} and isinstance(content, list):
        return metadata_inline_text(content[1])
    return metadata_inline_text(content)


def plain_text_from_block(block: dict[str, Any]) -> str:
    return re.sub(r"\s+", " ", metadata_inline_text(block)).strip()


def plain_text_from_markdown(markdown: str) -> str:
    document = markdown_document(markdown)
    return re.sub(r"\s+", " ", metadata_inline_text(document["blocks"])).strip()


def walk_nodes(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        yield from walk_nodes(value.get("c"))
    elif isinstance(value, list):
        for item in value:
            yield from walk_nodes(item)


def protected_signature(block: dict[str, Any]) -> list[dict[str, str]]:
    protected: list[dict[str, str]] = []
    for node in walk_nodes(block):
        node_type = node.get("t")
        content = node.get("c")
        if node_type == "Math" and isinstance(content, list):
            protected.append({"type": "math", "value": str(content[-1])})
        elif node_type == "Image" and isinstance(content, list):
            target = content[-1]
            if isinstance(target, list):
                protected.append({"type": "image", "value": str(target[0])})
        elif node_type == "Link" and isinstance(content, list):
            target = content[-1]
            if isinstance(target, list):
                protected.append({"type": "link", "value": str(target[0])})
        elif node_type == "Code" and isinstance(content, list):
            protected.append({"type": "code", "value": str(content[-1])})
    return protected


def protected_equivalent(
    source: list[dict[str, str]], target: list[dict[str, str]]
) -> bool:
    """Require the same protected payloads while allowing grammatical reordering."""

    def counts(values: list[dict[str, str]]) -> Counter[tuple[str, str]]:
        return Counter((str(item.get("type", "")), str(item.get("value", ""))) for item in values)

    return counts(source) == counts(target)


def structure_signature(block: dict[str, Any]) -> dict[str, Any]:
    node_type = str(block.get("t"))
    signature: dict[str, Any] = {"type": node_type}
    content = block.get("c")
    if node_type == "Header" and isinstance(content, list):
        signature["level"] = int(content[0])
    elif node_type in {"BulletList", "OrderedList"} and isinstance(content, list):
        items = content if node_type == "BulletList" else content[-1]
        signature["items"] = len(items)
    elif node_type == "DefinitionList" and isinstance(content, list):
        signature["items"] = len(content)
    elif node_type == "BlockQuote" and isinstance(content, list):
        signature["blocks"] = len(content)
    return signature


def markdown_block(markdown: str) -> dict[str, Any]:
    blocks = markdown_document(markdown).get("blocks") or []
    if len(blocks) != 1:
        raise ValueError(f"expected one top-level Markdown block, found {len(blocks)}")
    return blocks[0]


def tokenize_en(text: str) -> list[dict[str, str]]:
    return [{"t": match.group(0)} for match in EN_TOKEN_RE.finditer(text)]


def katakana_to_hiragana(text: str) -> str:
    result = []
    for character in str(text):
        codepoint = ord(character)
        if 0x30A1 <= codepoint <= 0x30FA:
            result.append(chr(codepoint - 0x60))
        else:
            result.append(character)
    return "".join(result)


def japanese_reading(word: Any) -> str:
    feature = word.feature
    for index in (17, 9, 6):
        if len(feature) > index and feature[index] not in {"", "*"}:
            return katakana_to_hiragana(str(feature[index]))
    converted = "".join(str(item.get("hira") or "") for item in KAKASI.convert(word.surface))
    return katakana_to_hiragana(converted)


def tokenize_ja(text: str) -> list[dict[str, str]]:
    tokens: list[dict[str, str]] = []
    for run in re.findall(r"\s+|\S+", str(text)):
        if run.isspace():
            tokens.append({"t": run})
            continue
        for word in MECAB(run):
            surface = str(word.surface)
            token = {"t": surface}
            if HAN_RE.search(surface):
                reading = japanese_reading(word)
                if reading:
                    token["r"] = reading
            tokens.append(token)
    return tokens


def tokenize_zh(text: str) -> list[dict[str, str]]:
    tokens: list[dict[str, str]] = []
    for surface in jieba.lcut(str(text), cut_all=False):
        token = {"t": surface}
        if HAN_RE.search(surface):
            readings = [
                values[0]
                for values in pinyin(surface, style=Style.TONE, heteronym=False, errors=lambda value: [value])
            ]
            if readings:
                token["r"] = " ".join(readings)
        tokens.append(token)
    return tokens


def tokens_for_language(text: str, language: str) -> list[dict[str, str]]:
    if language == "en":
        return tokenize_en(text)
    if language == "ja":
        return tokenize_ja(text)
    if language == "zh":
        return tokenize_zh(text)
    raise ValueError(f"unsupported language: {language}")


def build_entry_specs(book: dict[str, Any]) -> list[EntrySpec]:
    frontmatter_path = MANUSCRIPT / "frontmatter.tex"
    frontmatter = frontmatter_path.read_text(encoding="utf-8")
    marker = r"\chapter*{A Note on the Conversations}"
    marker_index = frontmatter.find(marker)
    if marker_index < 0:
        raise ValueError("could not locate the conversations note in frontmatter.tex")

    specs = [
        EntrySpec(
            slug="note-on-the-conversations",
            kind="preface",
            title=book["preface"]["title"],
            question=book["preface"]["question"],
            source_path=frontmatter_path,
            source_text=frontmatter[marker_index:],
        ),
        EntrySpec(
            slug="introduction",
            kind="introduction",
            title=book["introduction"]["title"],
            question=book["introduction"]["question"],
            source_path=MANUSCRIPT / "introduction.tex",
            source_text=(MANUSCRIPT / "introduction.tex").read_text(encoding="utf-8"),
        ),
    ]
    for part in book["parts"]:
        for chapter in part["chapters"]:
            number = int(chapter["number"])
            source_path = MANUSCRIPT / "chapters" / f"ch{number:02d}.tex"
            specs.append(
                EntrySpec(
                    slug=f"ch{number:02d}",
                    kind="chapter",
                    title=chapter["title"],
                    question=chapter["question"],
                    source_path=source_path,
                    source_text=source_path.read_text(encoding="utf-8"),
                    number=number,
                    part_number=part["number"],
                    part_title=part["title"],
                )
            )
    return specs


def load_book() -> dict[str, Any]:
    return json.loads(BOOK_DATA_PATH.read_text(encoding="utf-8"))


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_entry(slug: str) -> dict[str, Any]:
    return json.loads((ENTRY_ROOT / f"{slug}.json").read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
