import assert from "node:assert/strict";
import { expect, type Locator, type Page } from "@playwright/test";
import type { Credentials } from "../support/models.js";
import { settings } from "../support/settings.js";

export class AuthenticationPage {
  private readonly username: Locator;
  private readonly password: Locator;
  private readonly loginButton: Locator;

  constructor(private readonly page: Page) {
    this.username = page.getByLabel("Username");
    this.password = page.getByLabel("Password");
    this.loginButton = page.getByRole("button", { name: "Log in" });
  }

  async openFromStorefront(): Promise<void> {
    await this.page.goto(settings.baseUrl);
    await this.page.locator("header").getByRole("link", { name: "Log in", exact: true }).click();
  }

  open(): Promise<unknown> { return this.page.goto(`${settings.baseUrl}/signin`); }
  submit(): Promise<void> { return this.loginButton.click(); }

  async submitInvalid(): Promise<void> {
    await this.username.fill("unknown-playwright-user");
    await this.password.fill("Invalid-Playwright-Password!");
    await this.submit();
  }

  async login(credentials: Credentials): Promise<void> {
    await this.open();
    await this.username.fill(credentials.username);
    await this.password.fill(credentials.password);
    await this.submit();
    const destination = credentials.superuser ? `${settings.baseUrl}/admin/` : `${settings.baseUrl}/`;
    await this.page.waitForURL(destination);
  }

  async expectCredentialFields(): Promise<void> {
    await expect(this.page).toHaveURL(`${settings.baseUrl}/signin`);
    await expect(this.username).toBeVisible();
    await expect(this.password).toBeVisible();
  }

  expectLoginButton(): Promise<void> { return expect(this.loginButton).toBeVisible(); }

  async expectMissingCredentials(): Promise<void> {
    assert.equal(await this.username.evaluate((element: HTMLInputElement) => element.validity.valueMissing), true);
    assert.ok(await this.username.evaluate((element: HTMLInputElement) => element.validationMessage));
  }

  async expectSignedOut(): Promise<void> {
    await this.page.goto(settings.baseUrl);
    await expect(this.page.locator("header").getByRole("link", { name: "Log in", exact: true })).toBeVisible();
  }

  expectInvalidCredentials(): Promise<void> { return expect(this.page.getByRole("status")).toHaveText("Invalid credentials"); }

  async expectSignInPage(): Promise<void> {
    await expect(this.page).toHaveURL(`${settings.baseUrl}/signin`);
    await expect(this.username).toBeVisible();
    await expect(this.password).toBeVisible();
  }
}
