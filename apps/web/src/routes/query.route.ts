import { queryExamples } from "@amdb/content";
import { pickLocalized } from "@amdb/core";
import { env } from "../app/env";
import type { AppLayout } from "../app/layout";
import { clear, externalLink } from "../dom/html";
import { select } from "../services/sparql.service";

export function renderQuery(layout: AppLayout): void {
  clear(layout.main);
  const language = layout.getLanguage();

  const section = document.createElement("section");
  section.className = "page-section";
  const title = document.createElement("h1");
  title.textContent = "Amharic SPARQL endpoint";
  const intro = document.createElement("p");
  intro.className = "lead";
  intro.textContent =
    "A dedicated chapter query surface for the Amharic DBpedia endpoint. It mirrors the chapter pattern used by other DBpedia language editions while keeping queries bounded and readable.";

  const endpointPanel = document.createElement("section");
  endpointPanel.className = "endpoint-panel";
  const endpointTitle = document.createElement("h2");
  endpointTitle.textContent = "Endpoint";
  const endpoint = document.createElement("code");
  endpoint.textContent = env.sparqlEndpoint;
  const endpointCopy = document.createElement("p");
  endpointCopy.textContent =
    "Production deployments can expose this as /sparql through Virtuoso or a thin proxy, just like language-specific DBpedia chapters such as Hindi DBpedia.";
  endpointPanel.append(
    endpointTitle,
    endpoint,
    endpointCopy,
    externalLink(env.sparqlUi, "Open Tentris in a new tab"),
  );

  const tentris = document.createElement("section");
  tentris.className = "tentris-workspace";
  const tentrisHeader = document.createElement("div");
  tentrisHeader.className = "tentris-workspace__header";
  const tentrisCopy = document.createElement("div");
  const tentrisEyebrow = document.createElement("p");
  tentrisEyebrow.className = "eyebrow";
  tentrisEyebrow.textContent = "Public knowledge graph";
  const tentrisTitle = document.createElement("h2");
  tentrisTitle.textContent = "Tentris query workspace";
  const tentrisDescription = document.createElement("p");
  tentrisDescription.textContent =
    "Explore, compose, and run queries directly against the Amharic DBpedia endpoint.";
  tentrisCopy.append(tentrisEyebrow, tentrisTitle, tentrisDescription);
  const tentrisExternal = externalLink(env.sparqlUi, "Open in new tab");
  tentrisExternal.className = "button-link";
  tentrisHeader.append(tentrisCopy, tentrisExternal);

  const tentrisFrame = document.createElement("iframe");
  tentrisFrame.className = "tentris-frame";
  tentrisFrame.src = env.sparqlUi;
  tentrisFrame.title = "Amharic DBpedia Tentris query interface";
  tentrisFrame.loading = "eager";
  tentrisFrame.referrerPolicy = "no-referrer";
  tentrisFrame.setAttribute("allow", "clipboard-read; clipboard-write");

  const tentrisFallback = document.createElement("p");
  tentrisFallback.className = "tentris-workspace__fallback";
  tentrisFallback.append(
    "If the query workspace does not load, ",
    externalLink(env.sparqlUi, "open Tentris directly"),
    ".",
  );
  tentris.append(tentrisHeader, tentrisFrame, tentrisFallback);

  const workbench = document.createElement("section");
  workbench.className = "sparql-workbench";
  const workbenchTitle = document.createElement("h2");
  workbenchTitle.textContent = "Run a bounded SELECT query";
  const textarea = document.createElement("textarea");
  textarea.value = queryExamples[1]?.query ?? "SELECT ?s WHERE { ?s ?p ?o . } LIMIT 10";
  textarea.spellcheck = false;
  textarea.ariaLabel = "SPARQL query";
  const controls = document.createElement("div");
  controls.className = "query-controls";
  const run = document.createElement("button");
  run.type = "button";
  run.textContent = "Run query";
  const status = document.createElement("span");
  status.className = "status";
  controls.append(run, status);
  const results = document.createElement("div");
  results.className = "query-results";
  run.addEventListener("click", () => {
    void runQuery(textarea.value, status, results);
  });
  workbench.append(workbenchTitle, textarea, controls, results);

  section.append(title, intro, endpointPanel, tentris, workbench);

  for (const example of queryExamples) {
    const article = document.createElement("article");
    article.className = "query-example";
    const heading = document.createElement("h2");
    heading.textContent = pickLocalized(example.title, language) ?? "";
    const description = document.createElement("p");
    description.textContent = pickLocalized(example.description, language) ?? "";
    const pre = document.createElement("pre");
    const code = document.createElement("code");
    code.textContent = example.query;
    pre.append(code);
    const load = document.createElement("button");
    load.type = "button";
    load.textContent = "Load example";
    load.addEventListener("click", () => {
      textarea.value = example.query;
      textarea.focus();
    });
    article.append(heading, description, pre, load);
    section.append(article);
  }

  layout.main.append(section);
}

async function runQuery(query: string, status: HTMLElement, mount: HTMLElement): Promise<void> {
  clear(mount);
  if (!/\blimit\s+\d+/i.test(query)) {
    status.textContent = "Add a LIMIT before running public endpoint queries.";
    status.className = "status status--error";
    return;
  }

  status.textContent = "Running query...";
  status.className = "status";

  try {
    const data = await select(env.sparqlEndpoint, query);
    status.textContent = `${data.results.bindings.length} rows returned`;
    mount.append(renderResultsTable(data.head.vars, data.results.bindings));
  } catch (error) {
    status.textContent = error instanceof Error ? error.message : "Query failed";
    status.className = "status status--error";
  }
}

function renderResultsTable(
  vars: readonly string[],
  rows: readonly Record<string, { readonly value: string } | undefined>[],
): HTMLTableElement {
  const table = document.createElement("table");
  table.className = "stats-table query-table";

  const thead = document.createElement("thead");
  const header = document.createElement("tr");
  for (const variable of vars) {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = variable;
    header.append(th);
  }
  thead.append(header);

  const tbody = document.createElement("tbody");
  for (const row of rows) {
    const tr = document.createElement("tr");
    for (const variable of vars) {
      const td = document.createElement("td");
      td.textContent = row[variable]?.value ?? "";
      tr.append(td);
    }
    tbody.append(tr);
  }

  table.append(thead, tbody);
  return table;
}
