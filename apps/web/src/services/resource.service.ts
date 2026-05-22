import {
  bindingToTerm,
  compactIri,
  dbpediaResourceIri,
  describeResourceQuery,
  type Iri,
  localName,
  type ResourceFact,
  type ResourceSummary,
  resourceFactsQuery,
  toIri,
} from "@amdb/core";
import { env } from "../app/env";
import { describe, select } from "./sparql.service";

const LABEL_PREDICATES = new Set([
  "http://www.w3.org/2000/01/rdf-schema#label",
  "http://xmlns.com/foaf/0.1/name",
]);
const DESCRIPTION_PREDICATES = new Set([
  "http://dbpedia.org/ontology/abstract",
  "http://www.w3.org/2000/01/rdf-schema#comment",
]);
const TYPE_PREDICATE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type";

export async function loadResourceSummary(
  titleOrIri: string,
  signal?: AbortSignal,
): Promise<ResourceSummary> {
  const iri = dbpediaResourceIri(titleOrIri, env.resourceBase);
  const results = await select(env.sparqlEndpoint, resourceFactsQuery(iri), signal);
  const facts: ResourceFact[] = [];
  const types: Iri[] = [];
  let label = localName(iri);
  let description: string | undefined;
  let image: Iri | undefined;

  for (const row of results.results.bindings) {
    const predicateBinding = row.predicate;
    const objectBinding = row.object;
    if (!predicateBinding || predicateBinding.type !== "uri" || !objectBinding) continue;

    const predicate = toIri(predicateBinding.value);
    const object = bindingToTerm(objectBinding);
    const fact: ResourceFact = {
      predicate,
      predicateLabel: compactIri(predicate),
      object,
    };
    facts.push(fact);

    if (LABEL_PREDICATES.has(predicate) && object.termType === "Literal") {
      label = object.value;
    }
    if (!description && DESCRIPTION_PREDICATES.has(predicate) && object.termType === "Literal") {
      description = object.value;
    }
    if (predicate === TYPE_PREDICATE && object.termType === "NamedNode") {
      types.push(object.value);
    }
    if (!image && object.termType === "NamedNode" && isImageIri(object.value)) {
      image = object.value;
    }
  }

  return {
    iri,
    label,
    ...(description ? { description } : {}),
    ...(image ? { image } : {}),
    types,
    facts,
  };
}

export function loadRawResource(
  iri: Iri,
  format: "turtle" | "jsonld",
  signal?: AbortSignal,
): Promise<string> {
  return describe(
    env.sparqlEndpoint,
    describeResourceQuery(iri),
    format === "turtle" ? "text/turtle" : "application/ld+json",
    signal,
  );
}

function isImageIri(iri: string): boolean {
  return /\.(jpg|jpeg|png|gif|svg|webp)(\?.*)?$/i.test(iri);
}
