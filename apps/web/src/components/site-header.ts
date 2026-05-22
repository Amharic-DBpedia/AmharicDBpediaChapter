import type { LocalizedText } from "@amdb/content";
import { languages, type NavItem } from "@amdb/content";
import type { SupportedLanguage } from "@amdb/core";

interface SiteHeaderProps {
  readonly navigation: readonly NavItem[];
  readonly language: SupportedLanguage;
  readonly onLanguageChange: (language: SupportedLanguage) => void;
  readonly localize: (value: LocalizedText) => string;
}

export function renderSiteHeader(props: SiteHeaderProps): HTMLElement {
  const header = document.createElement("header");
  header.className = "site-header";

  const inner = document.createElement("div");
  inner.className = "site-header__inner";

  const brand = document.createElement("a");
  brand.href = "/";
  brand.className = "brand";
  const logo = document.createElement("img");
  logo.src = "/assets/images/dbpedia_am_logo.png";
  logo.alt = "";
  logo.width = 34;
  logo.height = 34;
  const brandText = document.createElement("span");
  brandText.textContent = "Amharic DBpedia";
  brand.append(logo, brandText);

  const nav = document.createElement("nav");
  nav.className = "site-nav";
  nav.setAttribute("aria-label", "Primary");

  for (const item of props.navigation) {
    const link = document.createElement("a");
    link.href = item.href;
    link.textContent = props.localize(item.label);
    nav.append(link);
  }

  const language = document.createElement("select");
  language.className = "language-select";
  language.ariaLabel = "Language";
  for (const [code, label] of Object.entries(languages)) {
    const option = document.createElement("option");
    option.value = code;
    option.textContent = label;
    option.selected = code === props.language;
    language.append(option);
  }
  language.addEventListener("change", () => {
    props.onLanguageChange(language.value as SupportedLanguage);
  });

  inner.append(brand, nav, language);
  header.append(inner);
  return header;
}
