import type { SupportedLanguage } from "@amdb/core";

const STORAGE_KEY = "amdb-preferred-language";
const supportedLanguages = new Set<SupportedLanguage>(["en", "am", "de"]);

export function getPreferredLanguage(): SupportedLanguage {
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored && supportedLanguages.has(stored as SupportedLanguage)) {
    return stored as SupportedLanguage;
  }
  return "en";
}

export function setPreferredLanguage(language: SupportedLanguage): void {
  window.localStorage.setItem(STORAGE_KEY, language);
}
