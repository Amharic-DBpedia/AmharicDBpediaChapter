import type { AppLayout } from "../app/layout";
import { clear, externalLink } from "../dom/html";

export function renderDocs(layout: AppLayout): void {
  clear(layout.main);

  const section = document.createElement("section");
  section.className = "page-section";
  const title = document.createElement("h1");
  title.textContent = "Implementation documentation";
  const intro = document.createElement("p");
  intro.textContent =
    "The refactor keeps DBpedia extraction as an upstream data pipeline and implements the chapter-facing product in vanilla TypeScript.";

  const docs = [
    ["Architecture", "/docs/architecture.md"],
    ["RDF pipeline", "/docs/rdf-pipeline.md"],
    ["Frontend implementation", "/docs/frontend-implementation.md"],
    ["Contributor guide", "/docs/contributor-guide.md"],
  ] as const;

  const list = document.createElement("ul");
  list.className = "doc-list";
  for (const [label, href] of docs) {
    const item = document.createElement("li");
    item.append(externalLink(href, label));
    list.append(item);
  }

  section.append(title, intro, list);
  layout.main.append(section);
}
