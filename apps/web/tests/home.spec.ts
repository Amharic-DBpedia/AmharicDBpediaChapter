import { expect, test } from "@playwright/test";

test("renders chapter homepage and resource search", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Amharic DBpedia Chapter" })).toBeVisible();
  await expect(page.getByLabel("Resource title or IRI")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Latest news" })).toBeVisible();
  await expect(page.locator(".news-item")).toHaveCount(3);
  await expect(page.getByRole("link", { name: "News", exact: true })).toBeVisible();
});

test("renders a dedicated news destination from the primary navigation", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "News", exact: true }).click();

  await expect(page).toHaveURL(/\/news$/);
  await expect(page.getByRole("heading", { name: "News and project updates" })).toBeVisible();
  await expect(page.getByText("Latest update")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Earlier updates" })).toBeVisible();
});

test("embeds Tentris inside the SPARQL page", async ({ page }) => {
  await page.goto("/sparql");

  await expect(page.getByRole("heading", { name: "Tentris query workspace" })).toBeVisible();
  await expect(page.getByTitle("Amharic DBpedia Tentris query interface")).toHaveAttribute(
    "src",
    "https://am.dbpedia.data.dice-research.org/ui",
  );
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
