import { navigation } from "@amdb/content";
import { describe, expect, it } from "vitest";

describe("web content", () => {
  it("exposes the resource viewer route", () => {
    expect(navigation.map((item) => item.href)).toContain("/resource/ደብረ_ብርሃን");
  });
});
