# Amharic DBpedia RDF Pipeline

## End-to-end model

The Amharic DBpedia pipeline has four distinct stages:

1. Amharic Wikipedia pages use structured templates, especially infoboxes.
2. DBpedia mappings connect those templates and parameters to ontology classes and
   properties.
3. The DBpedia Extraction Framework reads Wikimedia dumps, ontology files, and
   mappings, then emits RDF datasets.
4. Published datasets are loaded into a SPARQL endpoint and linked from the chapter
   website.

## GSoC 2025 documentation facts carried into the app

The project PDF documents the 2025 contributor workflow and current quality state:

- The report is an end-to-end guide for Wikipedia templates, mappings, extraction,
  statistics, Fuseki querying, and automation.
- Mapping quality improved from 17 mapped templates to 97 fully mapped templates.
- Template coverage reached 100%.
- Property mapping coverage improved from 15.70% to 77.29%.
- Property occurrence coverage reached 99.15%.
- Statistics generation should use `infobox-properties.ttl` instead of the older
  `infobox-test.ttl`.
- Remaining work includes translating English-only templates, harmonizing template
  names around `መረጃሳጥን`, maintaining an ignore list, and establishing stronger
  extraction infrastructure.

## Research paper facts carried into the app

`paper-amharic-dbpedia-research.pdf` adds the research framing and the public release
baseline:

- Amharic DBpedia is presented as a knowledge graph chapter for a low-resource
  language.
- The extraction work extends DEF with an Ethiopian date parser, Ethiopian-Gregorian
  calendar converter, Arabic-Ge'ez numeral converter, Amharic template mappings, and
  automated extraction workflows.
- The released graph contains 528,370 unique triples.
- The paper reports mapping statistics of 84/84 templates mapped, 2,392/3,095
  properties mapped, 3,958/3,958 template occurrences mapped, and 19,799/19,968
  property occurrences mapped.
- NLLB-200 reached BLEU 45.31 for zero-shot Amharic infobox property translation.
- Fine-tuned Afro-XLM-R reached 92.1% Top-10 accuracy for ontology property alignment.
- Public access is described through the live website, DBpedia Databus collection,
  Tentris query endpoint, automation workflows, documentation, and Zenodo archive.

## Local development endpoint guidance

For production-like DBpedia chapter hosting, Virtuoso remains the natural public
endpoint target because DBpedia itself documents and uses Virtuoso-backed SPARQL
services. For local contributor loops, the PDF recommends lightweight stores such as
Apache Jena Fuseki or Blazegraph when Virtuoso is too heavy.

The repo therefore treats triple stores as operational dependencies:

- Production: Virtuoso loaded from a Databus collection.
- Local smoke testing: Fuseki, Oxigraph, or another lightweight SPARQL server.
- Browser app: no embedded triple store.

## Validation loop

Every data-release cycle should include:

1. Regenerate extraction outputs from a known dump date.
2. Generate mapping statistics from `infobox-properties.ttl`.
3. Review templates with no useful properties, wrong ontology classes, or mixed
   English/Amharic property names.
4. Run regression SPARQL queries against representative resources.
5. Publish RDF artifacts to Databus and update chapter stats.

The website content should be updated only after the data-release state is known.
