# Backend API Demo Guide

This guide explains how to demo the implemented FastAPI backend APIs for the
Amharic DBpedia automation pipeline.

The demo is backend-only. It focuses on Swagger, JSON responses, generated
reports, logs, and how each backend service connects to the DBpedia Extraction
Framework.

## Demo Goal

The goal is to show that the backend can:

1. Accept an Amharic Wikipedia dump.
2. Sanitize markup that can break the DEF parser.
3. Extract template mapping candidates through the step-3 pipeline.
4. Trigger or wrap the DBpedia Extraction Framework.
5. Generate dynamic RDF statistics from extracted Turtle files.
6. Serve precomputed statistics through fast API endpoints.

The key message for the demo:

```text
The backend is not a static dashboard backend anymore.
It now manages real dump artifacts, real reports, real extraction logs, and
dynamic statistics generated from RDF output files.
```

## Local Demo Inputs

The current checkout already has useful demo inputs:

```text
Small sanitizer fixture:
backend/tests/fixtures/sample_raw.xml

Real Amharic Wikipedia dump:
data/raw/amwiki-latest-pages-articles.xml.bz2

Existing extracted RDF output for statistics demo:
amDbpediaDump/GSoC2025/

Sanitized full dump from earlier sanitizer run:
data/sanitized/amwiki-latest-pages-articles.sanitized.xml.bz2
```

If the raw dump is missing on another machine, download the Amharic Wikipedia
`pages-articles` dump from:

```text
https://dumps.wikimedia.org/amwiki/latest/
```

Use the file named like:

```text
amwiki-latest-pages-articles.xml.bz2
```

Put it under:

```text
data/raw/
```

## Start The Backend

From the repository root:

```bash
cd /home/matania/Desktop/dbpedia/AmharicDBpediaChapter
just backend-dev
```

Equivalent direct command:

```bash
cd /home/matania/Desktop/dbpedia/AmharicDBpediaChapter/backend
uv run uvicorn amdb.main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

What to explain:

```text
Swagger is the demo surface. Every endpoint shown here is backed by a service
inside backend/src/amdb/services. The backend writes artifacts into data/
instead of keeping results only in memory.
```

## API 1: Health Check

Swagger endpoint:

```text
GET /api/health
```

Expected response:

```json
{
  "status": "ok"
}
```

What to explain:

```text
This proves FastAPI started correctly and route registration is working.
It does not prove the pipeline is working yet; it only confirms the service is
alive.
```

Code path:

```text
backend/src/amdb/main.py
  -> includes health router
backend/src/amdb/api/routes_health.py
  -> returns {"status": "ok"}
```

## API 2: Sanitizer Run

Swagger endpoint:

```text
POST /api/sanitizer/run
```

### Demo 2A: Small Controlled Fixture

Use this first because it is fast and predictable.

Request body:

```json
{
  "input_path": "/home/matania/Desktop/dbpedia/AmharicDBpediaChapter/backend/tests/fixtures/sample_raw.xml",
  "output_name": "demo-sample.sanitized.xml"
}
```

Shortened expected response shape:

```json
{
  "input_path": ".../backend/tests/fixtures/sample_raw.xml",
  "output_path": ".../data/sanitized/demo-sample.sanitized.xml",
  "report_path": ".../data/reports/demo-sample.sanitized.sanitizer-report.json",
  "pages_seen": 1,
  "pages_changed": 1,
  "rules_applied": [
    {
      "rule_id": "remove-raw-div-tags",
      "count": 1
    }
  ],
  "changed_pages_sample": [
    {
      "title": "...",
      "rule_ids": ["..."],
      "before_hash": "...",
      "after_hash": "..."
    }
  ]
}
```

The exact rules can vary based on the fixture content, but the important fields
are:

```text
pages_seen
pages_changed
rules_applied
output_path
report_path
```

What to explain:

```text
The sanitizer reads the MediaWiki XML dump, finds each page text node, applies
conservative cleanup rules, writes a sanitized dump, and writes a JSON report.

It does not translate Amharic text and does not rewrite valid wiki content.
It only removes known DEF parser-breaking patterns such as raw div/span tags,
style attributes, float CSS, thumb markers, and broken px image options.
```

Code path:

```text
POST /api/sanitizer/run
  -> backend/src/amdb/api/routes_sanitizer.py
  -> ArtifactService chooses output path
  -> DumpSanitizer.sanitize_dump()
  -> data/sanitized/<name>
  -> data/reports/<name>.sanitizer-report.json
