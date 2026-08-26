#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 scripts/prepare_multilingual.py --check
python3 scripts/translate_multilingual.py \
  --all \
  --model "${MULTILINGUAL_MODEL:-gpt-5.6-sol}" \
  --reasoning "${MULTILINGUAL_REASONING:-xhigh}" \
  --max-attempts "${MULTILINGUAL_MAX_ATTEMPTS:-3}" \
  --continue-on-error \
  --commit
python3 scripts/validate_multilingual.py --require-complete
