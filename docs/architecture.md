# Amharic DBpedia TypeScript Architecture

## Purpose

This repository now separates the chapter-facing product from DBpedia data extraction.
The TypeScript code builds the public chapter website, resource viewer, query examples,
and lightweight graph exploration. It does not replace the DBpedia Extraction
Framework, which remains the upstream Scala data pipeline for converting Wikipedia
dumps and mappings into RDF.

## Workspace layout

- `apps/web`: vanilla TypeScript app built with Vite.
- `packages/core`: RDF, IRI, SPARQL, graph, and result-shape helpers.
- `packages/content`: typed multilingual chapter content and query examples.
- `tools/extraction`: operational notes and scripts for the DBpedia extraction boundary.
- `docs`: contributor-facing architecture, pipeline, and implementation documentation.

## Runtime design

The browser app uses native web platform primitives:

- History API for navigation.
- `URLPattern` when available, with an internal fallback matcher.
- `fetch` for SPARQL and raw RDF requests.
- `AbortController` for stale route fetch cancellation.
- DOM node creation and `textContent`, not string-based HTML rendering.
- Canvas2D for bounded one-hop ego graphs.

This keeps the browser bundle small and avoids a frontend framework while still giving
contributors a typed application structure.

## DBpedia boundary

DBpedia mappings connect language-specific Wikipedia templates to the language-neutral
DBpedia ontology. The DBpedia Extraction Framework then uses dumps, ontology files,
and mappings to produce RDF outputs. The Amharic web app consumes those outputs
through the public SPARQL endpoint and Databus collection.

The architectural rule is:

1. Mapping and extraction changes belong upstream in DBpedia/Mappings Wiki or
   automation repositories.
2. Dataset releases belong on Databus and in release artifacts.
3. The web app reads the endpoint, links to Databus, and explains contributor flows.

## Resource viewer flow

1. Route `/resource/:title` converts the title to `http://am.dbpedia.org/resource/...`.
2. `resource.service.ts` builds a bounded `SELECT DISTINCT ?predicate ?object` query.
3. `sparql.service.ts` fetches SPARQL JSON from the Amharic endpoint.
4. The result decoder maps bindings into RDF terms and resource facts.
5. `property-table.ts` renders safe DOM nodes.
6. `ego-graph.ts` renders a deterministic one-hop graph for named-node objects.
7. Raw Turtle and JSON-LD buttons run a `DESCRIBE` query and show the text in a
   bounded raw panel.

## Why generated dumps remain outside app code

The current repository contains RDF dump artifacts under `amDbpediaDump/`. They are
important project evidence, but the web app should not import them into the frontend.
Generated data should be published through Databus/releases and loaded into a triple
store. The app should link to those releases and query the endpoint.
