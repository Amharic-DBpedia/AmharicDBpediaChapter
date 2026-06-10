# ADR 0002: DBpedia Extraction Remains External

## Status

Accepted.

## Context

DBpedia extraction is an established Scala framework and operational workflow. The
Amharic chapter site should present and consume extracted RDF, but it should not try
to reimplement dump extraction in TypeScript.

## Decision

Keep extraction, statistics, validation, and Databus publication under `tools/extraction`
as operational guidance and scripts. Keep the browser app focused on website,
resource viewer, query examples, and endpoint consumption.

## Consequences

This avoids a misleading TypeScript rewrite of DBpedia's core extraction layer. It also
keeps future infrastructure work discoverable in this repository.