```

Useful log lines to point out:

```text
[sanitizer.started]
[sanitizer.input_read_started]
[sanitizer.xml_parse_started]
[sanitizer.pages_started]
[sanitizer.page_changed]
[sanitizer.output_write_completed]
[sanitizer.report_written]
[sanitizer.completed]
```

### Demo 2B: Real Dump Sanitization

Use this when you want to show the system working on the real Amharic dump.

Request body:

```json
{
  "input_path": "/home/matania/Desktop/dbpedia/AmharicDBpediaChapter/data/raw/amwiki-latest-pages-articles.xml.bz2",
  "output_name": "amwiki-latest-pages-articles.demo.sanitized.xml.bz2"
}
```

What to explain:

```text
The same API works for .xml and .xml.bz2. For compressed dumps, the service reads
through bzip2 and writes the sanitized result back as compressed output when the
output name ends with .bz2.

For full dumps this is slower than the fixture, but it demonstrates the actual
artifact lifecycle expected by DEF.
```

What to show after the request:

```text
data/sanitized/amwiki-latest-pages-articles.demo.sanitized.xml.bz2
data/reports/amwiki-latest-pages-articles.demo.sanitized.sanitizer-report.json
```

## API 3: Mapping Candidate Pipeline Preview

Swagger endpoint:

```text
POST /api/pipeline/preview
```

This API demonstrates the implemented pipeline through step 3:

```text
Step 1: Stream MediaWiki dump pages and parse infobox-like templates.
Step 2: Optionally enrich page context with Wikidata hints.
Step 3: Predict DBpedia ontology properties from existing mappings, Afro-XLM-R,
        or lexical fallback.
```

The preview endpoint runs synchronously and immediately returns the result.
Use it for demos because it is easier to explain than a background job.

### Demo 3A: Page Range With No Templates

Request body:

```json
{
  "input_path": "/home/matania/Desktop/dbpedia/AmharicDBpediaChapter/data/raw/amwiki-latest-pages-articles.xml.bz2",
  "run_name": "demo-no-template",
  "max_pages": 1,
  "top_k": 3,
  "use_wikidata": false,
  "use_existing_mappings": true,
  "use_ml_model": false
}
```

Expected response:

```json
{
  "run_id": "demo-no-template",
  "pages_seen": 1,
  "templates_seen": 0,
  "parameters_seen": 0,
  "candidates_count": 0,
  "candidates_sample": []
}
```

What to explain:

```text
This is an important negative scenario. Not every Wikipedia page has an infobox.
The backend should not fail or invent mappings. It should report that it scanned
pages but found no template parameters to map.
```

### Demo 3B: Page Range With Templates

Request body:

```json
{
  "input_path": "/home/matania/Desktop/dbpedia/AmharicDBpediaChapter/data/raw/amwiki-latest-pages-articles.xml.bz2",
  "run_name": "demo-template-existing",
  "max_pages": 150,
  "top_k": 3,
  "use_wikidata": true,
  "use_existing_mappings": true,
  "use_ml_model": false
}
```

Expected result:

```text
pages_seen > 1
templates_seen > 0
parameters_seen > 0
candidates_count > 0
candidates_sample contains template parameters and DBpedia predictions
```

What to explain:

```text
This is the main mapping-candidate demo. The backend streams the dump instead of
loading the whole file into memory. When it reaches a page with an Amharic
infobox-like template, it extracts named parameters and builds a mapping
candidate for each parameter.

When use_existing_mappings=true, the predictor first checks the existing
Amharic DEF mappings in ../extraction-framework/mappings/Mapping_am.xml. This is
why many predictions can return confidence 1.0 with source
existing-def-mapping.

When use_wikidata=true, the backend attempts to find the same entity in Wikidata
and uses Wikidata property labels as semantic hints. If Wikidata is unavailable,
the pipeline logs the failure and continues without hints.

For the demo, use_ml_model=false keeps the run lightweight and deterministic.
If sentence-transformers and the Afro-XLM-R model are installed, setting
use_ml_model=true enables embedding-based prediction. If the model cannot be
loaded, the backend falls back to lexical prediction.
```

Important response fields:

```text
page_title:
  Which Wikipedia page produced the candidate.

template_name:
  The Amharic infobox/template name.

parameter_name:
  The Amharic template parameter being mapped.

