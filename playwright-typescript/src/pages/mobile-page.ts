import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { expect, type Locator, type Page, type Route } from "@playwright/test";
import { projectPaths } from "../support/project-paths.js";

export class MobilePage {
  requestedUrls: string[] = [];
  configuredIosBase = "";

  constructor(private readonly page: Page) {}

  setViewport(width: number, height: number): Promise<void> { return this.page.setViewportSize({ width, height }); }

  async expectStorefrontFits(): Promise<void> {
    const heading = this.page.getByRole("heading", { name: "Welcome to FictoShop" });
    const catalog = this.page.locator("#catalog");
    await expect(heading).toBeVisible();
    await expect(catalog).toBeVisible();
    await this.expectInsideDocumentWidth(heading);
    await this.expectInsideDocumentWidth(catalog);
  }

  async expectPrimaryControlsUsable(): Promise<void> {
    assert.equal(await this.page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
    for (const control of [
      this.page.getByRole("link", { name: "Shop the catalog" }),
      this.page.getByLabel("Search catalog"),
      this.page.getByLabel("Sort by")
    ]) {
      await expect(control).toBeVisible();
      await expect(control).toBeEnabled();
      await this.expectInsideDocumentWidth(control);
    }
  }

  async expectCartWidthInsideViewport(): Promise<void> {
    await this.page.evaluate(() => window.scrollTo(0, window.scrollY));
    const cart = this.page.locator("#cart");
    await expect(cart).toBeVisible();
    await this.expectInsideDocumentWidth(cart);
  }

  async expectCartLinesScrollable(): Promise<void> {
    const items = this.page.locator("#cart-items");
    const overflow = await items.evaluate((element) => getComputedStyle(element).overflowY);
    const maxHeight = await items.evaluate((element) => getComputedStyle(element).maxHeight);
    assert.ok(["auto", "scroll"].includes(overflow));
    assert.notEqual(maxHeight, "none");
  }

  async expectCartActionsUsable(): Promise<void> {
    for (const name of ["Clear", "Checkout"]) {
      const button = this.page.getByRole("button", { name, exact: true });
      await expect(button).toBeVisible();
      await expect(button).toBeEnabled();
      await this.expectInsideDocumentWidth(button);
    }
  }

  async expectCheckoutSingleColumn(): Promise<void> {
    const columns = await this.page.locator(".shipping-form").evaluate((element) => getComputedStyle(element).gridTemplateColumns);
    assert.equal(columns.split(" ").length, 1, `Expected one column, got ${columns}`);
  }

  async expectCheckoutActionsUsable(): Promise<void> {
    for (const control of [
      this.page.getByRole("link", { name: "Back to cart", exact: true }),
      this.page.getByRole("button", { name: "Place order", exact: true })
    ]) {
      await expect(control).toBeVisible();
      await this.expectInsideDocumentWidth(control);
    }
  }

  async loadAndroidBundle(): Promise<void> {
    const index = path.join(projectPaths.root, "android-app/app/src/main/assets/index.html");
    await this.page.route("http://10.0.2.2:8000/**", (route) => this.bundleRoute(route));
    await this.page.goto(pathToFileURL(index).toString());
    await expect(this.page.locator("#product-grid")).toHaveAttribute("aria-busy", "false");
  }

  expectAndroidHostBase(): void {
    assert.ok(this.requestedUrls.some((url) => url.startsWith("http://10.0.2.2:8000/products")));
  }

  async loadIosBundle(): Promise<void> {
    const plist = await fs.readFile(path.join(projectPaths.root, "ios-app/fictoshop/Info.plist"), "utf8");
    const swift = await fs.readFile(path.join(projectPaths.root, "ios-app/fictoshop/fictoshop/WebView.swift"), "utf8");
    const project = await fs.readFile(path.join(projectPaths.root, "ios-app/fictoshop/fictoshop.xcodeproj/project.pbxproj"), "utf8");
    assert.match(plist, /<key>API_BASE_URL<\/key>/);
    assert.match(swift, /object\(forInfoDictionaryKey: "API_BASE_URL"\)/);
    const match = project.match(/API_BASE_URL = "([^"]+)";/);
    assert.ok(match, "API_BASE_URL is not configured in the Xcode project");
    this.configuredIosBase = match[1].replace(/\/$/, "");
    await this.page.addInitScript((base) => { (window as Window & { __FICTO_API_BASE__?: string }).__FICTO_API_BASE__ = base; }, this.configuredIosBase);
    await this.page.route(`${this.configuredIosBase}/**`, (route) => this.bundleRoute(route));
    await this.page.goto(pathToFileURL(path.join(projectPaths.root, "mobile-web/index.html")).toString());
    await expect(this.page.locator("#product-grid")).toHaveAttribute("aria-busy", "false");
  }

  expectIosConfiguredBase(): void {
    assert.ok(this.requestedUrls.some((url) => url.startsWith(`${this.configuredIosBase}/products`)));
  }

  expectBundleProduct(): Promise<void> {
    return expect(this.page.locator(".product-card").filter({ hasText: "Bundled mobile product" })).toBeVisible();
  }

  private async bundleRoute(route: Route): Promise<void> {
    const url = route.request().url();
    this.requestedUrls.push(url);
    if (url.endsWith("/products")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([{ id: 9001, name: "Bundled mobile product", description: "Product returned to a mobile bundle test.", price: 19.95, in_stock: 5, image_url: "", average_rating: null, review_count: 0 }])
      });
    } else if (url.endsWith("/cart")) {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [], total_items: 0, grand_total: 0 }) });
    } else {
      await route.continue();
    }
  }

  private async expectInsideDocumentWidth(locator: Locator): Promise<void> {
    const box = await locator.boundingBox();
    const viewport = this.page.viewportSize();
    assert.ok(box && viewport);
    const metrics = await this.page.evaluate(() => ({ innerWidth, visualWidth: visualViewport?.width ?? innerWidth }));
    const gutter = Math.max(0, metrics.innerWidth - metrics.visualWidth);
    assert.ok(box.x >= -gutter, `Element starts outside viewport: ${JSON.stringify(box)}`);
    assert.ok(box.x + box.width <= viewport.width, `Element ends outside viewport: ${JSON.stringify(box)}`);
  }
}
