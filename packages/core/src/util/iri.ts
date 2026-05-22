import type { Iri } from "../rdf/terms";

const IRI_PATTERN = /^[a-z][a-z0-9+.-]*:/i;

export function isIri(value: string): value is Iri {
  return IRI_PATTERN.test(value);
}

export function toIri(value: string): Iri {
  if (!isIri(value)) {
    throw new Error(`Expected absolute IRI, received: ${value}`);
  }
  return value as Iri;
}

export function dbpediaResourceIri(
  titleOrIri: string,
  base = "http://am.dbpedia.org/resource/",
): Iri {
  const value = decodeURIComponentSafe(titleOrIri.trim());
  if (isIri(value)) return toIri(value);
  const normalized = value.replaceAll(" ", "_");
  return toIri(`${base}${normalized}`);
}

export function localName(iri: string): string {
  const fragment = iri.includes("#") ? iri.split("#").at(-1) : undefined;
  const path = fragment ?? iri.split("/").at(-1) ?? iri;
  try {
    return decodeURIComponent(path).replaceAll("_", " ");
  } catch {
    return path.replaceAll("_", " ");
  }
}

function decodeURIComponentSafe(value: string): string {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

export function compactIri(iri: string): string {
  const prefixes: readonly [string, string][] = [
    ["http://dbpedia.org/ontology/", "dbo:"],
    ["http://dbpedia.org/property/", "dbp:"],
    ["http://am.dbpedia.org/property/", "amdbp:"],
    ["http://am.dbpedia.org/resource/", "am:"],
    ["http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:"],
    ["http://www.w3.org/2000/01/rdf-schema#", "rdfs:"],
    ["http://xmlns.com/foaf/0.1/", "foaf:"],
  ];

  for (const [prefix, label] of prefixes) {
    if (iri.startsWith(prefix)) return `${label}${localName(iri.slice(prefix.length))}`;
  }

  return localName(iri);
}
