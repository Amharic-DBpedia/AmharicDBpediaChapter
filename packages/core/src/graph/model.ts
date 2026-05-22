import type { Iri } from "../rdf/terms";

export interface GraphNode {
  readonly id: Iri;
  readonly label: string;
  readonly kind: "resource" | "literal";
}

export interface GraphEdge {
  readonly id: string;
  readonly from: Iri;
  readonly to: Iri;
  readonly predicate: Iri;
  readonly predicateLabel: string;
}
