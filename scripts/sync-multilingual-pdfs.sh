#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_root="$repo_root/editions/languages"
destination="${NUTSTORE_LAZYEARN_DIR:-$HOME/Nutstore Files/Share/LazyEarn}"

mkdir -p "$destination"

copy_verified() {
  local source="$1"
  local name="$2"
  local target="$destination/$name"
  local temporary="$destination/.${name}.tmp.$$"

  trap 'rm -f "$temporary"' RETURN
  test -s "$source"
  install -m 0644 "$source" "$temporary"
  test "$(sha256sum "$source" | cut -d' ' -f1)" = "$(sha256sum "$temporary" | cut -d' ' -f1)"
  mv -f "$temporary" "$target"
  test "$(sha256sum "$source" | cut -d' ' -f1)" = "$(sha256sum "$target" | cut -d' ' -f1)"
  trap - RETURN
  printf 'synced %s\n' "$target"
}

copy_verified "$source_root/how-you-got-rich-en.pdf" "How You Got Rich.pdf"
copy_verified "$source_root/how-you-got-rich-en-pocket-1.2x.pdf" "How You Got Rich - Pocket 1.2x.pdf"
copy_verified "$source_root/how-you-got-rich-ja.pdf" "How You Got Rich - Japanese (Furigana).pdf"
copy_verified "$source_root/how-you-got-rich-ja-pocket-1.2x.pdf" "How You Got Rich - Japanese (Furigana) - Pocket 1.2x.pdf"
copy_verified "$source_root/how-you-got-rich-zh.pdf" "How You Got Rich - Chinese (Pinyin).pdf"
copy_verified "$source_root/how-you-got-rich-zh-pocket-1.2x.pdf" "How You Got Rich - Chinese (Pinyin) - Pocket 1.2x.pdf"
copy_verified "$source_root/how-you-got-rich-en-ja-zh.pdf" "How You Got Rich - EN-JA-ZH Aligned.pdf"
copy_verified "$source_root/how-you-got-rich-en-ja-zh-pocket-1.2x.pdf" "How You Got Rich - EN-JA-ZH Aligned - Pocket 1.2x.pdf"
