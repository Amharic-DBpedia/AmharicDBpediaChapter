export type Iri = string & { readonly __brand: "iri" };
export type LangTag = string & { readonly __brand: "lang" };

export interface NamedNodeTerm {
  readonly termType: "NamedNode";
  readonly value: Iri;
}

export interface BlankNodeTerm {
  readonly termType: "BlankNode";
  readonly value: string;
}

export interface LiteralTerm {
  readonly termType: "Literal";
  readonly value: string;
  readonly language?: LangTag;
  readonly datatype?: Iri;
}

export type RdfTerm = NamedNodeTerm | BlankNodeTerm | LiteralTerm;

export interface RdfQuad {
  readonly subject: NamedNodeTerm | BlankNodeTerm;
  readonly predicate: NamedNodeTerm;
  readonly object: RdfTerm;
  readonly graph?: NamedNodeTerm | BlankNodeTerm;
}

export interface ResourceFact {
  readonly predicate: Iri;
  readonly predicateLabel: string;
  readonly object: RdfTerm;
}

export interface ResourceSummary {
  readonly iri: Iri;
  readonly label: string;
  readonly description?: string;
  readonly image?: Iri;
  readonly types: readonly Iri[];
  readonly facts: readonly ResourceFact[];
}

export function namedNode(value: Iri): NamedNodeTerm {
  return { termType: "NamedNode", value };
}

export function blankNode(value: string): BlankNodeTerm {
  return { termType: "BlankNode", value };
}

export function literal(value: string, language?: LangTag, datatype?: Iri): LiteralTerm {
  return {
    termType: "Literal",
    value,
    ...(language ? { language } : {}),
    ...(datatype ? { datatype } : {}),
  };
}
