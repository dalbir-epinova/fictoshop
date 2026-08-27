import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { Given, Then, When } from "@cucumber/cucumber";
import { CartPage } from "../pages/cart-page.js";
import { CheckoutPage } from "../pages/checkout-page.js";
import { MobilePage } from "../pages/mobile-page.js";
import { projectPaths } from "../support/project-paths.js";
import type { FictoshopWorld } from "../support/world.js";

function mobile(world: FictoshopWorld): MobilePage {
  const value = new MobilePage(world.page);
  value.requestedUrls = world.state.requestedUrls;
  value.configuredIosBase = world.state.configuredIosBase;
  return value;
}

async function ensureMobileProduct(world: FictoshopWorld): Promise<void> {
  if (!world.state.products.mobile) {
    const reference = randomUUID().slice(0, 8);
    world.state.products.mobile = await world.data.createProduct(`Mobile product ${reference}`, "Product for mobile layout tests.", 49.95, 7);
  }
}

Given("the browser viewport is {string}", async function (this: FictoshopWorld, viewport: string) { const [width, height] = viewport.toLowerCase().split("x").map(Number); await mobile(this).setViewport(width, height); });
Given("the browser uses a mobile viewport", async function (this: FictoshopWorld) { await mobile(this).setViewport(390, 844); });
Then("the heading and catalog fit within the viewport", async function (this: FictoshopWorld) { await mobile(this).expectStorefrontFits(); });
Then("primary controls are usable without horizontal scrolling", async function (this: FictoshopWorld) { await mobile(this).expectPrimaryControlsUsable(); });
When("the customer adds a product to the cart", async function (this: FictoshopWorld) { await ensureMobileProduct(this); const page = new CartPage(this.page); await page.open(); await page.addProduct(this.state.products.mobile.name); });
Then("the entire floating cart width remains inside the viewport", async function (this: FictoshopWorld) { await mobile(this).expectCartWidthInsideViewport(); });
Then("the cart lines can scroll when their content exceeds the maximum height", async function (this: FictoshopWorld) { await mobile(this).expectCartLinesScrollable(); });
Then("\"Clear\" and \"Checkout\" remain usable", async function (this: FictoshopWorld) { await mobile(this).expectCartActionsUsable(); });
Given("the cart contains a product", async function (this: FictoshopWorld) { await ensureMobileProduct(this); const page = new CartPage(this.page); await page.open(); await page.addProduct(this.state.products.mobile.name); });
When("the customer opens checkout", async function (this: FictoshopWorld) { await new CheckoutPage(this.page).open(); });
Then("shipping fields are arranged in one column", async function (this: FictoshopWorld) { await mobile(this).expectCheckoutSingleColumn(); });
Then("\"Back to cart\" and \"Place order\" are usable", async function (this: FictoshopWorld) { await mobile(this).expectCheckoutActionsUsable(); });
Given("the storefront is running in an Android emulator", function (this: FictoshopWorld) { assert.ok(fs.existsSync(path.join(projectPaths.root, "android-app\/app\/src\/main\/assets\/index.html"))); this.state.selectedProductName = "android"; });
Given("the storefront is running in the iOS app", function (this: FictoshopWorld) { assert.ok(fs.existsSync(path.join(projectPaths.root, "ios-app\/fictoshop\/fictoshop\/WebView.swift"))); this.state.selectedProductName = "ios"; });
When("the mobile bundle requests products", async function (this: FictoshopWorld) {
  const page = mobile(this);
  if (this.state.selectedProductName === "android") await page.loadAndroidBundle(); else await page.loadIosBundle();
  this.state.requestedUrls = page.requestedUrls;
  this.state.configuredIosBase = page.configuredIosBase;
});
Then("it uses {string}", function (this: FictoshopWorld, host: string) { assert.ok(this.state.requestedUrls.some((url) => url.startsWith(host + "/products"))); });
Then("it uses the configured \"API_BASE_URL\"", function (this: FictoshopWorld) { assert.ok(this.state.requestedUrls.some((url) => url.startsWith(`${this.state.configuredIosBase}\/products`))); });
Then("catalog products are displayed", async function (this: FictoshopWorld) { await mobile(this).expectBundleProduct(); });
