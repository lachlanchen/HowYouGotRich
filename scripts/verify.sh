#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
verify_dir="$repo_root/build/verify"
mkdir -p "$verify_dir"

(
  cd "$repo_root/editions"
  sha256sum -c SHA256SUMS
)

verify_pdf() {
  local pdf="$1"
  local label="$2"
  local text_path="$verify_dir/$label.txt"

  qpdf --check "$pdf" >/dev/null
  if pdffonts "$pdf" | tail -n +3 | grep -Eq '[[:space:]]no[[:space:]]'; then
    echo "Unembedded font detected in $pdf" >&2
    exit 1
  fi
  pdftotext "$pdf" "$text_path"
  grep -Fq 'Some costs are reversible' "$text_path"
  grep -Fq 'Mencius treated a stable livelihood' "$text_path"
  if grep -Eiq 'codex|prompt tool|agent session|private conversation|ProjectsLFS|generated_course_notes' "$text_path"; then
    echo "Reader-visible production language detected in $pdf" >&2
    exit 1
  fi
  pdfinfo "$pdf" | awk -v file="$pdf" '/^Pages:|^Page size:/ {print file ": " $0}'
}

accepted_full="$repo_root/editions/how-you-got-rich.pdf"
accepted_pocket="$repo_root/editions/how-you-got-rich-pocket-1.2x.pdf"
verify_pdf "$accepted_full" accepted-full
verify_pdf "$accepted_pocket" accepted-pocket

built_full="$repo_root/build/full/how-you-got-rich.pdf"
built_pocket="$repo_root/build/pocket/how-you-got-rich-pocket-1.2x.pdf"
if [[ -f "$built_full" ]]; then
  verify_pdf "$built_full" built-full
  cmp "$verify_dir/accepted-full.txt" "$verify_dir/built-full.txt"
fi
if [[ -f "$built_pocket" ]]; then
  verify_pdf "$built_pocket" built-pocket
  cmp "$verify_dir/accepted-pocket.txt" "$verify_dir/built-pocket.txt"
fi

full_log="$repo_root/build/logs/full-pass-3.log"
if [[ -f "$full_log" ]]; then
  # Four intentional ragged lines belong to the overlaid full-cover text.
  test "$(grep -c 'Underfull \\hbox' "$full_log")" -eq 4
  ! grep -Eq 'Overfull|Fatal error|Emergency stop' "$full_log"
fi

pocket_log="$repo_root/build/logs/pocket.log"
if [[ -f "$pocket_log" ]]; then
  ! grep -Eq 'Overfull|Underfull|Fatal error|Emergency stop' "$pocket_log"
fi

test "$(awk 'END {print NR - 1}' "$repo_root/sources/interviews.csv")" -eq 135
test "$(awk 'END {print NR - 1}' "$repo_root/sources/figures.csv")" -eq 2

echo 'Accepted editions and public source records verified.'
