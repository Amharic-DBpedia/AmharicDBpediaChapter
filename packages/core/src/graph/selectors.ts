import type { ResourceSummary } from "../rdf/terms";
import { compactIri } from "../util/iri";
import type { GraphEdge, GraphNode } from "./model";

export interface EgoGraph {
  readonly nodes: readonly GraphNode[];
  readonly edges: readonly GraphEdge[];
}

export function resourceToEgoGraph(resource: ResourceSummary, maxEdges = 24): EgoGraph {
  const nodes = new Map<string, GraphNode>();
  const edges: GraphEdge[] = [];

  nodes.set(resource.iri, {
    id: resource.iri,
    label: resource.label,
    kind: "resource",
  });

  for (const fact of resource.facts) {
    if (edges.length >= maxEdges) break;
    if (fact.object.termType !== "NamedNode") continue;

    nodes.set(fact.object.value, {
      id: fact.object.value,
      label: compactIri(fact.object.value),
      kind: "resource",
    });
    edges.push({
      id: `${resource.iri}-${fact.predicate}-${fact.object.value}`,
      from: resource.iri,
      to: fact.object.value,
      predicate: fact.predicate,
      predicateLabel: fact.predicateLabel,
    });
  }

  return { nodes: [...nodes.values()], edges };
}
