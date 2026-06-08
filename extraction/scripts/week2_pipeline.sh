#!/usr/bin/env bash
set -euo pipefail

RAW_DUMP="${1:?Missing raw dump path}"
SANITIZED_OUTPUT="${2:?Missing sanitized output path}"
DEF_OUTPUT_DIR="${3:?Missing DEF output directory}"
CONFIG_PATH="${4:-extraction/config/extraction.am.properties}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.."

cd "$ROOT_DIR/backend"
uv run python -m amdb.cli.sanitize \
  --input "../$RAW_DUMP" \
  --output "../$SANITIZED_OUTPUT"

cd "$ROOT_DIR"
bash extraction/scripts/run_def.sh \
  "$SANITIZED_OUTPUT" \
  "$DEF_OUTPUT_DIR" \
  "$CONFIG_PATH"
