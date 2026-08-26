#!/usr/bin/env python3
"""Shared deterministic renderers for the aligned multilingual book data."""

from __future__ import annotations

import html
import json
import re
import subprocess
from collections.abc import Iterable
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from multilingual_common import PANDOC_MARKDOWN, run_pandoc, tokens_for_language


ROOT = Path(__file__).resolve().parents[1]
START = "HYGR_BLOCK_START"
END = "HYGR_BLOCK_END"
MARKER_RE = re.compile(
    rf"<!--{START}:(?P<id>[A-Za-z0-9_-]+)-->(?P<body>.*?)"
    rf"<!--{END}:(?P=id)-->",
    re.DOTALL,
)
LATEX_MARKER_RE = re.compile(
    rf"% {START}:(?P<id>[A-Za-z0-9_-]+)\s*\n(?P<body>.*?)"
    rf"% {END}:(?P=id)(?:\s*\n|$)",
    re.DOTALL,
)
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def tex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in value)


def render_tokens_tex(tokens: Iterable[dict[str, str]], language: str) -> str:
    command = {"ja": "jpruby", "zh": "zhpy"}.get(language)
    rendered: list[str] = []
    for token in tokens:
        text = tex_escape(str(token.get("t", "")))
        reading = tex_escape(str(token.get("r", "")))
        if command and reading:
            rendered.append(rf"\{command}{{{text}}}{{{reading}}}")
        else:
            rendered.append(text)
    return "".join(rendered)


def render_text_tex(value: str, language: str, *, annotations: bool = True) -> str:
    if annotations and language in {"ja", "zh"}:
        return render_tokens_tex(tokens_for_language(value, language), language)
    return tex_escape(value)


def render_tokens_html(tokens: Iterable[dict[str, str]]) -> str:
    output: list[str] = []
    for token in tokens:
        text = html.escape(str(token.get("t", "")), quote=False)
        reading = str(token.get("r", ""))
        if reading:
            output.append(
                '<ruby><span class="ruby-base">'
                + text
                + '</span><rp>(</rp><rt>'
                + html.escape(reading, quote=False)
                + "</rt><rp>)</rp></ruby>"
            )
        else:
            output.append(text)
    return "".join(output)


