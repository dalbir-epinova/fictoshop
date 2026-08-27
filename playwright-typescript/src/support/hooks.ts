import fs from "node:fs/promises";
import path from "node:path";
import { After, Before, Status, setDefaultTimeout } from "@cucumber/cucumber";
import { chromium } from "@playwright/test";
import { settings } from "./settings.js";
import type { FictoshopWorld } from "./world.js";

setDefaultTimeout(60_000);

async function clearCart(): Promise<void> {
  const response = await fetch(`${settings.baseUrl}/cart`, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(`Could not clear cart: ${response.status} ${response.statusText}`);
  }
}

Before(async function (this: FictoshopWorld) {
  this.snapshot = await this.data.snapshot();
  this.browser = await chromium.launch({ headless: !settings.headed });
  this.context = await this.browser.newContext({
    baseURL: settings.baseUrl,
    viewport: { width: 1440, height: 900 }
  });
  this.page = await this.context.newPage();
  this.page.setDefaultTimeout(settings.timeout);
  this.page.setDefaultNavigationTimeout(settings.timeout);
  await clearCart();
});

After(async function (this: FictoshopWorld, scenario) {
  try {
    if (scenario.result?.status === Status.FAILED && this.page) {
      const artifactDirectory = path.join(process.cwd(), "artifacts");
      await fs.mkdir(artifactDirectory, { recursive: true });
      const safeName = scenario.pickle.name.replace(/[^a-zA-Z0-9._ -]/g, "_");
      const screenshot = await this.page.screenshot({
        path: path.join(artifactDirectory, `${safeName}.png`),
        fullPage: true
      });
      await this.attach(screenshot, "image/png");
    }
  } finally {
    try {
      await clearCart();
      if (this.snapshot) {
        await this.data.cleanup(this.snapshot);
      }
    } finally {
      await this.context?.close();
      await this.browser?.close();
    }
  }
});
