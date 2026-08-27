import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { Given, Then, When } from "@cucumber/cucumber";
import { CartPage } from "../pages/cart-page.js";
import type { FictoshopWorld } from "../support/world.js";

function cart(world: FictoshopWorld): CartPage { return new CartPage(world.page); }
function primary(world: FictoshopWorld) { return world.state.products.primary; }
function secondary(world: FictoshopWorld) { return world.state.products.secondary; }

Given("the catalog contains an available product", async function (this: FictoshopWorld) {
  const reference = randomUUID().slice(0, 8);
  this.state.products.primary = await this.data.createProduct(`Playwright product ${reference}`, "Product created for TypeScript cart scenarios.", 49.95, 7);
  this.state.products.secondary = await this.data.createProduct(`Second cart product ${reference}`, "Second product for TypeScript cart scenarios.", 15.25, 8);
});

for (const step of ["the floating cart is not visible", "the floating cart is hidden"]) {
  Then(step, async function (this: FictoshopWorld) { await cart(this).expectHidden(); });
}

When("the customer adds 1 available product to the cart", async function (this: FictoshopWorld) { await cart(this).addProduct(primary(this).name); });
Then("the floating cart is visible", async function (this: FictoshopWorld) { await cart(this).expectVisible(); });
Then("it shows the product name", async function (this: FictoshopWorld) { await cart(this).expectProductInCart(primary(this).name); });
Then("it shows 1 total item", async function (this: FictoshopWorld) { await cart(this).expectTotalItems(1); });
Then("it shows the correct total price", async function (this: FictoshopWorld) { await cart(this).expectGrandTotal(primary(this).price); });
Given("the customer has added 1 product to the cart", async function (this: FictoshopWorld) { await cart(this).addProduct(primary(this).name); });
When("the customer scrolls to another part of the storefront", async function (this: FictoshopWorld) { await cart(this).scroll(); });
Then("the floating cart remains inside the viewport", async function (this: FictoshopWorld) { await cart(this).expectInsideViewport(); });
When("the customer selects quantity 3", async function (this: FictoshopWorld) { await cart(this).selectQuantity(primary(this).name, 3); });
When("adds the product to the cart", async function (this: FictoshopWorld) { await cart(this).addSelectedProduct(primary(this).name); });

for (const step of ["the cart line shows quantity 3", "the line quantity is 3"]) {
  Then(step, async function (this: FictoshopWorld) { await cart(this).expectLineQuantity(primary(this).name, 3); });
}

Then("the total equals three times the unit price", async function (this: FictoshopWorld) { await cart(this).expectGrandTotal(primary(this).price * 3); });
When("the customer adds 2 more of the same product", async function (this: FictoshopWorld) { await cart(this).addProduct(primary(this).name, 2); });
Then("the cart contains one line for that product", async function (this: FictoshopWorld) { await cart(this).expectOneLine(primary(this).name); });

async function addMultiple(world: FictoshopWorld): Promise<void> {
  await cart(world).addProduct(primary(world).name, 1);
  await cart(world).addProduct(secondary(world).name, 2);
}

for (const step of ["the customer adds multiple different products", "the cart contains two different products", "the cart contains products"]) {
  Given(step, async function (this: FictoshopWorld) { await addMultiple(this); });
}

Then("every selected product is shown in the cart", async function (this: FictoshopWorld) {
  await cart(this).expectProductInCart(primary(this).name);
  await cart(this).expectProductInCart(secondary(this).name);
});
Then("total items equal the sum of all quantities", async function (this: FictoshopWorld) { await cart(this).expectTotalItems(3); });
Then("the grand total equals the sum of all line totals", async function (this: FictoshopWorld) { await cart(this).expectGrandTotal(primary(this).price + secondary(this).price * 2); });
When("the customer removes one product", async function (this: FictoshopWorld) { await cart(this).removeProduct(primary(this).name); });
Then("only that product disappears from the cart", async function (this: FictoshopWorld) {
  await cart(this).expectProductNotInCart(primary(this).name);
  await cart(this).expectProductInCart(secondary(this).name);
});
Then("the totals are recalculated", async function (this: FictoshopWorld) {
  await cart(this).expectTotalItems(2);
  await cart(this).expectGrandTotal(secondary(this).price * 2);
});
When("the customer selects \"Clear\"", async function (this: FictoshopWorld) { await cart(this).clear(); });
Then("all cart lines are removed", async function (this: FictoshopWorld) { assert.equal(await cart(this).cartItems.count(), 0); });
When("the customer reloads the storefront", async function (this: FictoshopWorld) { await cart(this).reload(); });
Then("the same product and quantity remain in the cart", async function (this: FictoshopWorld) {
  await cart(this).expectProductInCart(primary(this).name);
  await cart(this).expectLineQuantity(primary(this).name, 1);
});
When("the customer attempts to add more units than available", async function (this: FictoshopWorld) {
  const page = cart(this);
  await page.attemptOverStock(primary(this).name, primary(this).in_stock);
  this.state.lastBrowserStatus = page.lastCartResponseStatus;
});
Then("the request is rejected", function (this: FictoshopWorld) { assert.equal(this.state.lastBrowserStatus, 400); });
Then("a stock error is displayed", async function (this: FictoshopWorld) { await cart(this).expectStockError(primary(this).in_stock, primary(this).name); });
Then("the cart quantity is unchanged", async function (this: FictoshopWorld) { await cart(this).expectTotalItems(0); });
When("the customer removes that product from the cart", async function (this: FictoshopWorld) { await cart(this).removeProduct(primary(this).name); });
Then("the catalog shows the original available stock", async function (this: FictoshopWorld) { await cart(this).expectCatalogStock(primary(this).name, primary(this).in_stock); });
