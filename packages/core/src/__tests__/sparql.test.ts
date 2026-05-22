import { describe, expect, it } from "vitest";
import { resourceFactsQuery, toIri } from "../index";

describe("SPARQL query builders", () => {
  it("builds a bounded resource facts query", () => {
    const query = resourceFactsQuery(toIri("http://am.dbpedia.org/resource/ደብረ_ብርሃን"), 25);

    expect(query).toContain("<http://am.dbpedia.org/resource/ደብረ_ብርሃን>");
    expect(query).toContain("LIMIT 25");
  });
});
