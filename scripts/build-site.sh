#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
site_root="$repo_root/build/site"

case "$site_root" in
  "$repo_root"/build/site) ;;
  *)
    printf 'Refusing unsafe site output path: %s\n' "$site_root" >&2
    exit 1
    ;;
esac

rm -rf "$site_root"
mkdir -p "$site_root/assets" "$site_root/editions"

rsync -a "$repo_root/docs/" "$site_root/"
rsync -a "$repo_root/editions/" "$site_root/editions/"
install -m 0644 "$repo_root/assets/cover-page-1.png" "$site_root/assets/cover-page-1.png"

printf 'Assembled website: %s\n' "$site_root"
