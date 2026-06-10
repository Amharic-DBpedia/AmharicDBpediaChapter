#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:?Missing RDF source/base directory}"
OUTPUT_DIR="${2:?Missing statistics output directory}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_DEF_DIR="$(cd "$SCRIPT_DIR/../../../extraction-framework" 2>/dev/null && pwd || true)"
DEF_DIR="${DEF_DIR:-$DEFAULT_DEF_DIR}"
COLLECT_STATS="$DEF_DIR/scripts/src/main/bash/collectStats.sh"

log_step() {
  printf '[amdb-statistics] %s %s\n' "$1" "$2"
}

log_step "started" "Preparing native DBpedia statistics run"
log_step "input" "source_dir=$SOURCE_DIR"
log_step "input" "output_dir=$OUTPUT_DIR"
log_step "input" "def_dir=$DEF_DIR"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "RDF source/base directory does not exist: $SOURCE_DIR" >&2
  exit 2
fi
log_step "validated" "RDF source/base directory exists"

if [ ! -f "$COLLECT_STATS" ]; then
  echo "DEF collectStats.sh does not exist: $COLLECT_STATS" >&2
  exit 2
fi
log_step "validated" "DEF collectStats.sh exists"

SOURCE_DIR="$(cd "$SOURCE_DIR" && pwd)"
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"

log_step "layout_note" "collectStats.sh expects DBpedia release layout: core-i18n/<wiki>/<dataset>_<wiki>.ttl.bz2"
log_step "runtime_note" "DEF statistics launchers may require Java 8 and high heap settings"

cd "$DEF_DIR/scripts"
log_step "native_process_started" "Running collectStats.sh"
bash "$COLLECT_STATS" "$SOURCE_DIR"
log_step "native_process_completed" "collectStats.sh completed"

if [ -d "$SOURCE_DIR/statistics" ]; then
  mkdir -p "$OUTPUT_DIR/native-statistics"
  cp -a "$SOURCE_DIR/statistics/." "$OUTPUT_DIR/native-statistics/"
  log_step "outputs_copied" "statistics_dir=$OUTPUT_DIR/native-statistics"
else
  log_step "outputs_missing" "No source statistics directory was created"
fi
