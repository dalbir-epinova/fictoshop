import assert from "node:assert/strict";
import { expect, type Locator, type Page } from "@playwright/test";
import { settings } from "../support/settings.js";

export class CartPage {
  private readonly cart: Locator;
  lastCartResponseStatus?: number;

  constructor(private readonly page: Page) {
    this.cart = page.locator("#cart");
  }

  get cartItems(): Locator {
    return this.page.locator("#cart-items .cart-item");
  }

  productCard(name: string): Locator {
    return this.page.locator(".product-card").filter({ hasText: name });
  }

  cartLine(name: string): Locator {
    return this.cartItems.filter({ hasText: name });
  }

  async open(): Promise<void> {
    await this.page.goto(settings.baseUrl);
    await expect(this.page.locator("#product-grid")).toHaveAttribute("aria-busy", "false");
  }

  async addProduct(name: string, quantity = 1): Promise<void> {
    let card = this.productCard(name);
    if (await card.count() === 0) {
      await this.open();
      card = this.productCard(name);
    }
    await expect(card).toHaveCount(1);
    const input = card.locator(".quantity-input");
    await input.fill(String(quantity));
    await input.dispatchEvent("change");
    await card.getByRole("button", { name: "Add to cart", exact: true }).click();
    await expect(this.page.locator("#app-toast")).toContainText(`Added ${quantity}`);
    await expect(this.page.locator("#app-toast")).toContainText(name);
    await expect(this.cartLine(name)).toBeVisible();
  }

  async selectQuantity(name: string, quantity: number): Promise<void> {
    const input = this.productCard(name).locator(".quantity-input");
    await input.fill(String(quantity));
    await input.dispatchEvent("change");
    await expect(input).toHaveValue(String(quantity));
  }

  async addSelectedProduct(name: string): Promise<void> {
    const card = this.productCard(name);
    const quantity = Number(await card.locator(".quantity-input").inputValue());
    await card.getByRole("button", { name: "Add to cart", exact: true }).click();
    await expect(this.page.locator("#app-toast")).toContainText(`Added ${quantity}`);
    await expect(this.cartLine(name)).toBeVisible();
  }

  expectHidden(): Promise<void> { return expect(this.cart).toBeHidden(); }
  expectVisible(): Promise<void> { return expect(this.cart).toBeVisible(); }
  expectProductInCart(name: string): Promise<void> { return expect(this.cartLine(name)).toBeVisible(); }
  expectProductNotInCart(name: string): Promise<void> { return expect(this.cartLine(name)).toHaveCount(0); }
  expectTotalItems(quantity: number): Promise<void> { return expect(this.page.locator("#cart-total-items")).toHaveText(String(quantity)); }
  expectGrandTotal(total: number): Promise<void> { return expect(this.page.locator("#cart-grand-total")).toHaveText(`$${total.toFixed(2)}`); }
  expectLineQuantity(name: string, quantity: number): Promise<void> { return expect(this.cartLine(name).locator(".muted")).toContainText(`${quantity} `); }
  expectOneLine(name: string): Promise<void> { return expect(this.cartLine(name)).toHaveCount(1); }
  scroll(): Promise<unknown> { return this.page.evaluate(() => window.scrollTo(0, document.body.scrollHeight)); }

  async expectInsideViewport(): Promise<void> {
    const box = await this.cart.boundingBox();
    const viewport = this.page.viewportSize();
    assert.ok(box && viewport);
    assert.ok(box.x >= 0 && box.y >= 0);
    assert.ok(box.x + box.width <= viewport.width);
    assert.ok(box.y + box.height <= viewport.height);
  }

  async removeProduct(name: string): Promise<void> {
    const line = this.cartLine(name);
    await line.getByRole("button", { name: "Remove", exact: true }).click();
    await expect(line).toHaveCount(0);
  }

  async clear(): Promise<void> {
    await this.page.getByRole("button", { name: "Clear", exact: true }).click();
    await this.expectHidden();
  }

  async reload(): Promise<void> {
    await this.page.reload();
    await expect(this.page.locator("#product-grid")).toHaveAttribute("aria-busy", "false");
  }

  async attemptOverStock(name: string, stock: number): Promise<void> {
    const card = this.productCard(name);
    const attempted = String(stock + 1);
    await card.locator(".quantity-input").evaluate((element: HTMLInputElement, value) => {
      element.max = String(value);
      element.value = String(value);
    }, attempted);
    const responsePromise = this.page.waitForResponse((response) => response.url().replace(/\/$/, "").endsWith("/cart") && response.request().method() === "POST");
    await card.getByRole("button", { name: "Add to cart", exact: true }).click();
    this.lastCartResponseStatus = (await responsePromise).status();
  }

  expectRequestRejected(): void { assert.equal(this.lastCartResponseStatus, 400); }
  expectStockError(stock: number, name: string): Promise<void> { return expect(this.page.locator("#cart-message")).toHaveText(`Only ${stock} units left of ${name}`); }
  expectCatalogStock(name: string, stock: number): Promise<void> { return expect(this.productCard(name).locator(".badge")).toHaveText(`${stock} in stock`); }
}
