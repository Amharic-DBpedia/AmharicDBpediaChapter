import { chapterMetrics, mappingStatistics, researchHighlights } from "@amdb/content";
import { pickLocalized } from "@amdb/core";
import type { AppLayout } from "../app/layout";
import { clear } from "../dom/html";

export function renderStatistics(layout: AppLayout): void {
  clear(layout.main);
  const language = layout.getLanguage();

  const section = document.createElement("section");
  section.className = "page-section";
  const title = document.createElement("h1");
  title.textContent = "Chapter statistics";
  const intro = document.createElement("p");
  intro.className = "lead";
  intro.textContent =
    "The research paper and GSoC documentation report the current mapping and extraction baseline for the Amharic chapter.";

  const metrics = document.createElement("div");
  metrics.className = "metric-grid metric-grid--wide";
  for (const metric of chapterMetrics) {
    const article = document.createElement("article");
    article.className = `metric metric--${metric.tone ?? "primary"}`;
    const value = document.createElement("strong");
    value.textContent = metric.value;
    const label = document.createElement("span");
    label.textContent = pickLocalized(metric.label, language) ?? "";
    const detail = document.createElement("p");
    detail.textContent = pickLocalized(metric.detail, language) ?? "";
    article.append(value, label, detail);
    metrics.append(article);
  }

  const table = document.createElement("table");
  table.className = "stats-table";
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  for (const heading of ["Statistic", "Coverage", "Count", "Meaning"]) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = heading;
    headerRow.append(th);
  }
  thead.append(headerRow);
  const tbody = document.createElement("tbody");
  for (const stat of mappingStatistics) {
    const row = document.createElement("tr");
    for (const value of [stat.label, stat.percentage, stat.count, stat.description]) {
      const cell = document.createElement(value === stat.label ? "th" : "td");
      if (cell instanceof HTMLTableCellElement && value === stat.label) cell.scope = "row";
      cell.textContent = value;
      row.append(cell);
    }
    tbody.append(row);
  }
  table.append(thead, tbody);

  const highlights = document.createElement("div");
  highlights.className = "insight-grid";
  const heading = document.createElement("h2");
  heading.textContent = "Research implementation notes";
  highlights.append(heading);
  for (const item of researchHighlights) {
    const card = document.createElement("article");
    card.className = "insight-card";
    const cardTitle = document.createElement("h3");
    cardTitle.textContent = pickLocalized(item.title, language) ?? "";
    const cardBody = document.createElement("p");
    cardBody.textContent = pickLocalized(item.body, language) ?? "";
    card.append(cardTitle, cardBody);
    highlights.append(card);
  }

  section.append(title, intro, metrics, table, highlights);
  layout.main.append(section);
}
