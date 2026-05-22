import { contributors, teamMembers } from "@amdb/content";
import { pickLocalized } from "@amdb/core";
import type { AppLayout } from "../app/layout";
import { clear, externalLink } from "../dom/html";

export function renderTeam(layout: AppLayout): void {
  clear(layout.main);
  const language = layout.getLanguage();

  const section = document.createElement("section");
  section.className = "page-section";
  const title = document.createElement("h1");
  title.textContent = "Team";
  const intro = document.createElement("p");
  intro.className = "lead";
  intro.textContent =
    "Mentors, researchers, and GSoC contributors behind the Amharic DBpedia chapter and research release.";

  const grid = document.createElement("div");
  grid.className = "team-grid";
  for (const member of teamMembers) {
    const card = document.createElement("article");
    card.className = "team-card";
    const avatar = document.createElement("div");
    avatar.className = "team-card__avatar";
    avatar.textContent = initials(member.name);
    const name = document.createElement("h2");
    name.textContent = member.name;
    const role = document.createElement("p");
    role.className = "team-card__role";
    role.textContent = pickLocalized(member.role, language) ?? "";
    const affiliation = document.createElement("p");
    affiliation.textContent = member.affiliation;
    card.append(avatar, name, role, affiliation);
    if (member.href) card.append(externalLink(member.href, "Profile"));
    grid.append(card);
  }

  const gsoc = document.createElement("section");
  gsoc.className = "people-strip";
  const gsocTitle = document.createElement("h2");
  gsocTitle.textContent = "GSoC project contributors";
  gsoc.append(gsocTitle);
  for (const contributor of contributors) {
    gsoc.append(
      externalLink(
        contributor.href,
        `${contributor.name} · ${contributor.year} · ${
          pickLocalized(contributor.role, language) ?? ""
        }`,
      ),
    );
  }

  section.append(title, intro, grid, gsoc);
  layout.main.append(section);
}

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}
