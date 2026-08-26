#!/usr/bin/env python3
"""Translate aligned readings with resumable, validated Codex calls."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from multilingual_common import (
    ENTRY_ROOT,
    MANIFEST_PATH,
    MULTILINGUAL_ROOT,
    ROOT,
    load_entry,
    load_manifest,
    markdown_block,
    plain_text_from_block,
    protected_signature,
    structure_signature,
    tokens_for_language,
    write_json,
)


RUNTIME_ROOT = MULTILINGUAL_ROOT / "runtime"
RESPONSE_SCHEMA = MULTILINGUAL_ROOT / "translation-response.schema.json"
GUIDELINES = MULTILINGUAL_ROOT / "translation-guidelines.md"
KANA_RE = re.compile(r"[\u3040-\u30ff]")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
USAGE_LIMIT_RE = re.compile(
    r"(?i)(?:usage limit|rate limit|purchase more credits|try again at|quota exceeded)"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_records(entry: dict[str, Any], force: bool) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    metadata = entry["metadata"]
    metadata_complete = all(
        str(metadata[field].get(language, "")).strip()
        for field in ("title", "question")
        for language in ("ja", "zh")
    )
    if force or not metadata_complete:
        records.extend(
            [
                {
                    "id": "__title__",
                    "kind": "metadata",
                    "en": metadata["title"]["en"],
                },
                {
                    "id": "__question__",
                    "kind": "metadata",
                    "en": metadata["question"]["en"],
                },
            ]
        )
    for block in entry["blocks"]:
        complete = all(block[language].get("status") == "reviewed" for language in ("ja", "zh"))
        if complete and not force:
            continue
        records.append(
            {
                "id": block["id"],
                "kind": block["kind"],
                "structure": block["structure"],
                "protected": block["protected"],
                "en": block["en"]["markdown"],
            }
        )
    return records


def build_prompt(entry: dict[str, Any], records: list[dict[str, Any]], repair: list[str]) -> str:
    contract = GUIDELINES.read_text(encoding="utf-8")
    repair_text = ""
    if repair:
        repair_text = (
            "\nThe previous attempt failed these deterministic checks. Produce a fresh, "
            "complete response that fixes every issue:\n- "
            + "\n- ".join(repair[:80])
            + "\n"
        )
    payload = {
        "book": "How You Got Rich",
        "entry_id": entry["id"],
        "entry_kind": entry["kind"],
        "entry_title": entry["metadata"]["title"]["en"],
        "entry_question": entry["metadata"]["question"]["en"],
        "records": records,
    }
    return f"""Translate one complete reading of a serious nonfiction book.

{contract}

