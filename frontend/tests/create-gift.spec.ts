// ABOUTME: End-to-end tests for gift creation.
// ABOUTME: Runs authenticated through the storage state saved by auth.setup.ts.

import { expect, test } from "@playwright/test"

test.describe("Gift Creation", () => {
  test("Authenticated user can create a gift", async ({ page }) => {
    await page.goto("/create-gift")

    await page.getByLabel("Name").fill("Birthday Present")
    await page.getByLabel("Approximate Price").fill("50.00")
    await page.getByRole("button", { name: "Create Gift" }).click()

    await expect(page.getByText("Gift created successfully.")).toBeVisible()
  })

  test("Authenticated user can create a gift with an image", async ({ page }) => {
    await page.goto("/create-gift")

    await page.getByLabel("Name").fill("Gift with photo")
    await page.getByLabel("Approximate Price").fill("25.00")
    await page
      .getByLabel("Gift Image")
      .setInputFiles("tests/assets/test_image.png")
    await page.getByRole("button", { name: "Create Gift" }).click()

    await expect(page.getByText("Gift created successfully.")).toBeVisible()
  })
})
