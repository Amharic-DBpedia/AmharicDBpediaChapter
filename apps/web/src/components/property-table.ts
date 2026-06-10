import type { RdfTerm, ResourceFact } from "@amdb/core";
import { localName } from "@amdb/core";
import { externalLink } from "../dom/html";

export function renderPropertyTable(facts: readonly ResourceFact[]): HTMLTableElement {
  const table = document.createElement("table");
  table.className = "property-table";

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  for (const heading of ["Property", "Value"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = heading;
    headRow.append(th);
  }
  thead.append(headRow);

  const tbody = document.createElement("tbody");
  for (const fact of facts) {
    const row = document.createElement("tr");
    const property = document.createElement("th");
    property.scope = "row";
    property.append(externalLink(fact.predicate, fact.predicateLabel));

    const value = document.createElement("td");
    value.append(renderTerm(fact.object));

    row.append(property, value);
    tbody.append(row);
  }

  table.append(thead, tbody);
  return table;
}

function renderTerm(term: RdfTerm): Node {
  if (term.termType === "NamedNode") {
    const isImage = /\.(jpg|jpeg|png|gif|svg|webp)(\?.*)?$/i.test(term.value);
    if (!isImage) return externalLink(term.value, localName(term.value));

    const link = externalLink(term.value, "");
    const image = document.createElement("img");
    image.src = term.value;
    image.alt = localName(term.value);
    image.loading = "lazy";
    image.className = "inline-resource-image";
    link.append(image);
    return link;
  }

  const span = document.createElement("span");
  span.textContent =
    term.termType === "Literal" && term.language ? `${term.value} (${term.language})` : term.value;
  return span;
}
