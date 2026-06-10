import type { AppLayout } from "../../app/layout";
import { navigate } from "../../app/router";

export function renderResourceSearch(layout: AppLayout): HTMLElement {
  const form = document.createElement("form");
  form.className = "resource-search";
  form.setAttribute("role", "search");

  const label = document.createElement("label");
  label.htmlFor = "resource-title";
  label.textContent = "Resource title or IRI";

  const input = document.createElement("input");
  input.id = "resource-title";
  input.name = "resource";
  input.type = "search";
  input.placeholder = "ወርቁ_ማሞ";
  input.autocomplete = "off";

  const button = document.createElement("button");
  button.type = "submit";
  button.textContent = "Open";

  form.append(label, input, button);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const value = input.value.trim();
    if (!value) return;
    void navigate(`/resource/${encodeURIComponent(value)}`, layout);
  });

  return form;
}
