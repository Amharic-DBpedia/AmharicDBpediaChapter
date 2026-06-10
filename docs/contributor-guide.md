# Contributor Guide

## Setup

```bash
pnpm install
pnpm dev
```

Open the Vite dev server URL printed by the command.

## Common commands

```bash
pnpm run typecheck
pnpm run lint
pnpm run test
pnpm run build
```

## Working with content

Static website copy, chapter metrics, query examples, resource links, and contributor
cards live in `packages/content/src/site-content.ts`. Add all maintained languages at
the same time. If a translation is not maintained, prefer English over stale text.

## Working with RDF and SPARQL

Shared RDF and SPARQL helpers live in `packages/core/src`. Add query builders there
when multiple features need the same query. Keep endpoint URLs and DBpedia constants
centralized so future endpoint migrations do not require route rewrites.

## Working with extraction outputs

Do not import RDF dump files into `apps/web`. Extraction outputs should be produced by
DBpedia extraction tooling, validated, published as release artifacts, and loaded into a
SPARQL endpoint. The web app should link to Databus and query the endpoint.

## Documentation rule

Each implementation change that introduces a new architectural boundary, DBpedia
workflow assumption, route, or data-release process should update one of the Markdown
docs in this folder. Small visual or copy-only changes do not need an architecture note.
