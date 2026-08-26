#!/usr/bin/env python3
"""Report multilingual translation coverage by reading."""

from __future__ import annotations

from multilingual_common import load_entry, load_manifest


def main() -> int:
    manifest = load_manifest()
    complete = 0
    print("reading\tblocks\tja\tzh\tstatus")
    for item in manifest["entries"]:
        entry = load_entry(item["id"])
        ja = sum(block["ja"].get("status") == "reviewed" for block in entry["blocks"])
        zh = sum(block["zh"].get("status") == "reviewed" for block in entry["blocks"])
        metadata = all(
            str(entry["metadata"][field].get(language, "")).strip()
            for field in ("title", "question")
            for language in ("ja", "zh")
        )
        status = "complete" if ja == zh == entry["block_count"] and metadata else "pending"
        complete += status == "complete"
        print(f"{entry['id']}\t{entry['block_count']}\t{ja}\t{zh}\t{status}")
    print(
        f"TOTAL\t{manifest['block_count']}\t{manifest['reviewed_blocks']['ja']}\t"
        f"{manifest['reviewed_blocks']['zh']}\t{complete}/{manifest['entry_count']} complete"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
