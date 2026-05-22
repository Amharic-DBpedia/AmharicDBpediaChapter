import { expect, test } from "@playwright/test";

test("renders chapter homepage and resource search", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Amharic DBpedia Chapter" })).toBeVisible();
  await expect(page.getByLabel("Resource title or IRI")).toBeVisible();
});

test("resource route keeps Amharic titles readable when endpoint has no triples", async ({
  page,
}) => {
  await page.route("**/sparql?**", async (route) => {
    await route.fulfill({
      contentType: "application/sparql-results+json",
      body: JSON.stringify({ head: { vars: ["predicate", "object"] }, results: { bindings: [] } }),
    });
  });

  await page.goto("/resource/ወርቁ_ማሞ");

  await expect(
    page.getByRole("link", { name: "http://am.dbpedia.org/resource/ወርቁ_ማሞ" }),
  ).toBeVisible();
  await expect(page.getByText("No triples returned")).toBeVisible();
  await expect(page.getByText("%25E1")).toHaveCount(0);
});
