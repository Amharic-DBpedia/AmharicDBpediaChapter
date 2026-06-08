set dotenv-load := true

backend-sync:
    cd backend && uv sync

backend-dev:
    cd backend && uv run uvicorn amdb.main:app --reload

backend-test:
    cd backend && uv run pytest

backend-lint:
    cd backend && uv run ruff check src tests && uv run mypy src

sanitize input output:
    cd backend && uv run python -m amdb.cli.sanitize --input "../{{input}}" --output "../{{output}}"

run-def dump run_name="week2-smoke":
    cd backend && uv run python -m amdb.cli.run_def --dump "../{{dump}}" --run-name "{{run_name}}"

week2-pipeline raw_dump sanitized_output run_name="week2-smoke":
    bash extraction/scripts/week2_pipeline.sh "{{raw_dump}}" "{{sanitized_output}}" "data/def-runs/{{run_name}}" "extraction/config/extraction.am.properties"
