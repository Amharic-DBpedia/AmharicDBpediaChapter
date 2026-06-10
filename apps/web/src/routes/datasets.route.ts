import { datasetArtifacts } from "@amdb/content";
import { AMHARIC_DATABUS_COLLECTION } from "@amdb/core";
import type { AppLayout } from "../app/layout";
import { clear, externalLink } from "../dom/html";

export function renderDatasets(layout: AppLayout): void {
  clear(layout.main);

  const section = document.createElement("section");
  section.className = "page-section";
  const title = document.createElement("h1");
  title.textContent = "Datasets and releases";
  const intro = document.createElement("p");
  intro.className = "lead";
  intro.textContent =
    "Generated RDF dumps remain data-release artifacts. The web app links to Databus and uses the public SPARQL endpoint instead of bundling dump files into the browser.";

  const list = document.createElement("ul");
  list.className = "dataset-list";
  for (const artifact of datasetArtifacts) {
    const item = document.createElement("li");
    const name = document.createElement("strong");
    name.textContent = artifact.name;
    const badge = document.createElement("span");
    badge.className = `dataset-badge dataset-badge--${artifact.type}`;
    badge.textContent = artifact.type;
    const description = document.createElement("p");
    description.textContent = artifact.description;
    item.append(name, badge, description);
    list.append(item);
  }

  const action = document.createElement("p");
  action.append(externalLink(AMHARIC_DATABUS_COLLECTION, "Open Amharic Databus collection"));

  section.append(title, intro, list, action);
  layout.main.append(section);
}