Before returning, silently perform a second fidelity pass: compare every target
against its English record, restore any missing qualification or attribution,
and verify that protected payloads and list shape are unchanged. Do not edit
files or use repository tools. Return only JSON conforming to the supplied
schema. The `translations` array must contain every requested ID exactly once
and no unrequested IDs.
{repair_text}
INPUT JSON:
{json.dumps(payload, ensure_ascii=False, indent=2)}
"""


def run_codex(
    entry_id: str,
    prompt: str,
    model: str,
    reasoning: str,
    attempt: int,
) -> tuple[dict[str, Any] | None, str]:
    runtime = RUNTIME_ROOT / entry_id
    runtime.mkdir(parents=True, exist_ok=True)
    output_path = runtime / f"attempt-{attempt:02d}.json"
    log_path = runtime / f"attempt-{attempt:02d}.log"
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--model",
        model,
        "--config",
        f'model_reasoning_effort="{reasoning}"',
        "--config",
        'approval_policy="never"',
        "--sandbox",
        "danger-full-access",
        "--cd",
        str(ROOT),
        "--output-schema",
        str(RESPONSE_SCHEMA),
        "--output-last-message",
        str(output_path),
        "-",
    ]
    completed = subprocess.run(
        command,
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
    )
    log_path.write_text(
        completed.stdout + "\n--- STDERR ---\n" + completed.stderr,
        encoding="utf-8",
    )
    combined = completed.stdout + "\n" + completed.stderr
    if completed.returncode:
        return None, combined.strip() or f"codex exited {completed.returncode}"
    if not output_path.is_file():
        return None, "codex did not write the structured response"
    try:
        return json.loads(output_path.read_text(encoding="utf-8")), combined
    except json.JSONDecodeError as error:
        return None, f"invalid response JSON: {error}"


def validate_metadata(value: str, language: str, location: str, errors: list[str]) -> None:
    text = value.strip()
    if not text:
        errors.append(f"{location}: empty translation")
    elif language == "ja" and not (KANA_RE.search(text) or HAN_RE.search(text)):
        errors.append(f"{location}: no Japanese text")
    elif language == "zh" and not HAN_RE.search(text):
        errors.append(f"{location}: no Chinese text")


def validate_response(
    entry: dict[str, Any], records: list[dict[str, Any]], response: dict[str, Any]
) -> tuple[list[str], dict[str, dict[str, str]]]:
    errors: list[str] = []
    translations = response.get("translations")
    if not isinstance(translations, list):
        return ["response.translations is not an array"], {}
    expected = [record["id"] for record in records]
    received = [str(item.get("id", "")) for item in translations if isinstance(item, dict)]
    if len(received) != len(set(received)):
        errors.append("response contains duplicate IDs")
    if set(received) != set(expected):
        missing = sorted(set(expected) - set(received))
        extra = sorted(set(received) - set(expected))
        errors.append(f"ID mismatch; missing={missing}, extra={extra}")
    indexed = {
        str(item.get("id")): item
        for item in translations
        if isinstance(item, dict) and item.get("id")
    }
    source_by_id = {block["id"]: block for block in entry["blocks"]}
    accepted: dict[str, dict[str, str]] = {}
    for record in records:
        record_id = record["id"]
        candidate = indexed.get(record_id)
        if candidate is None:
            continue
        accepted[record_id] = {
            "ja": str(candidate.get("ja", "")).strip(),
            "zh": str(candidate.get("zh", "")).strip(),
        }
        if record_id.startswith("__"):
            for language in ("ja", "zh"):
                validate_metadata(
                    accepted[record_id][language],
                    language,
                    f"{record_id}.{language}",
                    errors,
                )
            continue
        source = source_by_id[record_id]
        source_words = max(1, len(re.findall(r"\b[\w'-]+\b", source["en"]["markdown"])))
        for language in ("ja", "zh"):
            location = f"{record_id}.{language}"
            markdown = accepted[record_id][language]
            if not markdown:
                errors.append(f"{location}: empty translation")
                continue
            try:
                block = markdown_block(markdown)
            except (RuntimeError, ValueError) as error:
                errors.append(f"{location}: {error}")
                continue
            if structure_signature(block) != source["structure"]:
                errors.append(f"{location}: Markdown structure changed")
            if protected_signature(block) != source["protected"]:
                errors.append(f"{location}: protected math/link/image/code changed")
            text = plain_text_from_block(block)
            visible = len(re.sub(r"\s+", "", text))
            minimum = max(1, int(source_words * (0.45 if language == "zh" else 0.7)))
            if visible < minimum:
                errors.append(
                    f"{location}: suspiciously short target ({visible} chars for {source_words} source words)"
                )
            if len(text) >= 30 and language == "ja" and not KANA_RE.search(text):
                errors.append(f"{location}: Japanese prose has no kana")
            if len(text) >= 30 and language == "zh" and not HAN_RE.search(text):
                errors.append(f"{location}: Chinese prose has no Han text")
    return errors, accepted


def apply_translations(
    entry: dict[str, Any], accepted: dict[str, dict[str, str]], model: str, reasoning: str
) -> None:
    metadata = entry["metadata"]
    if "__title__" in accepted:
        for language in ("ja", "zh"):
            metadata["title"][language] = accepted["__title__"][language]
    if "__question__" in accepted:
        for language in ("ja", "zh"):
            metadata["question"][language] = accepted["__question__"][language]

    for block in entry["blocks"]:
        translated = accepted.get(block["id"])
        if translated is None:
            continue
        for language in ("ja", "zh"):
            markdown = translated[language]
            parsed = markdown_block(markdown)
            text = plain_text_from_block(parsed)
            block[language] = {
                "status": "reviewed",
                "source_sha256": block["source_sha256"],
                "markdown": markdown,
                "tokens": tokens_for_language(text, language),
                "model": model,
                "reasoning": reasoning,
                "reviewed_at": now_iso(),
            }


def atomic_write_entry(entry: dict[str, Any]) -> None:
    target = ENTRY_ROOT / f"{entry['id']}.json"
    temporary = target.with_suffix(".json.tmp")
    write_json(temporary, entry)
    temporary.replace(target)


def refresh_and_validate(entry_id: str) -> None:
    subprocess.run(
        [sys.executable, "scripts/prepare_multilingual.py"], cwd=ROOT, check=True
    )
    subprocess.run(
        [sys.executable, "scripts/validate_multilingual.py", "--entry", entry_id],
        cwd=ROOT,
        check=True,
    )


def commit_entry(entry: dict[str, Any]) -> None:
    path = ENTRY_ROOT / f"{entry['id']}.json"
    subprocess.run(["git", "add", str(path), str(MANIFEST_PATH)], cwd=ROOT, check=True)
    if not subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False
    ).returncode:
        return
    if entry["kind"] == "chapter":
        subject = f"Translate Chapter {entry['number']} into Japanese and Chinese"
    elif entry["kind"] == "introduction":
        subject = "Translate the introduction into Japanese and Chinese"
    else:
        subject = "Translate the source note into Japanese and Chinese"
    subprocess.run(["git", "commit", "-m", subject], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)


def translate_entry(
    entry_id: str,
    model: str,
    reasoning: str,
    max_attempts: int,
    force: bool,
    dry_run: bool,
    commit: bool,
) -> bool:
    entry = load_entry(entry_id)
    records = source_records(entry, force)
    if not records:
        print(f"{entry_id}: already complete")
        return True
    prompt = build_prompt(entry, records, [])
    if dry_run:
        print(
            f"{entry_id}: {len(records)} records, {len(prompt):,} prompt characters, "
            f"model={model}, reasoning={reasoning}"
        )
        return True

    repair: list[str] = []
    for attempt in range(1, max_attempts + 1):
        prompt = build_prompt(entry, records, repair)
        print(f"{entry_id}: translation attempt {attempt}/{max_attempts}", flush=True)
        response, diagnostic = run_codex(entry_id, prompt, model, reasoning, attempt)
        if response is None:
            repair = [diagnostic[-4000:]]
            if USAGE_LIMIT_RE.search(diagnostic):
                wait_seconds = int(os.environ.get("MULTILINGUAL_USAGE_WAIT_SECONDS", "1800"))
                print(f"{entry_id}: usage limit detected; waiting {wait_seconds}s", flush=True)
                time.sleep(wait_seconds)
            continue
        errors, accepted = validate_response(entry, records, response)
        if errors:
            repair = errors
            print(f"{entry_id}: rejected attempt with {len(errors)} issue(s)", flush=True)
            continue
        apply_translations(entry, accepted, model, reasoning)
        atomic_write_entry(entry)
        refresh_and_validate(entry_id)
        if commit:
            commit_entry(entry)
        print(f"{entry_id}: accepted {len(records)} translated records", flush=True)
        return True
    failure_path = RUNTIME_ROOT / entry_id / "failure.json"
    write_json(
        failure_path,
        {
            "entry": entry_id,
            "status": "failed",
            "attempts": max_attempts,
            "issues": repair,
            "updated_at": now_iso(),
        },
    )
    print(f"{entry_id}: failed after {max_attempts} attempts", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--entry", action="append")
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--reasoning", default="xhigh")
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest()
    known = [item["id"] for item in manifest["entries"]]
    entries = known if args.all else args.entry
    unknown = sorted(set(entries) - set(known))
    if unknown:
        parser.error(f"unknown entries: {', '.join(unknown)}")

    failed = []
    for entry_id in entries:
        success = translate_entry(
            entry_id,
            args.model,
            args.reasoning,
            args.max_attempts,
            args.force,
            args.dry_run,
            args.commit,
        )
        if not success:
            failed.append(entry_id)
            if not args.continue_on_error:
                break
    if failed:
        print(f"Failed entries: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
