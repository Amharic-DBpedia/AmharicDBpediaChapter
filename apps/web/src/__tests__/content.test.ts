import { navigation, newsItems } from "@amdb/content";
import { describe, expect, it } from "vitest";

describe("web content", () => {
  it("exposes the resource viewer route", () => {
    expect(navigation.map((item) => item.href)).toContain("/resource/ደብረ_ብርሃን");
  });

  it("exposes news as a primary navigation destination", () => {
    expect(navigation.map((item) => item.href)).toContain("/news");
  });

  it("publishes chapter news in reverse chronological order", () => {
    expect(newsItems.length).toBeGreaterThanOrEqual(3);
    expect(newsItems.map((item) => item.publishedAt)).toEqual(
      [...newsItems]
        .map((item) => item.publishedAt)
        .sort()
        .reverse(),
    );
  });

  it("features the real LREC 2026 Amharic DBpedia paper announcement", () => {
    const [latest] = newsItems;

    expect(latest?.title.en).toContain("LREC 2026");
    expect(latest?.href).toBe("https://lrec.elra.info/lrec2026-main-627");
    expect(latest?.links?.map((link) => link.href)).toContain(
      "https://github.com/Amharic-DBpedia/",
    );
  });
});
