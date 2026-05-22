import { describe, expect, it } from "vitest";
import { compactIri, dbpediaResourceIri, localName } from "../index";

describe("IRI helpers", () => {
  it("creates Amharic DBpedia resource IRIs from titles", () => {
    expect(dbpediaResourceIri("ደብረ ብርሃን")).toBe("http://am.dbpedia.org/resource/ደብረ_ብርሃን");
  });

  it("decodes route encoded Amharic titles once", () => {
    expect(dbpediaResourceIri("%E1%8B%88%E1%88%AD%E1%89%81_%E1%88%9B%E1%88%9E")).toBe(
      "http://am.dbpedia.org/resource/ወርቁ_ማሞ",
    );
  });

  it("keeps readable labels for encoded IRI segments", () => {
    expect(localName("%E1%8B%B0%E1%89%A5%E1%88%A8_%E1%89%A5%E1%88%AD%E1%88%83%E1%8A%95")).toBe(
      "ደብረ ብርሃን",
    );
  });

  it("compacts known DBpedia namespaces", () => {
    expect(compactIri("http://dbpedia.org/ontology/birthDate")).toBe("dbo:birthDate");
  });
});