wikidata_entity_id / wikidata_entity_label:
  Optional global entity context.

wikidata_hints:
  English property labels from Wikidata.

predictions:
  Candidate DBpedia ontology mappings.
```

Code path:

```text
POST /api/pipeline/preview
  -> backend/src/amdb/api/routes_pipeline.py
  -> MappingPipelineService.run()
  -> DumpTemplateParser.iter_pages()
  -> WikidataClient.get_context_for_title()
  -> AfroXlmrPropertyPredictor.predict()
  -> data/reports/<run-id>.mapping-pipeline-report.json
```

Useful log lines to point out:

```text
[ingestion.started]
[ingestion.parser_loaded] or [ingestion.parser_fallback]
[ontology.load_started]
[mapping_index.load_started]
[pipeline.started]
[pipeline.candidate_predicted]
[pipeline.completed]
```

## API 4: Background Mapping Pipeline Job

Swagger endpoints:

```text
POST /api/pipeline/runs
GET /api/pipeline/runs/{job_id}
```

Use this to show the same pipeline as a background job.

Start request:

```json
{
  "input_path": "/home/matania/Desktop/dbpedia/AmharicDBpediaChapter/data/raw/amwiki-latest-pages-articles.xml.bz2",
  "run_name": "demo-background-pipeline",
  "max_pages": 150,
  "top_k": 3,
  "use_wikidata": true,
  "use_existing_mappings": true,
  "use_ml_model": false
}
```

Expected initial response:

```json
{
  "job_id": "demo-background-pipeline",
  "status": "queued",
  "input_path": "...",
  "report_path": null,
  "error": null
}
```

Then call:

```text
GET /api/pipeline/runs/demo-background-pipeline
```

Expected later response:

```json
{
  "job_id": "demo-background-pipeline",
  "status": "succeeded",
  "input_path": "...",
  "report_path": ".../data/reports/demo-background-pipeline.mapping-pipeline-report.json",
  "error": null
}
```

What to explain:

```text
The preview endpoint is best for interactive explanation. The background job
endpoint is closer to production orchestration: the API returns quickly, the
pipeline continues in the background, and the frontend or operator can poll the
job status.

The current job store is in memory, so it is suitable for demos and local
development. For production, this should move to a persistent database.
```

## API 5: Run DEF On Sanitized Dump

Swagger endpoint:

```text
POST /api/extraction/run-def
```

Request body:

```json
{
  "sanitized_dump_path": "/home/matania/Desktop/dbpedia/AmharicDBpediaChapter/data/sanitized/amwiki-latest-pages-articles.sanitized.xml.bz2",
  "config_path": "/home/matania/Desktop/dbpedia/AmharicDBpediaChapter/extraction/config/extraction.am.properties",
  "run_name": "demo-def-run",
  "generate_statistics": true,
  "statistics_source_dir": null,
  "use_native_def_statistics": false,
  "statistics_max_files": null
}
```

Expected response shape:

```json
{
  "run_id": "demo-def-run",
  "sanitized_dump_path": ".../data/sanitized/amwiki-latest-pages-articles.sanitized.xml.bz2",
  "output_dir": ".../data/def-runs/demo-def-run",
  "stdout_path": ".../data/def-runs/demo-def-run/stdout.log",
  "stderr_path": ".../data/def-runs/demo-def-run/stderr.log",
  "exit_code": 0,
  "success": true,
  "statistics_job_scheduled": true
}
```

What to explain:

```text
This endpoint does not implement DEF in Python. It wraps the real Scala DBpedia
Extraction Framework by calling extraction/scripts/run_def.sh.

The shell script stages the sanitized dump into the layout DEF expects, writes a
runtime extraction config, runs ../extraction-framework/dump via ../run
extraction, and captures stdout/stderr into data/def-runs/<run-id>.

If DEF succeeds and generate_statistics=true, the backend schedules statistics
generation after extraction.
```

Important local environment note:

```text
If the response has success=false and exit_code=1, inspect stdout_path and
stderr_path. In the current local setup, DEF can fail because the extraction
framework requires Java 8. That is an environment/runtime issue, not a FastAPI
API failure.
```

What to show if DEF fails:

```text
data/def-runs/demo-def-run/stdout.log
data/def-runs/demo-def-run/stderr.log
```

What to explain if DEF fails:

```text
The backend still performed its job: it validated inputs, called the DEF runner,
captured logs, returned the exit code, and preserved the failure evidence. The
next operational step is fixing the Java/DEF runtime, not changing the API.
```

Code path:

```text
POST /api/extraction/run-def
  -> backend/src/amdb/api/routes_extraction.py
  -> DefRunner.run()
  -> extraction/scripts/run_def.sh
  -> ../extraction-framework/dump
  -> data/def-runs/<run-id>/stdout.log
  -> data/def-runs/<run-id>/stderr.log
