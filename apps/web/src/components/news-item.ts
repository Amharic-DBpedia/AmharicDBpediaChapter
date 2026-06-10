import type { NewsItem } from "@amdb/content";
import { pickLocalized, type SupportedLanguage } from "@amdb/core";

export type NewsItemVariant = "preview" | "featured" | "archive";

export function renderNewsItem(
  item: NewsItem,
  language: SupportedLanguage,
  variant: NewsItemVariant = "preview",
): HTMLElement {
  const article = document.createElement("article");
  article.className = `news-item news-item--${variant}`;

  const meta = document.createElement("div");
  meta.className = "news-item__meta";
  const category = document.createElement("span");
  category.className = "news-item__category";
  category.textContent = pickLocalized(item.category, language) ?? "";
  const published = document.createElement("time");
  published.dateTime = item.publishedAt;
  published.textContent = formatNewsDate(item.publishedAt, language);
  meta.append(category, published);

  const title = document.createElement(variant === "featured" ? "h2" : "h3");
  const link = document.createElement("a");
  link.href = item.href;
  link.textContent = pickLocalized(item.title, language) ?? "";
  title.append(link);

  const summary = document.createElement("p");
  summary.textContent = pickLocalized(item.summary, language) ?? "";

  const relatedLinks = document.createElement("div");
  relatedLinks.className = "news-item__links";
  if (variant !== "preview") {
    for (const related of item.links ?? []) {
      const relatedLink = document.createElement("a");
      relatedLink.href = related.href;
      relatedLink.textContent = pickLocalized(related.label, language) ?? "";
      relatedLinks.append(relatedLink);
    }
  }

  const action = document.createElement("a");
  action.className = "news-item__action";
  action.href = item.href;
  action.textContent = item.actionLabel
    ? (pickLocalized(item.actionLabel, language) ?? "Read related update")
    : "Read related update";

  article.append(meta, title, summary);
  if (relatedLinks.childElementCount > 0) {
    article.append(relatedLinks);
  }
  article.append(action);
  return article;
}

function formatNewsDate(value: string, language: SupportedLanguage): string {
  const locale = language === "am" ? "am-ET" : language === "de" ? "de-DE" : "en-US";
  return new Intl.DateTimeFormat(locale, {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}
