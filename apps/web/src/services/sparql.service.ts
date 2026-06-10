import { isSparqlSelectResults, type SparqlSelectResults } from "@amdb/core";

export async function select(
  endpoint: string,
  query: string,
  signal?: AbortSignal,
): Promise<SparqlSelectResults> {
  const url = new URL(endpoint);
  url.searchParams.set("query", query);
  url.searchParams.set("format", "application/sparql-results+json");

  const response = await fetch(url, {
    method: "GET",
    headers: {
      accept: "application/sparql-results+json",
    },
    ...(signal ? { signal } : {}),
  });

  if (!response.ok) {
    throw new Error(`SPARQL request failed: ${response.status} ${response.statusText}`);
  }

  const body: unknown = await response.json();
  if (!isSparqlSelectResults(body)) {
    throw new Error("SPARQL endpoint returned an unexpected SELECT result shape");
  }

  return body;
}

export async function describe(
  endpoint: string,
  query: string,
  accept: "text/turtle" | "application/ld+json",
  signal?: AbortSignal,
): Promise<string> {
  const url = new URL(endpoint);
  url.searchParams.set("query", query);
  url.searchParams.set("format", accept);

  const response = await fetch(url, {
    method: "GET",
    headers: { accept },
    ...(signal ? { signal } : {}),
  });

  if (!response.ok) {
    throw new Error(`DESCRIBE request failed: ${response.status} ${response.statusText}`);
  }

  return response.text();
}
