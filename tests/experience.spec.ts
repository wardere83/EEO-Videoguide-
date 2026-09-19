import { test, expect } from "@playwright/test";
test("public routes, resource filtering, video, and portal destination", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    "Opportunity for everyone",
  );
  await expect(
    page.getByRole("link", { name: "Open dashboard", exact: true }),
  ).toHaveAttribute("href", "https://eeo.bulleconsulting.com");
  const homeVideo = page.locator("video");
  await expect(homeVideo).toHaveJSProperty("muted", true);
  await expect(homeVideo).toHaveJSProperty("loop", true);
  await expect(homeVideo).toHaveJSProperty("controls", false);
  await expect.poll(() => homeVideo.evaluate((v) => v.paused)).toBe(false);
  await page
    .getByRole("navigation", { name: "Main navigation" })
    .getByRole("link", { name: "Resources", exact: true })
    .click();
  await page.getByLabel("Search resources").fill("dashboard");
  await expect(page.locator(".resource-grid article")).toHaveCount(1);
  await page.getByLabel("Search resources").fill("no match possible");
  await expect(page.getByText("No matching resources.")).toBeVisible();
  await page.getByRole("button", { name: "Clear filters" }).click();
  await expect(page.locator(".resource-grid article")).toHaveCount(4);
  await page.getByRole("button", { name: "Training", exact: true }).click();
  await page.getByRole("link", { name: "View the overview" }).click();
  await expect(page.locator('video source[type="video/mp4"]')).toHaveAttribute(
    "src",
    /eeo-initiative.mp4/,
  );
  await page.reload();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "EEO IBP Initiative",
  );
  await page.goto("/#/missing");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Page not found.",
  );
  expect(errors).toEqual([]);
});
test("desktop and mobile layout and navigation", async ({ page }) => {
  for (const width of [1440, 390, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto("/");
    await expect(page.locator(".logo").first()).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBe(true);
    if (width < 760) {
      await page.getByRole("button", { name: "Open navigation" }).click();
      await page
        .getByRole("navigation", { name: "Main navigation" })
        .getByRole("link", { name: "Resources", exact: true })
        .click();
      await expect(page.getByLabel("Search resources")).toBeVisible();
      await expect(
        page.getByRole("button", { name: "Open navigation" }),
      ).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
      ).toBe(true);
    }
  }
  await page.setViewportSize({ width: 1440, height: 1050 });
  await page.goto("/");
  await page.screenshot({ path: "/tmp/eeo-desktop.png", fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: "/tmp/eeo-mobile.png", fullPage: true });
});

test("initiative priorities, district award graph, and funding story are interactive", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("link", { name: "Grantees", exact: true }),
  ).toHaveCount(0);
  await expect(page.locator(".award-column")).toHaveCount(11);
  await expect(page.locator(".award-column img")).toHaveCount(11);
  expect(
    await page.locator(".award-column img").evaluateAll((images) =>
      images.every((image) => (image as HTMLImageElement).naturalWidth > 0),
    ),
  ).toBe(true);
  await expect(page.getByRole("button", { name: /Allan Hancock.*\$100,000/ })).toBeVisible();
  await page.getByRole("button", { name: /North Orange County.*\$150,000/ }).click();
  await expect(page.locator("#district-award-detail")).toContainText("North Orange County CCD");
  await expect(page.locator("#district-award-detail")).toContainText("$150,000");
  await expect(page.locator("#district-award-detail")).toContainText("Project");
  await expect(page.locator("#district-award-detail")).toContainText("Intended impact");
  await expect(page.locator("#district-award-detail")).toContainText("student perspective");
  await page.getByRole("button", { name: "Belonging", exact: true }).click();
  await expect(page.locator("#priority-description")).toContainText(
    "connected, valued",
  );
  await page.getByRole("button", { name: "Growth", exact: true }).click();
  await expect(page.locator("#priority-description")).toContainText(
    "mentorship",
  );
  await expect(
    page
      .getByRole("navigation", { name: "Main navigation" })
      .getByRole("link", { name: "Film", exact: true }),
  ).toHaveCount(0);
  await page.goto("/#/video");
  await expect(page.locator("video")).toHaveJSProperty("duration", 64);
  await expect(page.locator("video")).toHaveJSProperty("controls", false);
  await page
    .getByRole("button", { name: /05 Combined impact/ })
    .click();
  await expect
    .poll(async () =>
      page.locator("video").evaluate((v: HTMLVideoElement) => v.currentTime),
    )
    .toBeGreaterThanOrEqual(33);
  await expect(page.locator("video")).toHaveJSProperty("paused", false);
  await page.getByRole("tab", { name: /2026–28 \$1.4M/ }).click();
  await expect(page.getByRole("tabpanel")).toContainText("11 district awards");
  await expect(page.getByRole("tabpanel")).toContainText("$1.4M");
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "One connected view of the work." })).toBeVisible();
  await page.getByRole("button", { name: "District B", exact: true }).click();
  await expect(page.locator(".app-greeting")).toContainText("District B");
  await page.getByRole("button", { name: "Show Book an SME" }).click();
  await expect(page.locator(".demo-scene")).toContainText("Book an SME");
  await expect(page.locator(".demo-scene")).toContainText("View availability");
  await page.goto("/#/video");
  await page.getByText("Read transcript", { exact: true }).click();
  await expect(page.locator(".transcript")).toContainText(
    "West Valley-Mission CCD",
  );
});
