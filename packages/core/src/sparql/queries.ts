import type { Iri } from "../rdf/terms";

export const AMHARIC_SPARQL_ENDPOINT = "https://am.dbpedia.data.dice-research.org/sparql";
export const AMHARIC_TENTRIS_UI = "https://am.dbpedia.data.dice-research.org/ui";
export const AMHARIC_DATABUS_COLLECTION =
  "https://databus.dbpedia.org/purplebee/collections/am_chapter/";
export const AMHARIC_MAPPING_NAMESPACE = "https://mappings.dbpedia.org/index.php/Mapping_am";

export function describeResourceQuery(iri: Iri): string {
  return `DESCRIBE <${iri}>`;
}

export function resourceFactsQuery(iri: Iri, limit = 1000): string {
  return `
SELECT DISTINCT ?predicate ?object WHERE {
  <${iri}> ?predicate ?object .
}
LIMIT ${limit}
`.trim();
}

export function resourceLabelsQuery(search: string, limit = 10): string {
  const escaped = search.replaceAll("\\", "\\\\").replaceAll('"', '\\"');
  return `
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?resource ?label WHERE {
  ?resource rdfs:label ?label .
  FILTER(lang(?label) = "am")
  FILTER(CONTAINS(LCASE(STR(?label)), LCASE("${escaped}")))
}
LIMIT ${limit}
`.trim();
}

export function sampleResourcesQuery(limit = 10): string {
  return `
SELECT DISTINCT ?resource WHERE {
  ?resource ?predicate ?object .
}
LIMIT ${limit}
`.trim();
}
