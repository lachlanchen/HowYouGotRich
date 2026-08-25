#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/source/book"
output_dir="$repo_root/build/full"
log_dir="$repo_root/build/logs"

mkdir -p "$output_dir" "$log_dir"

for pass in 1 2 3; do
  (
    cd "$source_dir"
    pdflatex \
      -interaction=nonstopmode \
      -halt-on-error \
      -file-line-error \
      -output-directory="$output_dir" \
      how-you-got-rich.tex
  ) >"$log_dir/full-pass-$pass.log" 2>&1
done

pdf="$output_dir/how-you-got-rich.pdf"
test -s "$pdf"
printf 'Built %s\n' "$pdf"
sha256sum "$pdf"
