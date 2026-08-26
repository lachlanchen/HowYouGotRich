#!/usr/bin/env python3
"""Validate aligned language data, readings, structure, and source fidelity."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import jsonschema

from multilingual_common import (
    ENTRY_ROOT,
    MANIFEST_PATH,
    MULTILINGUAL_ROOT,
    build_entry_specs,
    load_book,
    load_entry,
    markdown_block,
    plain_text_from_block,
    protected_signature,
    sha256_text,
    structure_signature,
    tokens_for_language,
)


KANA_RE = re.compile(r"[\u3040-\u30ff]")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
LATIN_RE = re.compile(r"[A-Za-z]")
PROCESS_LEAK_RE = re.compile(
    r"(?i)(?:codex|chatgpt|large language model|prompt tool|source file path|"
    r"transcript-processing pipeline|as an ai)"
)


def validate_annotation_tokens(
    tokens: list[dict[str, str]], language: str, location: str, errors: list[str]
) -> None:
    for index, token in enumerate(tokens):
        text = str(token.get("t", ""))
        reading = str(token.get("r", ""))
        if not text:
            errors.append(f"{location}.tokens[{index}]: empty token")
        if reading and not HAN_RE.search(text):
            errors.append(f"{location}.tokens[{index}]: reading on non-Han token {text!r}")
        if language == "ja" and reading and not re.fullmatch(r"[\u3040-\u309fー・\s]+", reading):
            errors.append(f"{location}.tokens[{index}]: invalid furigana {reading!r}")
        if language == "zh" and reading and HAN_RE.search(reading):
            errors.append(f"{location}.tokens[{index}]: pinyin contains Han text {reading!r}")


def validate_target(
    source: dict[str, Any], language: str, require_complete: bool, errors: list[str]
) -> bool:
    location = f"{source['id']}.{language}"
    target = source[language]
    status = target.get("status")
    if status == "missing":
        if require_complete:
            errors.append(f"{location}: missing translation")
        if target.get("markdown") or target.get("tokens"):
            errors.append(f"{location}: missing block carries content")
        return False
    if require_complete and status != "reviewed":
        errors.append(f"{location}: expected reviewed status, found {status!r}")
    markdown = str(target.get("markdown", ""))
    if not markdown.strip():
        errors.append(f"{location}: empty Markdown")
        return False
    try:
        target_block = markdown_block(markdown)
    except (RuntimeError, ValueError) as error:
        errors.append(f"{location}: {error}")
        return False

    structure = structure_signature(target_block)
    if structure != source["structure"]:
        errors.append(
            f"{location}: structure changed from {source['structure']} to {structure}"
        )
    protected = protected_signature(target_block)
    if protected != source["protected"]:
        errors.append(f"{location}: protected math/link/image/code payload changed")

    text = plain_text_from_block(target_block)
    if len(text) >= 30:
        if language == "ja" and not KANA_RE.search(text):
            errors.append(f"{location}: Japanese prose has no kana")
        if language == "zh" and not HAN_RE.search(text):
            errors.append(f"{location}: Chinese prose has no Han text")
        latin = len(LATIN_RE.findall(text))
        visible = len(re.sub(r"\s+", "", text))
        if visible and latin / visible > 0.58:
            errors.append(f"{location}: target appears substantially untranslated")
    if PROCESS_LEAK_RE.search(text):
        errors.append(f"{location}: reader-facing process language detected")

    tokens = target.get("tokens") or []
    expected_tokens = tokens_for_language(text, language)
    if tokens != expected_tokens:
        errors.append(f"{location}: stored reading tokens do not match target prose")
    if "".join(str(token.get("t", "")) for token in tokens) != text:
        errors.append(f"{location}: token text does not reconstruct target prose")
    validate_annotation_tokens(tokens, language, location, errors)
    return status == "reviewed" and not any(error.startswith(location) for error in errors)


def validate_entry(
    entry: dict[str, Any], schema: dict[str, Any], require_complete: bool
) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    counts = {"blocks": 0, "ja": 0, "zh": 0}
    try:
        jsonschema.validate(entry, schema)
    except jsonschema.ValidationError as error:
        errors.append(f"{entry.get('id', '<unknown>')}: schema: {error.message}")
        return errors, counts

    if entry["block_count"] != len(entry["blocks"]):
        errors.append(f"{entry['id']}: block_count does not match blocks")
    ids = [block["id"] for block in entry["blocks"]]
    if len(ids) != len(set(ids)):
        errors.append(f"{entry['id']}: duplicate block ids")

    metadata = entry["metadata"]
    for language in ("ja", "zh"):
        for field in ("title", "question"):
            value = str(metadata[field].get(language, "")).strip()
            if require_complete and not value:
                errors.append(f"{entry['id']}.metadata.{field}.{language}: missing")

    for block in entry["blocks"]:
        counts["blocks"] += 1
        if block["source_sha256"] != sha256_text(block["en"]["markdown"]):
            errors.append(f"{block['id']}: English Markdown hash mismatch")
        try:
            source_block = markdown_block(block["en"]["markdown"])
        except (RuntimeError, ValueError) as error:
            errors.append(f"{block['id']}.en: {error}")
            continue
        if structure_signature(source_block) != block["structure"]:
            errors.append(f"{block['id']}.en: recorded structure mismatch")
        if protected_signature(source_block) != block["protected"]:
            errors.append(f"{block['id']}.en: recorded protected payload mismatch")
        source_text = plain_text_from_block(source_block)
        if block["en"]["tokens"] != tokens_for_language(source_text, "en"):
            errors.append(f"{block['id']}.en: stored source tokens mismatch")
        for language in ("ja", "zh"):
            before = len(errors)
            complete = validate_target(block, language, require_complete, errors)
            if complete and len(errors) == before:
                counts[language] += 1
    return errors, counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--entry", action="append", default=[])
    args = parser.parse_args()

    schema = json.loads((MULTILINGUAL_ROOT / "schema.json").read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    selected = set(args.entry)
    manifest_entries = [
        item for item in manifest["entries"] if not selected or item["id"] in selected
    ]
    if selected and selected != {item["id"] for item in manifest_entries}:
        missing = sorted(selected - {item["id"] for item in manifest_entries})
        print(f"Unknown entries: {', '.join(missing)}", file=sys.stderr)
        return 2

    specs = {spec.slug: spec for spec in build_entry_specs(load_book())}
    all_errors: list[str] = []
    totals = {"entries": 0, "blocks": 0, "ja": 0, "zh": 0}
    for item in manifest_entries:
        entry = load_entry(item["id"])
        spec = specs[item["id"]]
        if entry["source_sha256"] != sha256_text(spec.source_text):
            all_errors.append(f"{entry['id']}: accepted TeX source hash changed")
        errors, counts = validate_entry(entry, schema, args.require_complete)
        all_errors.extend(errors)
        totals["entries"] += 1
        for key in ("blocks", "ja", "zh"):
            totals[key] += counts[key]

    if not selected:
        if totals["entries"] != manifest["entry_count"]:
            all_errors.append("manifest entry_count mismatch")
        if totals["blocks"] != manifest["block_count"]:
            all_errors.append("manifest block_count mismatch")
        if totals["ja"] != manifest["reviewed_blocks"]["ja"]:
            all_errors.append("manifest Japanese reviewed count mismatch")
        if totals["zh"] != manifest["reviewed_blocks"]["zh"]:
            all_errors.append("manifest Chinese reviewed count mismatch")

    if all_errors:
        for error in all_errors[:200]:
            print(error, file=sys.stderr)
        if len(all_errors) > 200:
            print(f"... {len(all_errors) - 200} more errors", file=sys.stderr)
        return 1
    print(
        f"Validated {totals['entries']} readings, {totals['blocks']} blocks; "
        f"reviewed JA {totals['ja']}, ZH {totals['zh']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