```

Useful log lines to point out:

```text
[def_runner.started]
[def_runner.validation_completed]
[def_runner.command_prepared]
[def_runner.process_started]
[def_runner.process_completed]
[def_runner.logs_written]
[def_runner.succeeded] or [def_runner.failed]
[extraction.statistics_scheduled]
```

## API 6: Generate Dynamic RDF Statistics

Swagger endpoint:

```text
POST /api/statistics/generate
```

Use this endpoint to show dynamic statistics without depending on a fresh DEF
run. It scans existing RDF outputs and writes a precomputed JSON report.

Request body:

```json
{
  "source_dir": "/home/matania/Desktop/dbpedia/AmharicDBpediaChapter/amDbpediaDump/GSoC2025",
  "run_name": "demo-gsoc2025-statistics",
  "dump_date": "20250820",
  "extraction_run_id": "GSoC2025",
  "use_native_def_stats": false,
  "max_files": null
}
```

Expected response fields:

```text
run_id
source_dir
report_path
generated_at
success
engine
file_count
total_triples
unique_subjects
unique_predicates
unique_objects
mapping_based_triples
raw_infobox_triples
dataset_statistics
native_def_stats
```

The current local smoke run over `amDbpediaDump/GSoC2025` produced:

```text
file_count: 32
total_triples: 600792
unique_subjects: 68937
unique_predicates: 1016
unique_objects: 230955
mapping_based_triples: 19456
raw_infobox_triples: 39892
```

What to explain:

```text
Statistics are not calculated when a website user refreshes the page. They are
precomputed after extraction or on demand by this API.

This is the correct design because RDF statistics can involve many compressed
Turtle files and hundreds of thousands or millions of triples. The API reads the
saved JSON report quickly, instead of recalculating graph counts on every
request.
```

What the backend counts:

```text
total_triples:
  Number of RDF statements parsed across the selected files.

unique_subjects:
  Number of unique resources/entities appearing as RDF subjects.

unique_predicates:
  Number of unique RDF properties.

unique_objects:
  Number of unique RDF object values.

mapping_based_triples:
  Triples from mapping-based datasets such as mappingbased-literals,
  mappingbased-objects, geo-coordinates-mappingbased, and
  specific-mappingbased-properties.

raw_infobox_triples:
  Triples from raw infobox property datasets such as infobox-properties.

dataset_statistics:
  Per-file counts and top predicates.
```

Code path:

```text
POST /api/statistics/generate
  -> backend/src/amdb/api/routes_statistics.py
  -> StatisticsService.generate()
  -> stream .ttl/.ttl.bz2/.nt/.nt.bz2 files
  -> data/reports/<run-id>.statistics-report.json
  -> data/reports/statistics-latest.json
```

Useful log lines to point out:

```text
[statistics.started]
[statistics.files_discovered]
[statistics.file_started]
[statistics.file_completed]
[statistics.completed]
```

## Native DEF Statistics Option

The statistics request has:

```json
{
  "use_native_def_stats": true
}
```

What it does:

```text
It calls extraction/scripts/run_statistics.sh.
That script wraps ../extraction-framework/scripts/src/main/bash/collectStats.sh.
collectStats.sh runs DEF TypeStatistics and StatsPostProcessing.
```

What to explain:

```text
The official DEF statistics tools are preserved, but they require DEF's release
directory layout, usually core-i18n/<wiki>/<dataset>_<wiki>.ttl.bz2. They can
also require Java 8 and high heap settings.

