# Frontend Implementation Notes

## Why vanilla TypeScript

The app is small, data-oriented, and long-lived. A framework would not solve the core
problems: RDF modeling, SPARQL query safety, endpoint behavior, and contributor
documentation. Vanilla TypeScript with Vite gives fast builds, typed modules, and a
small browser runtime.

## Rendering rules

- Build UI with DOM APIs and `textContent`.
- Use `innerHTML` only for static trusted templates if a future component explicitly
  needs it.
- Keep SPARQL construction in services, not route files.
- Keep DBpedia constants in `packages/core`.
- Keep editorial content in `packages/content`.
- Keep route files focused on orchestration and mount/unmount behavior.

## Resource viewer behavior

The viewer intentionally performs bounded exploration:

- Default fact query is capped at 1000 rows.
- Amharic titles are preserved as Unicode IRIs when querying SPARQL. Do not
  percent-encode a title before placing it inside `<...>`; that causes endpoint
  lookups for encoded resources such as `%E1...` and can produce double-encoded raw
  RDF displays.
- Graph rendering uses named-node objects only and caps edges.
- Raw Turtle and JSON-LD are fetched on demand.
- Search accepts either a full IRI or a resource title.

This avoids the common mistake of attempting to render the entire knowledge graph in
the browser.

## Accessibility and responsive layout

The app uses semantic headings, tables for predicate/object facts, labels on search
inputs, and browser-native controls. Fixed-format UI such as graph canvas and tables
has stable sizing so dynamic RDF values do not shift the whole page.

## Adding a route

1. Add a route module under `apps/web/src/routes`.
2. Add the pathname to `apps/web/src/app/router.ts`.
3. Add a navigation item to `packages/content/src/site-content.ts` if it should appear
   in the header.
4. Put shared domain logic in `packages/core` or `apps/web/src/services`, not directly
   in the route.
5. Add a focused test when the route introduces new parsing or data-shaping behavior.