class RubyHTMLParser(HTMLParser):
    """Re-emit a Pandoc fragment while adding ruby to visible CJK text."""

    SKIP_TAGS = {"code", "kbd", "math", "pre", "script", "style", "svg"}

    def __init__(self, language: str) -> None:
        super().__init__(convert_charrefs=True)
        self.language = language
        self.output: list[str] = []
        self.skip_stack: list[bool] = []

    @property
    def skipping(self) -> bool:
        return any(self.skip_stack)

    @staticmethod
    def attrs_text(attrs: list[tuple[str, str | None]]) -> str:
        pieces = []
        for name, value in attrs:
            if value is None:
                pieces.append(f" {name}")
            else:
                pieces.append(f' {name}="{html.escape(value, quote=True)}"')
        return "".join(pieces)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        skip = tag in self.SKIP_TAGS or "math" in classes
        self.skip_stack.append(skip)
        self.output.append(f"<{tag}{self.attrs_text(attrs)}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.output.append(f"<{tag}{self.attrs_text(attrs)}>")

    def handle_endtag(self, tag: str) -> None:
        self.output.append(f"</{tag}>")
        if self.skip_stack:
            self.skip_stack.pop()

    def handle_data(self, data: str) -> None:
        if self.skipping or not HAN_RE.search(data):
            self.output.append(html.escape(data, quote=False))
            return
        self.output.append(render_tokens_html(tokens_for_language(data, self.language)))

    def handle_comment(self, data: str) -> None:
        self.output.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.output.append(f"<!{decl}>")


def annotate_html(fragment: str, language: str) -> str:
    if language == "en":
        return fragment
    parser = RubyHTMLParser(language)
    parser.feed(fragment)
    parser.close()
    return "".join(parser.output)


def marked_markdown(blocks: Iterable[dict[str, Any]], language: str) -> str:
    pieces: list[str] = []
    for block in blocks:
        block_id = str(block["id"])
        markdown = str(block[language]["markdown"])
        pieces.append(
            f"<!--{START}:{block_id}-->\n\n{markdown}\n\n"
            f"<!--{END}:{block_id}-->"
        )
    return "\n\n".join(pieces) + "\n"


def split_html_blocks(rendered: str, expected: list[str]) -> dict[str, str]:
    result = {
        match.group("id"): match.group("body").strip()
        for match in MARKER_RE.finditer(rendered)
    }
    if list(result) != expected:
        raise ValueError(
            f"Pandoc HTML block alignment changed: expected {expected}, got {list(result)}"
        )
    return result


def render_html_blocks(entry: dict[str, Any], language: str) -> dict[str, str]:
    command = [
        "pandoc",
        f"--from={PANDOC_MARKDOWN}",
        "--to=html5",
        "--mathjax",
        "--wrap=none",
    ]
    completed = subprocess.run(
        command,
        input=marked_markdown(entry["blocks"], language),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"pandoc failed while rendering {entry['id']}.{language}: {detail}")
    expected = [str(block["id"]) for block in entry["blocks"]]
    blocks = split_html_blocks(completed.stdout, expected)
    for block_id, fragment in blocks.items():
        fragment = fragment.replace(' aria-hidden="true"', "")
        fragment = re.sub(
            r'src="([^"/]+\.(?:jpg|jpeg|png|webp))"',
            lambda match: (
                'src="../assets/figures/'
                + html.escape(Path(match.group(1)).name, quote=True)
                + '" loading="lazy" decoding="async"'
            ),
            fragment,
            flags=re.IGNORECASE,
        )
        if language != "en":
            fragment = re.sub(r"(<h[1-6])\s+id=\"[^\"]+\"", r"\1", fragment)
        blocks[block_id] = annotate_html(fragment, language)
    return blocks


def marked_document(entry: dict[str, Any], language: str) -> dict[str, Any]:
    return json.loads(run_pandoc(marked_markdown(entry["blocks"], language), PANDOC_MARKDOWN, "json"))


def ruby_inline_nodes(text: str, language: str) -> list[dict[str, Any]]:
    command = {"ja": "jpruby", "zh": "zhpy"}.get(language)
    if not command:
        return [{"t": "Str", "c": text}]
    output: list[dict[str, Any]] = []
    for token in tokens_for_language(text, language):
        token_text = str(token.get("t", ""))
        reading = str(token.get("r", ""))
        if reading:
            output.append(
                {
                    "t": "RawInline",
                    "c": [
                        "latex",
                        rf"\{command}{{{tex_escape(token_text)}}}{{{tex_escape(reading)}}}",
                    ],
                }
            )
        elif token_text:
            output.append({"t": "Str", "c": token_text})
    return output


def transform_ast(value: Any, language: str, *, annotate: bool = True) -> Any:
    if isinstance(value, list):
        output: list[Any] = []
        for item in value:
            transformed = transform_ast(item, language, annotate=annotate)
            if isinstance(transformed, _InlineExpansion):
                output.extend(transformed.nodes)
            else:
                output.append(transformed)
        return output
    if not isinstance(value, dict):
        return value

    node = deepcopy(value)
    node_type = node.get("t")
    content = node.get("c")
    if node_type == "Str" and annotate:
        return _InlineExpansion(ruby_inline_nodes(str(content), language))
    if node_type in {"Code", "CodeBlock", "Math", "RawInline"}:
        return node
    if node_type == "RawBlock" and isinstance(content, list):
        raw_format, raw_value = content
        marker = re.fullmatch(
            rf"<!--(?P<edge>{START}|{END}):(?P<id>[A-Za-z0-9_-]+)-->",
            str(raw_value).strip(),
        )
        if marker:
            node["c"] = ["latex", f"% {marker.group('edge')}:{marker.group('id')}\n"]
        return node
    if node_type == "Header" and isinstance(content, list):
        level, attributes, inlines = content
        node["c"] = [max(1, int(level) - 1), attributes, transform_ast(inlines, language, annotate=False)]
        return node
    if "c" in node:
        node["c"] = transform_ast(content, language, annotate=annotate)
    return node


class _InlineExpansion:
    def __init__(self, nodes: list[dict[str, Any]]) -> None:
        self.nodes = nodes


def split_latex_blocks(rendered: str, expected: list[str]) -> dict[str, str]:
    result = {
        match.group("id"): match.group("body").strip()
        for match in LATEX_MARKER_RE.finditer(rendered)
    }
    if list(result) != expected:
        raise ValueError(
            f"Pandoc LaTeX block alignment changed: expected {expected}, got {list(result)}"
        )
    return result


def render_latex_blocks(entry: dict[str, Any], language: str) -> dict[str, str]:
    document = marked_document(entry, language)
    transformed = deepcopy(document)
    transformed["blocks"] = transform_ast(document["blocks"], language)
    rendered = run_pandoc(json.dumps(transformed, ensure_ascii=False), "json", "latex")
    rendered = rendered.replace(
        r"\begin{longtable}[]{@{}ll@{}}",
        r"\begin{longtable}[]{@{}p{0.27\linewidth}p{0.68\linewidth}@{}}",
    )
    expected = [str(block["id"]) for block in entry["blocks"]]
    return split_latex_blocks(rendered, expected)
