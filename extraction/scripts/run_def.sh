#!/usr/bin/env bash
set -euo pipefail

SANITIZED_DUMP_PATH="${1:?Missing sanitized dump path}"
OUTPUT_DIR="${2:?Missing output directory}"
CONFIG_PATH="${3:?Missing DEF config path}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_DEF_DIR="$(cd "$SCRIPT_DIR/../../../extraction-framework" 2>/dev/null && pwd || true)"
DEF_DIR="${DEF_DIR:-$DEFAULT_DEF_DIR}"
LANGUAGE="${AMDB_DEF_LANGUAGE:-am}"
WIKI_CODE="${LANGUAGE}wiki"

log_step() {
  printf '[amdb-def] %s %s\n' "$1" "$2"
}

log_step "started" "Preparing DBpedia Extraction Framework run"
log_step "input" "sanitized_dump_path=$SANITIZED_DUMP_PATH"
log_step "input" "output_dir=$OUTPUT_DIR"
log_step "input" "config_path=$CONFIG_PATH"
log_step "input" "def_dir=$DEF_DIR"
log_step "input" "wiki_code=$WIKI_CODE"

if [ ! -f "$SANITIZED_DUMP_PATH" ]; then
  echo "Sanitized dump does not exist: $SANITIZED_DUMP_PATH" >&2
  exit 2
fi
log_step "validated" "Sanitized dump exists"

if [ ! -d "$DEF_DIR/dump" ]; then
  echo "DEF dump module does not exist: $DEF_DIR/dump" >&2
  exit 2
fi
log_step "validated" "DEF dump module exists"

if [ ! -f "$CONFIG_PATH" ]; then
  echo "DEF config does not exist: $CONFIG_PATH" >&2
  exit 2
fi
log_step "validated" "DEF config exists"

mkdir -p "$OUTPUT_DIR"
SANITIZED_DUMP_PATH="$(cd "$(dirname "$SANITIZED_DUMP_PATH")" && pwd)/$(basename "$SANITIZED_DUMP_PATH")"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"
CONFIG_PATH="$(cd "$(dirname "$CONFIG_PATH")" && pwd)/$(basename "$CONFIG_PATH")"
log_step "paths_resolved" "sanitized_dump_path=$SANITIZED_DUMP_PATH"
log_step "paths_resolved" "output_dir=$OUTPUT_DIR"
log_step "paths_resolved" "config_path=$CONFIG_PATH"

DUMP_BASENAME="$(basename "$SANITIZED_DUMP_PATH")"
if [[ "$DUMP_BASENAME" =~ ${WIKI_CODE}-([0-9]{8})- ]]; then
  DUMP_DATE="${BASH_REMATCH[1]}"
else
  DUMP_DATE="${AMDB_DUMP_DATE:-20250101}"
fi
log_step "dump_date" "dump_date=$DUMP_DATE"

RUNTIME_BASE_DIR="$OUTPUT_DIR/dumps"
RUNTIME_LOG_DIR="$OUTPUT_DIR/logs"
RUNTIME_DUMP_DIR="$RUNTIME_BASE_DIR/$WIKI_CODE/$DUMP_DATE"
RUNTIME_CONFIG="$OUTPUT_DIR/extraction.runtime.properties"
RUNTIME_SOURCE="pages-articles.xml.bz2"
RUNTIME_DUMP="$RUNTIME_DUMP_DIR/$WIKI_CODE-$DUMP_DATE-$RUNTIME_SOURCE"

mkdir -p "$RUNTIME_DUMP_DIR" "$RUNTIME_LOG_DIR"
log_step "runtime_dirs_created" "runtime_dump_dir=$RUNTIME_DUMP_DIR runtime_log_dir=$RUNTIME_LOG_DIR"

case "$SANITIZED_DUMP_PATH" in
  *.bz2)
    log_step "dump_stage_started" "Copying compressed dump into DEF runtime layout"
    cp "$SANITIZED_DUMP_PATH" "$RUNTIME_DUMP"
    ;;
  *)
    log_step "dump_stage_started" "Compressing XML dump into DEF runtime layout"
    bzip2 -c "$SANITIZED_DUMP_PATH" > "$RUNTIME_DUMP"
    ;;
esac
log_step "dump_stage_completed" "runtime_dump=$RUNTIME_DUMP"

log_step "config_stage_started" "Writing DEF runtime extraction config"
grep -v -E '^(base-dir|log-dir|source)=' "$CONFIG_PATH" > "$RUNTIME_CONFIG"
{
  echo "base-dir=$RUNTIME_BASE_DIR"
  echo "log-dir=$RUNTIME_LOG_DIR"
  echo "source=$RUNTIME_SOURCE"
} >> "$RUNTIME_CONFIG"
log_step "config_stage_completed" "runtime_config=$RUNTIME_CONFIG"

log_step "def_process_started" "Running DBpedia Extraction Framework"
log_step "def_process_started" "DEF_DIR=$DEF_DIR"
log_step "def_process_started" "Runtime config=$RUNTIME_CONFIG"
log_step "def_process_started" "Staged dump=$RUNTIME_DUMP"

cd "$DEF_DIR/dump"
../run extraction "$RUNTIME_CONFIG"
