# Amharic DBpedia Backend

Week 2 backend for the Amharic DBpedia automation pipeline.

It provides:

- FastAPI health, sanitizer, and DEF runner endpoints.
- A step 1-3 mapping-candidate pipeline:
  - streaming MediaWiki dump ingestion
  - infobox/template parameter extraction
  - Wikidata context enrichment
  - existing DEF mapping lookup
  - Afro-XLM-R ontology-property prediction
- CLI commands for local and CI usage.
- A conservative Amharic Wikipedia dump sanitizer.
- A DEF runner wrapper that stages a sanitized dump into the layout expected by the DBpedia Extraction Framework.

## Local commands

```bash
uv sync
uv run uvicorn amdb.main:app --reload
uv run pytest
uv run python -m amdb.cli.sanitize --input ../data/raw/sample_raw.xml --output ../data/sanitized/sample.sanitized.xml
uv run python -m amdb.cli.pipeline --input ../data/raw/sample_raw.xml --max-pages 10 --no-ml-model
```

Install the parser and real Afro-XLM-R prediction dependencies when you want the
full production path:

```bash
uv sync --extra pipeline
```

Without those optional dependencies, the backend still works for smoke tests:
it uses a conservative template parser and lexical fallback ranking.

The DEF runner expects the extraction framework checkout next to this repository by default:

```text
../extraction-framework
```

Override it with:

```bash
export AMDB_DEF_DIR=/absolute/path/to/extraction-framework
```

The mapping-candidate pipeline uses these files from the DEF checkout:

```text
ontology.xml
mappings/Mapping_am.xml
```

API endpoints:

```text
POST /api/pipeline/runs      starts a background run
GET  /api/pipeline/runs/{id} returns job status
POST /api/pipeline/preview   runs synchronously for small dumps
```
