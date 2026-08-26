#!/usr/bin/env python3
"""Create or refresh the immutable English spine for multilingual editions."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from multilingual_common import (
    ENTRY_ROOT,
    MANIFEST_PATH,
    ROOT,
    block_to_markdown,
    build_entry_specs,
    latex_document,
    load_book,
    plain_text_from_block,
    protected_signature,
    sha256_text,
    structure_signature,
    tokens_for_language,
    write_json,
)


BOOK_TITLES = {
    "en": "How You Got Rich",
    "ja": "あなたはいかにして富を築いたか",
    "zh": "你是如何致富的",
}
BOOK_SUBTITLES = {
    "en": "From Abundance to Fulfillment and Contentment",
    "ja": "豊かさから充実、そして「足るを知る」へ",
    "zh": "从富足到满足与知足",
}
PART_TITLES = {
    "I": {"ja": "お金は何のためにあるのか", "zh": "金钱为何存在"},
    "II": {"ja": "価値あるものをつくる", "zh": "创造有价值之物"},
    "III": {"ja": "仕組みを所有する", "zh": "拥有运转的系统"},
    "IV": {"ja": "資本・リスク・時間", "zh": "资本、风险与时间"},
    "V": {"ja": "自由と「足る」", "zh": "自由与知足"},
}


def source_commit() -> str:
    return subprocess.check_output(
        [
            "git",
            "log",
            "-1",
            "--format=%H",
            "--",
            "source/book/manuscript",
            "source/book/how-you-got-rich.tex",
            "docs/data/book.json",
        ],
        cwd=ROOT,
        text=True,
    ).strip()


def source_commit_time(commit: str) -> str:
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", commit], cwd=ROOT, text=True
    ).strip()


def load_existing(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def preserve_translation(
    existing: dict[str, Any], source_sha256: str, language: str
) -> dict[str, Any]:
    if existing.get("source_sha256") != source_sha256:
        return {"status": "missing", "markdown": "", "tokens": []}
    value = existing.get(language)
    if not isinstance(value, dict):
        return {"status": "missing", "markdown": "", "tokens": []}
    return value


def prepare_entry(spec: Any) -> dict[str, Any]:
    document = latex_document(spec.source_text)
    source_blocks = list(document.get("blocks") or [])
    if source_blocks and source_blocks[0].get("t") == "Header":
        content = source_blocks[0].get("c") or []
        if content and int(content[0]) == 1:
            source_blocks = source_blocks[1:]

    output_path = ENTRY_ROOT / f"{spec.slug}.json"
    existing = load_existing(output_path)
    existing_blocks = {
        block.get("id"): block
        for block in existing.get("blocks", [])
        if isinstance(block, dict) and block.get("id")
    }

    blocks = []
    for index, source_block in enumerate(source_blocks, 1):
        block_id = f"{spec.slug}-b{index:04d}"
        markdown = block_to_markdown(
            source_block,
            document.get("meta") or {},
            document["pandoc-api-version"],
        )
        source_sha256 = sha256_text(markdown)
        source_text = plain_text_from_block(source_block)
        previous = existing_blocks.get(block_id, {})
        blocks.append(
            {
                "id": block_id,
                "kind": source_block.get("t"),
                "source_sha256": source_sha256,
                "structure": structure_signature(source_block),
                "protected": protected_signature(source_block),
                "en": {
                    "status": "source",
                    "markdown": markdown,
                    "tokens": tokens_for_language(source_text, "en"),
                },
                "ja": preserve_translation(previous, source_sha256, "ja"),
                "zh": preserve_translation(previous, source_sha256, "zh"),
            }
        )

    metadata_existing = existing.get("metadata") or {}
    title_existing = metadata_existing.get("title") or {}
    question_existing = metadata_existing.get("question") or {}
    metadata_source_hash = sha256_text(spec.title + "\n" + spec.question)
    metadata_is_current = metadata_existing.get("source_sha256") == metadata_source_hash
    title = {
        "en": spec.title,
        "ja": title_existing.get("ja", "") if metadata_is_current else "",
        "zh": title_existing.get("zh", "") if metadata_is_current else "",
    }
    question = {
        "en": spec.question,
        "ja": question_existing.get("ja", "") if metadata_is_current else "",
        "zh": question_existing.get("zh", "") if metadata_is_current else "",
    }
    return {
        "schema_version": 1,
        "id": spec.slug,
        "kind": spec.kind,
        "number": spec.number,
        "part": {
            "number": spec.part_number,
            "title_en": spec.part_title,
        }
        if spec.part_number
        else None,
        "source_path": str(spec.source_path.relative_to(ROOT)),
        "source_sha256": sha256_text(spec.source_text),
        "metadata": {
            "source_sha256": metadata_source_hash,
            "title": title,
            "question": question,
        },
        "block_count": len(blocks),
        "blocks": blocks,
    }


def translation_counts(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"source": 0, "ja": 0, "zh": 0}
    for entry in entries:
        for block in entry["blocks"]:
            counts["source"] += 1
            for language in ("ja", "zh"):
                if block[language].get("status") == "reviewed":
                    counts[language] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if preparation changes tracked data")
    args = parser.parse_args()

    book = load_book()
    specs = build_entry_specs(book)
    entries = [prepare_entry(spec) for spec in specs]
    counts = translation_counts(entries)
    accepted_source_commit = source_commit()
    manifest = {
        "schema_version": 1,
        "book_version": book["version"],
        "source_commit": accepted_source_commit,
        "source_commit_time": source_commit_time(accepted_source_commit),
        "title": BOOK_TITLES,
        "subtitle": BOOK_SUBTITLES,
        "author": "LazyingArt · LazyLearn",
        "languages": ["en", "ja", "zh"],
        "parts": [
            {
                "number": part["number"],
                "title": {
                    "en": part["title"],
                    "ja": PART_TITLES[part["number"]]["ja"],
                    "zh": PART_TITLES[part["number"]]["zh"],
                },
            }
            for part in book["parts"]
        ],
        "entry_count": len(entries),
        "block_count": counts["source"],
        "reviewed_blocks": {"ja": counts["ja"], "zh": counts["zh"]},
        "entries": [
            {
                "id": entry["id"],
                "kind": entry["kind"],
                "number": entry["number"],
                "part": entry["part"],
                "path": f"entries/{entry['id']}.json",
                "source_sha256": entry["source_sha256"],
                "block_count": entry["block_count"],
            }
            for entry in entries
        ],
    }

    snapshots: dict[Path, str] = {}
    for entry in entries:
        path = ENTRY_ROOT / f"{entry['id']}.json"
        snapshots[path] = json.dumps(entry, ensure_ascii=False, indent=2) + "\n"
    snapshots[MANIFEST_PATH] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    changed = [
        path
        for path, content in snapshots.items()
        if not path.is_file() or path.read_text(encoding="utf-8") != content
    ]
    if args.check and changed:
        for path in changed:
            print(path.relative_to(ROOT))
        return 1
    for path, content in snapshots.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    print(
        f"Prepared {len(entries)} readings and {counts['source']} aligned blocks; "
        f"reviewed JA {counts['ja']}, ZH {counts['zh']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
