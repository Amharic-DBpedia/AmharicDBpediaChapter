import { compactIri, type Iri, resourceToEgoGraph } from "@amdb/core";
import type { AppLayout } from "../app/layout";
import { renderPropertyTable } from "../components/property-table";
import { clear, externalLink } from "../dom/html";
import { renderEgoGraph } from "../features/graph/ego-graph";
import { renderResourceSearch } from "../features/search/resource-search";
import { loadRawResource, loadResourceSummary } from "../services/resource.service";

let activeController: AbortController | undefined;

export async function renderResource(layout: AppLayout, title: string): Promise<void> {
  activeController?.abort();
  activeController = new AbortController();

  clear(layout.main);
  const section = document.createElement("section");
  section.className = "page-section resource-page";
  const heading = document.createElement("h1");
  heading.textContent = "Resource viewer";
  const intro = document.createElement("p");
  intro.className = "lead";
  intro.textContent =
    "Open an Amharic DBpedia resource by title or IRI. Titles are preserved as Unicode IRIs so Amharic names are not double-encoded.";
  const loading = document.createElement("p");
  loading.className = "status";
  loading.textContent = "Loading resource facts...";
  section.append(heading, intro, renderResourceSearch(layout), loading);
  layout.main.append(section);

  try {
    const resource = await loadResourceSummary(title, activeController.signal);
    clear(section);

    const header = document.createElement("div");
    header.className = "resource-header";
    if (resource.image) {
      const image = document.createElement("img");
      image.className = "resource-hero-image";
      image.src = resource.image;
      image.alt = resource.label;
      header.append(image);
    }
    const titleNode = document.createElement("h1");
    titleNode.textContent = resource.label;
    const iri = document.createElement("p");
    iri.className = "resource-iri";
    iri.append(externalLink(resource.iri, resource.iri));
    header.append(titleNode, iri);

    if (resource.description) {
      const description = document.createElement("p");
      description.className = "lead";
      description.textContent = resource.description;
      header.append(description);
    }

    const rawActions = document.createElement("div");
    rawActions.className = "raw-actions";
    for (const [format, label] of [
      ["turtle", "Turtle"],
      ["jsonld", "JSON-LD"],
    ] as const) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label;
      button.addEventListener("click", () => {
        void showRaw(section, resource.iri, format);
      });
      rawActions.append(button);
    }
    header.append(rawActions);

    const typeLine = document.createElement("p");
    typeLine.className = "resource-types";
    typeLine.textContent =
      resource.types.length > 0
        ? `Types: ${resource.types.map((type) => compactIri(type)).join(", ")}`
        : "Types: not returned by this query";

    const summaryCards = document.createElement("div");
    summaryCards.className = "resource-summary-grid";
    for (const [label, value] of [
      ["Facts", String(resource.facts.length)],
      ["Types", String(resource.types.length)],
      ["Graph edges", String(resourceToEgoGraph(resource).edges.length)],
    ] as const) {
      const card = document.createElement("article");
      card.className = "resource-summary-card";
      const strong = document.createElement("strong");
      strong.textContent = value;
      const span = document.createElement("span");
      span.textContent = label;
      card.append(strong, span);
      summaryCards.append(card);
    }

    const graphModel = resourceToEgoGraph(resource);
    const graph = renderEgoGraph(graphModel, resource.iri);
    const table =
      resource.facts.length > 0 ? renderPropertyTable(resource.facts) : renderNoFacts(resource.iri);

    section.append(header, summaryCards, typeLine, graph, table);
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") return;
    loading.textContent = error instanceof Error ? error.message : "Failed to load resource";
    loading.className = "status status--error";
  }
}

function renderNoFacts(iri: string): HTMLElement {
  const panel = document.createElement("section");
  panel.className = "empty-state";
  const title = document.createElement("h2");
  title.textContent = "No triples returned";
  const body = document.createElement("p");
  body.textContent =
    "The endpoint did not return facts for this IRI. This usually means the article is not in the loaded release, the title differs, or the resource has not been extracted yet.";
  const code = document.createElement("code");
  code.textContent = iri;
  const examples = document.createElement("p");
  examples.textContent = "Try known extracted resources such as ዳኛቸው_ወርቁ or አስናቀች_ወርቁ.";
  panel.append(title, body, code, examples);
  return panel;
}

async function showRaw(section: HTMLElement, iri: Iri, format: "turtle" | "jsonld"): Promise<void> {
  const existing = section.querySelector(".raw-panel");
  existing?.remove();

  const panel = document.createElement("section");
  panel.className = "raw-panel";
  const title = document.createElement("h2");
  title.textContent = `Raw ${format === "turtle" ? "Turtle" : "JSON-LD"}`;
  const pre = document.createElement("pre");
  pre.textContent = "Loading raw RDF...";
  panel.append(title, pre);
  section.prepend(panel);

  try {
    const raw = await loadRawResource(iri, format);
    pre.textContent =
      raw.trim().length > 0
        ? format === "jsonld"
          ? prettyJson(raw)
          : raw
        : `No ${format === "turtle" ? "Turtle" : "JSON-LD"} returned for ${iri}`;
  } catch (error) {
    pre.textContent = error instanceof Error ? error.message : "Failed to load raw RDF";
  }
}

function prettyJson(raw: string): string {
  try {
    return JSON.stringify(JSON.parse(raw), null, 2);
  } catch {
    return raw;
  }
}
