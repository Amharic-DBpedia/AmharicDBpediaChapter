# ADR 0001: Vanilla TypeScript Frontend

## Status

Accepted.

## Context

The Amharic chapter needs a durable public website and resource viewer, not a large
interactive application framework. The main complexity is DBpedia domain logic:
SPARQL, RDF terms, mappings, data releases, and endpoint behavior.

## Decision

Use Vite with vanilla TypeScript. Do not introduce a client framework for routing,
state, or templating. Use focused libraries only when the web platform is insufficient.

## Consequences

The app stays small and transparent for contributors. Shared behavior must be kept in
typed modules so route code does not become a new monolith.
