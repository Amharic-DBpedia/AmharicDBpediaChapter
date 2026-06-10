import { newsItems } from "@amdb/content";
import type { AppLayout } from "../app/layout";
import { renderNewsItem } from "../components/news-item";
import { clear } from "../dom/html";

export function renderNews(layout: AppLayout): void {
  clear(layout.main);
  const language = layout.getLanguage();
  const [featured, ...archiveItems] = newsItems;

  const section = document.createElement("section");
  section.className = "page-section news-page";

  const header = document.createElement("header");
  header.className = "news-page__header";
  const eyebrow = document.createElement("p");
  eyebrow.className = "eyebrow";
  eyebrow.textContent = "Amharic DBpedia Chapter";
  const title = document.createElement("h1");
  title.textContent = "News and project updates";
  const intro = document.createElement("p");
  intro.className = "lead";
  intro.textContent =
    "Follow extraction releases, engineering milestones, research progress, and new ways to explore the Amharic knowledge graph.";
  header.append(eyebrow, title, intro);

  if (featured) {
    const featuredSection = document.createElement("section");
    featuredSection.className = "news-feature";
    const featuredLabel = document.createElement("p");
    featuredLabel.className = "news-section-label";
    featuredLabel.textContent = "Latest update";
    featuredSection.append(featuredLabel, renderNewsItem(featured, language, "featured"));
    section.append(header, featuredSection);
  } else {
    section.append(header);
  }

  const archive = document.createElement("section");
  archive.className = "news-archive";
  const archiveHeader = document.createElement("div");
  archiveHeader.className = "news-archive__header";
  const archiveTitle = document.createElement("h2");
  archiveTitle.textContent = "Earlier updates";
  const archiveCount = document.createElement("span");
  archiveCount.textContent = `${archiveItems.length} published updates`;
  archiveHeader.append(archiveTitle, archiveCount);

  const archiveList = document.createElement("div");
  archiveList.className = "news-archive__list";
  for (const item of archiveItems) {
    archiveList.append(renderNewsItem(item, language, "archive"));
  }
  archive.append(archiveHeader, archiveList);
  section.append(archive);

  layout.main.append(section);
}
