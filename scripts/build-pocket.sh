#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compile_root="$repo_root/build/pocket-work"
compile_output="$compile_root/book/build"
publish_dir="$repo_root/build/pocket"
log_path="$repo_root/build/logs/pocket.log"

mkdir -p "$publish_dir" "$(dirname "$log_path")"

"$repo_root/scripts/build-pocket-variant.sh" \
  --source-root "$repo_root/source" \
  --main-tex book/how-you-got-rich.tex \
  --compile-root "$compile_root" \
  --build-dir "$compile_output" \
  --log-path "$log_path" \
  --font-mode onepointtwo \
  --paper-width 6in \
  --paper-height 9in \
  --margin 0.55in \
  --compile-engine pdflatex

source_pdf="$compile_output/how-you-got-rich.pdf"
output_pdf="$publish_dir/how-you-got-rich-pocket-1.2x.pdf"
test -s "$source_pdf"
install -m 0644 "$source_pdf" "$output_pdf"
printf 'Built %s\n' "$output_pdf"
sha256sum "$output_pdf"
