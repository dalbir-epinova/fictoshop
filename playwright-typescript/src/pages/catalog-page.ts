import assert from "node:assert/strict";
import { expect, type Locator, type Page } from "@playwright/test";
import type { ProductRecord } from "../support/models.js";
import { settings } from "../support/settings.js";

export class CatalogPage {
  constructor(private readonly page: Page) {}

  get productCards(): Locator {
    return this.page.locator(".product-card");
  }

  productCard(name: string): Locator {
    return this.productCards.filter({
      has: this.page.getByRole("heading", { name, exact: true })
    });
  }

  async open(): Promise<void> {
    await this.page.goto(settings.baseUrl);
    await this.waitForCatalog();
  }

  async expectOpen(): Promise<void> {
    await expect(this.page).toHaveURL(`${settings.baseUrl}/`);
  }

  async expectHeadingAndCatalog(): Promise<void> {
    await this.waitForCatalog();
    await expect(this.page.getByRole("heading", { name: "Welcome to FictoShop", exact: true })).toBeVisible();
    await expect(this.page.locator("#catalog")).toBeVisible();
    assert.ok((await this.productCards.count()) > 0);
  }

  async expectCardsHavePurchasingInformation(): Promise<void> {
    await this.waitForCatalog();
    const count = await this.productCards.count();
    assert.ok(count > 0);
    for (let index = 0; index < count; index += 1) {
      const card = this.productCards.nth(index);
      await expect(card.locator("h3")).not.toHaveText("");
      await expect(card.locator(".product-price")).toContainText("$");
      await expect(card.locator(".badge")).toBeVisible();
    }
  }

  expectAvailableAddEnabled(name: string): Promise<void> {
    return expect(this.productCard(name).getByRole("button", { name: "Add to cart", exact: true })).toBeEnabled();
  }

  openProduct(name: string): Promise<void> {
    return this.productCard(name).locator(".product-card-title").click();
  }

  async expectProductDetail(product: ProductRecord): Promise<void> {
    await expect(this.page).toHaveURL(new RegExp(`/products/${product.id}/view$`));
    await expect(this.page.getByRole("heading", { name: product.name, exact: true })).toBeVisible();
    await expect(this.page.getByText(product.description, { exact: true })).toBeVisible();
    await expect(this.page.locator(".product-detail-price")).toContainText(`$${product.price.toFixed(2)}`);
    await expect(this.page.locator(".product-detail-rating")).toBeVisible();
    await expect(this.page.locator("#reviews")).toBeVisible();
  }

  search(query: string): Promise<void> {
    return this.page.locator("#product-search").fill(query);
  }

  async expectOnlyProduct(name: string): Promise<void> {
    await expect(this.productCards).toHaveCount(1);
    await expect(this.productCards.first().locator("h3")).toHaveText(name);
  }

  expectCatalogStatus(matches: number, total: number): Promise<void> {
    return expect(this.page.locator("#product-status")).toContainText(`Showing ${matches} of ${total}`);
  }

  async expectNoProducts(): Promise<void> {
    await expect(this.productCards).toHaveCount(0);
    await expect(this.page.locator("#product-empty")).toBeVisible();
  }

  clearSearch(): Promise<void> {
    return this.search("");
  }

  expectProductCount(count: number): Promise<void> {
    return expect(this.productCards).toHaveCount(count);
  }

  selectSort(label: string): Promise<string[]> {
    return this.page.locator("#product-sort").selectOption({ label });
  }

  async displayedPrices(): Promise<number[]> {
    return (await this.productCards.locator(".product-price").allTextContents())
      .map((value) => Number(value.replace("$", "").replaceAll(",", "")));
  }

  async displayedStocks(): Promise<number[]> {
    const result: number[] = [];
    for (let index = 0; index < await this.productCards.count(); index += 1) {
      result.push(Number(await this.productCards.nth(index).locator(".quantity-input").getAttribute("max") ?? 0));
    }
    return result;
  }

  enableInStockOnly(): Promise<void> {
    return this.page.locator("#product-in-stock").check();
  }

  expectProductHidden(name: string): Promise<void> {
    return expect(this.productCard(name)).toHaveCount(0);
  }

  async expectOutOfStockControls(name: string): Promise<void> {
    const card = this.productCard(name);
    await expect(card.locator(".badge")).toHaveText("Out of stock");
    await expect(card.locator(".quantity-input")).toBeDisabled();
    await expect(card.locator(".quantity-btn").first()).toBeDisabled();
    await expect(card.locator(".quantity-btn").last()).toBeDisabled();
    await expect(card.getByRole("button", { name: "Add to cart", exact: true })).toBeDisabled();
  }

  decreaseInitialQuantity(name: string): Promise<void> {
    return this.productCard(name).locator(".quantity-btn").first().click();
  }

  expectQuantity(name: string, quantity: number): Promise<void> {
    return expect(this.productCard(name).locator(".quantity-input")).toHaveValue(String(quantity));
  }

  async increaseBeyondStock(name: string, stock: number): Promise<void> {
    const plus = this.productCard(name).locator(".quantity-btn").last();
    for (let index = 0; index < stock + 2; index += 1) {
      await plus.click();
    }
  }

  exploreApi(): Promise<void> {
    return this.page.getByRole("link", { name: "Explore the API", exact: true }).click();
  }

  expectProductsEndpoint(): Promise<void> {
    return expect(this.page).toHaveURL(`${settings.baseUrl}/products`);
  }

  async expectApiCatalogProducts(): Promise<void> {
    assert.match(await this.page.locator("body").innerText(), /name/);
  }

  expectSignedInUser(username: string): Promise<void> {
    return expect(this.page.locator(".nav-user")).toHaveText(`Signed in as ${username}`);
  }

  expectLogoutButton(): Promise<void> {
    return expect(this.page.locator("header").getByRole("button", { name: "Log out", exact: true })).toBeVisible();
  }

  expectProductVisible(name: string): Promise<void> {
    return expect(this.productCard(name)).toBeVisible();
  }

  expectProductStock(name: string, stock: number): Promise<void> {
    return expect(this.productCard(name).locator(".badge")).toHaveText(`${stock} in stock`);
  }

  async expectProductImage(name: string): Promise<void> {
    const image = this.productCard(name).getByRole("img", { name: `${name} photo` });
    await image.scrollIntoViewIfNeeded();
    await expect(image).toBeVisible();
    await expect(image).toHaveAttribute("src", /\/images\/uploads\//);
    await expect(image).toHaveJSProperty("complete", true, { timeout: 15_000 });
    assert.equal(await image.evaluate((element: HTMLImageElement) => element.naturalWidth > 0), true);
  }

  private waitForCatalog(): Promise<void> {
    return expect(this.page.locator("#product-grid")).toHaveAttribute("aria-busy", "false");
  }
}