For flat local demo folders like amDbpediaDump/GSoC2025, the Python streaming
statistics engine is the feasible default. It produces the dynamic API numbers
we need today while keeping the official DEF stats path available for release
layouts.
```

## API 7: Read Latest Statistics

Swagger endpoint:

```text
GET /api/statistics/latest
```

Shortened expected response:

```json
{
  "run_id": "demo-gsoc2025-statistics",
  "success": true,
  "file_count": 32,
  "total_triples": 600792,
  "dataset_statistics": []
}
```

The real response includes the full `dataset_statistics` array.

What to explain:

```text
This is what the frontend should call. It is fast because it reads
data/reports/statistics-latest.json. It does not scan RDF files during the GET
request.
```

## API 8: List And Read Statistics Runs

Swagger endpoints:

```text
GET /api/statistics/runs
GET /api/statistics/runs/{run_id}
```

Use:

```text
GET /api/statistics/runs
```

to show all available statistics reports.

Then use:

```text
GET /api/statistics/runs/demo-gsoc2025-statistics
```

to retrieve one specific report.

What to explain:

```text
This makes statistics reproducible. Instead of only showing one hard-coded
number, each extraction or demo run gets a report with run_id, source_dir,
dump_date, extraction_run_id, counts, and per-dataset details.
```

## Complete Recommended Demo Order

Use this sequence in a live presentation:

```text
1. GET /api/health
   Explain that the backend is alive.

2. POST /api/sanitizer/run with the small fixture.
   Explain conservative cleanup and report generation.

3. POST /api/sanitizer/run with the real dump if time allows.
   Explain real artifact generation for DEF.

4. POST /api/pipeline/preview with max_pages=1.
   Explain the no-template case.

5. POST /api/pipeline/preview with max_pages=150.
   Explain ingestion, Wikidata hints, existing Mapping_am.xml, and predictions.

6. POST /api/extraction/run-def.
   Explain that Python hands off to the real Scala DEF and captures logs.

7. POST /api/statistics/generate using amDbpediaDump/GSoC2025.
   Explain dynamic precomputed RDF statistics.

8. GET /api/statistics/latest.
   Explain this is the fast endpoint a frontend dashboard should call.

9. GET /api/statistics/runs.
   Explain reproducibility across extraction runs.
```

## How To Explain The Architecture In One Flow

Use this summary during the demo:

```text
The dump first enters the sanitizer, which removes parser-breaking markup and
writes a sanitized XML artifact plus a report.

The mapping pipeline then streams the dump page by page, extracts infobox-like
templates, optionally enriches each page with Wikidata, and predicts DBpedia
properties using existing DEF mappings, Afro-XLM-R when available, or lexical
fallback.

The extraction endpoint then hands the sanitized dump to the real DBpedia
Extraction Framework. The backend captures the DEF logs and exit code so parser
failures and runtime failures are visible.

After RDF files exist, the statistics service scans compressed Turtle output
once, writes a statistics JSON report, and serves that report through fast GET
endpoints.
```

## Expected Generated Files

After the demo, these folders should contain evidence:

```text
data/sanitized/
  Sanitized XML or XML.BZ2 dump files.

data/reports/
  *.sanitizer-report.json
  *.mapping-pipeline-report.json
  *.statistics-report.json
  statistics-latest.json

data/def-runs/
  <run-id>/stdout.log
  <run-id>/stderr.log
  <run-id>/extraction.runtime.properties
  <run-id>/dumps/
```

What to explain:

```text
These files are mentor-proof artifacts. They show what input was used, what
changed, what the backend predicted, whether DEF succeeded, and what statistics
were generated from RDF output.
```

## Demo Troubleshooting

### DEF returns success=false

Check:

```text
stdout_path
stderr_path
```

Explain:

```text
The backend captured the failure. If the logs mention Java 8, the fix is to run
DEF with the required Java runtime.
```

### Pipeline returns zero candidates

Check:

```text
max_pages
```

Explain:

```text
The first pages in the dump may not contain infobox templates. Increase max_pages
to 150 or more for the real Amharic dump demo.
```

### Wikidata hints are empty

Explain:

```text
Wikidata is optional context enrichment. If the lookup fails, the backend
continues with existing mappings and lexical or ML prediction.
```

### Afro-XLM-R does not load

Explain:

```text
The model is optional for the current backend demo. If sentence-transformers or
the model files are unavailable, the predictor logs the fallback and uses lexical
matching. Existing DEF mappings still produce high-confidence predictions for
known Amharic parameters.
```

### Statistics source has no RDF files

Explain:

```text
The statistics service scans .ttl, .ttl.bz2, .nt, .nt.bz2, .ntriples, and
.ntriples.bz2 files. Point source_dir to the extraction output folder or to an
existing RDF folder such as amDbpediaDump/GSoC2025.
```
