export type SupportedLanguage = "en" | "am" | "de";

export type LocalizedText = Readonly<Record<SupportedLanguage, string>>;

export interface NavItem {
  readonly label: LocalizedText;
  readonly href: string;
}

export interface ResourceLink {
  readonly title: LocalizedText;
  readonly description: LocalizedText;
  readonly href: string;
  readonly image?: string;
}

export interface ChapterMetric {
  readonly label: LocalizedText;
  readonly value: string;
  readonly detail: LocalizedText;
  readonly tone?: "primary" | "accent" | "warm";
}

export interface QueryExample {
  readonly title: LocalizedText;
  readonly description: LocalizedText;
  readonly query: string;
}

export interface Contributor {
  readonly name: string;
  readonly year: string;
  readonly role: LocalizedText;
  readonly href: string;
}

export interface TeamMember {
  readonly name: string;
  readonly role: LocalizedText;
  readonly affiliation: string;
  readonly href?: string;
}

export interface ResearchHighlight {
  readonly title: LocalizedText;
  readonly body: LocalizedText;
}

export interface NewsLink {
  readonly label: LocalizedText;
  readonly href: string;
}

export interface NewsItem {
  readonly title: LocalizedText;
  readonly summary: LocalizedText;
  readonly category: LocalizedText;
  readonly publishedAt: string;
  readonly href: string;
  readonly actionLabel?: LocalizedText;
  readonly links?: readonly NewsLink[];
}

export interface MappingStatistic {
  readonly label: string;
  readonly percentage: string;
  readonly count: string;
  readonly description: string;
}

export interface DatasetArtifact {
  readonly name: string;
  readonly type: "raw" | "mapping-based" | "metadata";
  readonly description: string;
}
