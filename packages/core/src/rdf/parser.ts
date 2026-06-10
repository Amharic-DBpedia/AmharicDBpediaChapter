import { Parser, Store } from "n3";

export function parseTurtle(turtle: string): Store {
  const parser = new Parser({ format: "text/turtle" });
  return new Store(parser.parse(turtle));
}

export function labelsForSubject(turtle: string, subjectIri: string): readonly string[] {
  const store = parseTurtle(turtle);
  return store
    .getQuads(subjectIri, "http://www.w3.org/2000/01/rdf-schema#label", null, null)
    .map((quad) => quad.object.value);
}
