import { AMHARIC_SPARQL_ENDPOINT, AMHARIC_TENTRIS_UI } from "@amdb/core";

export const env = {
  sparqlEndpoint: import.meta.env.VITE_AMDB_SPARQL_ENDPOINT ?? AMHARIC_SPARQL_ENDPOINT,
  sparqlUi: import.meta.env.VITE_AMDB_SPARQL_UI ?? AMHARIC_TENTRIS_UI,
  resourceBase: import.meta.env.VITE_AMDB_RESOURCE_BASE ?? "http://am.dbpedia.org/resource/",
} as const;
