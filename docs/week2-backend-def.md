# Week 2 Backend and DEF Verification

## DEF context

The DBpedia Extraction Framework has four important pieces for this project:

- Source: reads MediaWiki XML pages from a dump.
- WikiParser: parses wiki markup into an AST.
- Extractor: turns AST/page data into RDF statements.
- Destination: writes RDF datasets such as labels, infobox properties, mappings, and page links.

For Amharic, the parser is the fragile boundary. Raw HTML fragments, CSS declarations, image options such as `thumb` and `250px`, and inconsistent infobox syntax can cause failures before useful triples are written. The Week 2 backend therefore sanitizes the dump before DEF sees it, then runs DEF against the sanitized artifact.

## Implemented pipeline

```text
FastAPI / CLI
  -> DumpSanitizer
    -> data/sanitized/*.xml or *.xml.bz2
    -> data/reports/*.sanitizer-report.json
  -> DefRunner
    -> extraction/scripts/run_def.sh
      -> sibling ../extraction-framework/dump
      -> data/def-runs/<run-id>/stdout.log
      -> data/def-runs/<run-id>/stderr.log
```

## Commands

```bash
just backend-sync
just backend-test
just backend-dev
```

```bash
just sanitize data/raw/sample_raw.xml data/sanitized/sample.sanitized.xml
just run-def data/sanitized/sample.sanitized.xml week2-smoke
```

## Done criteria

- `/api/health` returns `{"status": "ok"}`.
- `POST /api/sanitizer/run` writes a sanitized dump and report.
- `uv run pytest` passes.
- `POST /api/extraction/run-def` stages the sanitized dump into DEF layout and captures stdout/stderr.
- Raw-vs-sanitized DEF logs can be compared for parser IOException counts.
