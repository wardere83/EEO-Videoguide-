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
  await page.getByLabel("Search resources").fill("NOVA");
  await expect(page.locator(".resource-grid article")).toHaveCount(1);
  await page.getByLabel("Search resources").fill("no match possible");
  await expect(page.getByText("No matching resources.")).toBeVisible();
  await page.getByRole("button", { name: "Clear filters" }).click();
  await expect(page.locator(".resource-grid article")).toHaveCount(5);
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

test("initiative priorities and film chapters work without a district directory", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("link", { name: "Grantees", exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByText("Allan Hancock Joint CCD", { exact: true }),
  ).toHaveCount(0);
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
  await expect(page.locator("video")).toHaveJSProperty("duration", 100);
  await page
    .getByRole("button", { name: "A shared future", exact: true })
    .click();
  await expect
    .poll(async () =>
      page.locator("video").evaluate((v: HTMLVideoElement) => v.currentTime),
    )
    .toBeGreaterThanOrEqual(70);
  await expect(page.locator("video")).toHaveJSProperty("paused", false);
  await page.getByText("Read transcript", { exact: true }).click();
  await expect(page.locator(".film-chapters details")).toContainText(
    "West Valley-Mission CCD",
  );
});
