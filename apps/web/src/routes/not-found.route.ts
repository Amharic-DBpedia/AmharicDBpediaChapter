import type { AppLayout } from "../app/layout";
import { clear } from "../dom/html";

export function renderNotFound(layout: AppLayout): void {
  clear(layout.main);
  const section = document.createElement("section");
  section.className = "page-section";
  const title = document.createElement("h1");
  title.textContent = "Page not found";
  const link = document.createElement("a");
  link.href = "/";
  link.textContent = "Return home";
  section.append(title, link);
  layout.main.append(section);
}
