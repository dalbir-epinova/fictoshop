import { expect, type Locator, type Page } from "@playwright/test";
import type { Credentials, OrderItemRecord, OrderRecord } from "../support/models.js";
import { settings } from "../support/settings.js";

export class AdminPage {
  private readonly username: Locator;
  private readonly password: Locator;
  private readonly loginButton: Locator;

  constructor(private readonly page: Page) {
    this.username = page.getByLabel("Username");
    this.password = page.getByLabel("Password");
    this.loginButton = page.getByRole("button", { name: "Log in" });
  }

  open(): Promise<unknown> { return this.page.goto(`${settings.baseUrl}/admin/`); }

  async login(credentials: Credentials): Promise<void> {
    await this.username.fill(credentials.username);
    await this.password.fill(credentials.password);
    await this.loginButton.click();
  }

  async expectLoginPage(): Promise<void> {
    await expect(this.username).toBeVisible();
    await expect(this.password).toBeVisible();
    await expect(this.loginButton).toBeVisible();
  }

  expectIndex(): Promise<void> { return expect(this.page.getByRole("heading", { name: "Site administration" })).toBeVisible(); }

  async expectProductsAndOrders(): Promise<void> {
    await expect(this.page.getByRole("link", { name: "Products", exact: true })).toBeVisible();
    await expect(this.page.getByRole("link", { name: "Orders", exact: true })).toBeVisible();
  }

  openNewProduct(): Promise<unknown> { return this.page.goto(`${settings.baseUrl}/admin/shop/product/add/`); }

  async fillProduct(name: string, description: string, price: number, stock: number): Promise<void> {
    await this.page.getByLabel("Name:").fill(name);
    await this.page.getByLabel("Description:").fill(description);
    await this.page.getByLabel("Price:").fill(price.toFixed(2));
    await this.page.getByLabel("In stock:").fill(String(stock));
  }

  uploadImage(path: string): Promise<void> { return this.page.getByLabel("Image:").setInputFiles(path); }
  save(): Promise<void> { return this.page.getByRole("button", { name: "Save", exact: true }).click(); }
  openProduct(id: number): Promise<unknown> { return this.page.goto(`${settings.baseUrl}/admin/shop/product/${id}/change/`); }

  async changeStock(stock: number): Promise<void> {
    await this.page.getByLabel("In stock:").fill(String(stock));
    await this.save();
  }

  expectProductListed(name: string): Promise<void> {
    return expect(this.page.locator("#result_list").getByRole("link", { name, exact: true })).toBeVisible();
  }

  openOrder(id: number): Promise<unknown> { return this.page.goto(`${settings.baseUrl}/admin/shop/order/${id}/change/`); }

  async expectOrder(order: OrderRecord): Promise<void> {
    await expect(this.page.getByLabel("Full name:")).toHaveValue(order.full_name);
    await expect(this.page.getByLabel("Email:")).toHaveValue(order.email);
    await expect(this.page.getByLabel("Phone:")).toHaveValue(order.phone);
    await expect(this.page.getByLabel("Address:")).toHaveValue(order.address);
    await expect(this.page.getByLabel("Postal code:")).toHaveValue(order.postal_code);
    await expect(this.page.getByLabel("City:")).toHaveValue(order.city);
    await expect(this.page.getByLabel("Country:")).toHaveValue(order.country);
    await expect(this.page.locator("#content-main")).toContainText(String(order.total_amount));
    await expect(this.page.locator(".field-created_at .readonly")).not.toBeEmpty();
  }

  async expectItemsReadOnly(items: OrderItemRecord[]): Promise<void> {
    const group = this.page.locator("#items-group");
    for (const item of items) {
      await expect(group).toContainText(item.product_name);
      await expect(group).toContainText(String(item.unit_price));
      await expect(group).toContainText(String(item.quantity));
      await expect(group).toContainText(String(item.line_total));
    }
    for (const field of ["product_name", "unit_price", "quantity", "line_total"]) {
      await expect(group.locator(`input[name$="-${field}"]`)).toHaveCount(0);
    }
  }
}
