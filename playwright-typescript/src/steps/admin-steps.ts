import assert from "node:assert/strict";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { Given, Then, When } from "@cucumber/cucumber";
import { AdminPage } from "../pages/admin-page.js";
import { CatalogPage } from "../pages/catalog-page.js";
import { projectPaths } from "../support/project-paths.js";
import type { FictoshopWorld } from "../support/world.js";

const description = "Product created by the Playwright admin scenario.";
const price = 49.95;
const stock = 7;
const newStock = 12;

function admin(world: FictoshopWorld) { return new AdminPage(world.page); }
function productName(world: FictoshopWorld): string {
  world.state.selectedProductName ||= `Playwright product ${randomUUID().slice(0, 8)}`;
  return world.state.selectedProductName;
}

Given("a superuser is signed in", async function (this: FictoshopWorld) {
  this.state.admin ??= await this.data.createUser(true);
  await admin(this).open();
  await admin(this).login(this.state.admin);
  await admin(this).expectIndex();
});
When("the customer opens {string}", async function (this: FictoshopWorld, _path: string) { await admin(this).open(); });
When("the superuser opens {string}", async function (this: FictoshopWorld, _path: string) { await admin(this).open(); });
Then("the Django admin login page is displayed", async function (this: FictoshopWorld) { await admin(this).expectLoginPage(); });
Then("the administration index is visible", async function (this: FictoshopWorld) { await admin(this).expectIndex(); });
Then("Products and Orders are listed", async function (this: FictoshopWorld) { await admin(this).expectProductsAndOrders(); });
When("the superuser opens the new product form", async function (this: FictoshopWorld) { await admin(this).openNewProduct(); });
When("enters a valid product name, description, price, and stock", async function (this: FictoshopWorld) { await admin(this).fillProduct(productName(this), description, price, stock); });
When("uploads a dummy product image", async function (this: FictoshopWorld) { await admin(this).uploadImage(path.join(projectPaths.root, "images", "uploads", "boxing_gloves.jpg")); });
When("saves the product", async function (this: FictoshopWorld) { await admin(this).save(); });
Then("the product appears in Django administration", async function (this: FictoshopWorld) { await admin(this).expectProductListed(productName(this)); });
Then("the product appears in the storefront catalog", async function (this: FictoshopWorld) { const page = new CatalogPage(this.page); await page.open(); await page.expectProductVisible(productName(this)); });
Then("the product image is displayed in the storefront catalog", async function (this: FictoshopWorld) { await new CatalogPage(this.page).expectProductImage(productName(this)); });
Given("a product exists", async function (this: FictoshopWorld) { this.state.products.admin = await this.data.createProduct(productName(this), description, price, stock); });
When("the superuser changes its stock value", async function (this: FictoshopWorld) { await admin(this).openProduct(this.state.products.admin.id); await admin(this).changeStock(newStock); });
Then("the new stock value appears in the storefront", async function (this: FictoshopWorld) { const page = new CatalogPage(this.page); await page.open(); await page.expectProductStock(productName(this), newStock); });
Given("a customer order exists", async function (this: FictoshopWorld) { this.state.order = await this.data.createOrder(); });
When("the superuser opens that order in administration", async function (this: FictoshopWorld) { assert.ok(this.state.order); await admin(this).openOrder(this.state.order.id); });
Then("customer, shipping, total, and creation details are visible", async function (this: FictoshopWorld) { assert.ok(this.state.order); await admin(this).expectOrder(this.state.order); });
Then("each order line is visible as read-only data", async function (this: FictoshopWorld) { assert.ok(this.state.order); await admin(this).expectItemsReadOnly(this.state.order.items); });
