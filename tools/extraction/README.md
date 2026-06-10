# Amharic DBpedia Extraction Tooling Boundary

This folder documents the operational side of the Amharic DBpedia chapter. It is not
part of the Vite browser app.

## Expected flow

1. Download or prepare the Amharic Wikimedia dump.
2. Run the DBpedia Extraction Framework with Amharic mappings and ontology files.
3. Generate mapping statistics from `infobox-properties.ttl`.
4. Validate representative RDF outputs.
5. Publish release artifacts to Databus.
6. Load the Databus collection into a SPARQL endpoint.
7. Update website metrics and links after validation.

## Scripts

The scripts in `tools/extraction/scripts` are placeholders for the chapter's operational
automation. They intentionally fail fast until environment-specific commands are
provided.

Keep credentials, server names, and private deployment paths out of this repository.
