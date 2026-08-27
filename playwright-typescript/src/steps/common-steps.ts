import assert from "node:assert/strict";
import { Given } from "@cucumber/cucumber";
import { CartPage } from "../pages/cart-page.js";
import { CatalogPage } from "../pages/catalog-page.js";
import type { FictoshopWorld } from "../support/world.js";

Given("the cart has been cleared", async function (this: FictoshopWorld) {
  assert.ok((await this.api.delete("/cart")).status < 300);
});

Given("the customer opens the storefront", async function (this: FictoshopWorld) {
  await new CatalogPage(this.page).open();
});

Given("the customer has added a product to the cart", async function (this: FictoshopWorld) {
  const product = this.state.products.primary ?? this.state.products.available;
  assert.ok(product, "No product fixture is available for the cart.");
  const cart = new CartPage(this.page);
  await cart.open();
  await cart.addProduct(product.name, 1);
});

Given("the customer is signed out", async function (this: FictoshopWorld) {
  await this.context?.clearCookies();
});
