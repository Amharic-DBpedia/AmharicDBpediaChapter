import { literal, namedNode, type RdfTerm } from "../rdf/terms";
import { toIri } from "../util/iri";
import { toLangTag } from "../util/lang";

export interface SparqlJsonBinding {
  readonly type: "uri" | "literal" | "bnode";
  readonly value: string;
  readonly datatype?: string;
  readonly "xml:lang"?: string;
}

export interface SparqlSelectResults {
  readonly head: { readonly vars: readonly string[] };
  readonly results: {
    readonly bindings: readonly Record<string, SparqlJsonBinding | undefined>[];
  };
}

export function isSparqlSelectResults(value: unknown): value is SparqlSelectResults {
  if (!value || typeof value !== "object") return false;
  const candidate = value as SparqlSelectResults;
  return Array.isArray(candidate.head?.vars) && Array.isArray(candidate.results?.bindings);
}

export function bindingToTerm(binding: SparqlJsonBinding): RdfTerm {
  if (binding.type === "uri") return namedNode(toIri(binding.value));
  if (binding.type === "bnode") return { termType: "BlankNode", value: binding.value };
  return literal(
    binding.value,
    binding["xml:lang"] ? toLangTag(binding["xml:lang"]) : undefined,
    binding.datatype ? toIri(binding.datatype) : undefined,
  );
}
