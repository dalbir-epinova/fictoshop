import assert from "node:assert/strict";
import { expect, type Browser, type Page } from "@playwright/test";
import type { OrderItemRecord } from "../support/models.js";
import { settings } from "../support/settings.js";

const fieldIds: Record<string, string> = {
  "Full name": "#id_full_name",
  Email: "#id_email",
  Phone: "#id_phone",
  Address: "#id_address",
  "Postal code": "#id_postal_code",
  City: "#id_city",
  Country: "#id_country"
};

export class CheckoutPage {
  orderId?: number;

  constructor(private readonly page: Page) {}

  open(): Promise<unknown> { return this.page.goto(`${settings.baseUrl}/checkout`); }
  expectStorefront(): Promise<void> { return expect(this.page).toHaveURL(`${settings.baseUrl}/`); }

  async expectShippingPage(): Promise<void> {
    await expect(this.page).toHaveURL(`${settings.baseUrl}/checkout`);
    await expect(this.page.getByRole("heading", { name: "Shipping details" })).toBeVisible();
  }

  async expectShippingFields(): Promise<void> {
    for (const label of Object.keys(fieldIds)) {
      await expect(this.page.getByLabel(label, { exact: true })).toBeVisible();
    }
  }

  async expectSummary(name: string, quantity: number, total: number): Promise<void> {
    const summary = this.page.locator(".checkout-summary");
    await expect(summary).toContainText(name);
    await expect(summary).toContainText(`${quantity} `);
    await expect(summary).toContainText(`$${total.toFixed(2)}`);
  }

  backToCart(): Promise<void> { return this.page.getByRole("link", { name: "Back to cart", exact: true }).click(); }

  async fillShipping(data: Record<string, string>, missing?: string): Promise<void> {
    for (const [label, value] of Object.entries(data)) {
      await this.page.getByLabel(label, { exact: true }).fill(label === missing ? "" : value);
    }
  }

  placeOrder(): Promise<void> { return this.page.getByRole("button", { name: "Place order", exact: true }).click(); }

  async expectFieldValidation(label: string): Promise<void> {
    assert.equal(this.page.url(), `${settings.baseUrl}/checkout`);
    const field = this.page.locator(fieldIds[label]);
    await expect(field).toBeVisible();
    assert.equal(await field.evaluate((element: HTMLInputElement) => element.validity.valid), false);
    assert.ok(await field.evaluate((element: HTMLInputElement) => element.validationMessage));
  }

  expectCheckoutUrl(): Promise<void> { return expect(this.page).toHaveURL(`${settings.baseUrl}/checkout`); }

  async expectConfirmation(): Promise<void> {
    await expect(this.page).toHaveURL(/\/orders\/\d+\/confirmation$/);
    const match = this.page.url().match(/\/orders\/(\d+)\/confirmation$/);
    assert.ok(match);
    this.orderId = Number(match[1]);
    await expect(this.page.getByRole("heading", { name: "Your order was placed successfully", exact: true })).toBeVisible();
  }

  expectOrderNumber(): Promise<void> { return expect(this.page.locator(".confirmation > .eyebrow")).toHaveText(/Order #\d+/); }
  expectSuccess(): Promise<void> { return expect(this.page.getByRole("heading", { name: "Your order was placed successfully", exact: true })).toBeVisible(); }

  async expectOrderItems(expected: OrderItemRecord[]): Promise<void> {
    for (const item of expected) {
      const line = this.page.locator(".confirmation .summary-lines li").filter({ hasText: item.product_name });
      await expect(line).toContainText(String(item.quantity));
      await expect(line).toContainText(`$${item.unit_price.toFixed(2)}`);
      await expect(line).toContainText(`$${item.line_total.toFixed(2)}`);
    }
  }

  expectOrderTotal(total: number): Promise<void> { return expect(this.page.locator(".confirmation .summary-total")).toContainText(`$${total.toFixed(2)}`); }

  async expectShippingSummary(data: Record<string, string>): Promise<void> {
    const summary = this.page.locator('[aria-labelledby="delivery-title"]');
    for (const value of Object.values(data)) {
      await expect(summary).toContainText(value);
    }
  }

  backToStorefront(): Promise<void> { return this.page.getByRole("link", { name: "Back to storefront", exact: true }).click(); }

  async expectStorefrontCatalog(): Promise<void> {
    await expect(this.page.getByRole("heading", { name: "Welcome to FictoShop" })).toBeVisible();
    await expect(this.page.getByRole("heading", { name: "Our products" })).toBeVisible();
  }

  expectInsufficientStock(name: string): Promise<void> {
    return expect(this.page.locator(".form-error")).toContainText(`There is no longer enough stock for ${name}.`);
  }

  async openConfirmationInAnotherSession(browser: Browser): Promise<{ status: number; body: string }> {
    const context = await browser.newContext();
    try {
      const response = await (await context.newPage()).goto(this.page.url());
      assert.ok(response);
      return { status: response.status(), body: await response.text() };
    } finally {
      await context.close();
    }
  }
}
