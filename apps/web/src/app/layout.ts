import { navigation } from "@amdb/content";
import { pickLocalized, type SupportedLanguage } from "@amdb/core";
import { renderSiteHeader } from "../components/site-header";
import { clear } from "../dom/html";

export interface AppLayout {
  readonly main: HTMLElement;
  readonly setLanguage: (language: SupportedLanguage) => void;
  readonly getLanguage: () => SupportedLanguage;
}

export function createLayout(
  root: HTMLElement,
  initialLanguage: SupportedLanguage,
  onLanguageChange: (language: SupportedLanguage) => void,
): AppLayout {
  let language = initialLanguage;

  const shell = document.createElement("div");
  shell.className = "site-shell";

  const main = document.createElement("main");
  main.id = "main";
  main.tabIndex = -1;

  const footer = document.createElement("footer");
  footer.className = "site-footer";
  const footerInner = document.createElement("div");
  footerInner.className = "site-footer__inner";
  footerInner.textContent = "Amharic DBpedia Chapter";
  footer.append(footerInner);

  function renderHeader(): void {
    const header = renderSiteHeader({
      navigation,
      language,
      onLanguageChange: (next) => {
        language = next;
        renderHeader();
        onLanguageChange(next);
      },
      localize: (value) => pickLocalized(value, language) ?? "",
    });

    const existing = shell.querySelector(".site-header");
    if (existing) existing.replaceWith(header);
    else shell.prepend(header);
  }

  clear(root);
  shell.append(main, footer);
  root.append(shell);
  renderHeader();

  return {
    main,
    setLanguage(next) {
      language = next;
      renderHeader();
    },
    getLanguage() {
      return language;
    },
  };
}
