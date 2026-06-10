import type { LangTag } from "../rdf/terms";

export type SupportedLanguage = "en" | "am" | "de";

export function toLangTag(value: string): LangTag {
  if (!/^[a-z]{2,3}(-[a-z0-9]+)*$/i.test(value)) {
    throw new Error(`Invalid language tag: ${value}`);
  }
  return value as LangTag;
}

export function pickLocalized<T>(
  localized: Partial<Record<SupportedLanguage, T>>,
  preferred: SupportedLanguage,
): T | undefined {
  return localized[preferred] ?? localized.en ?? localized.am ?? localized.de;
}
