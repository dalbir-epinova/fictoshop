import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { Given, Then, When } from "@cucumber/cucumber";
import { CartPage } from "../pages/cart-page.js";
import { CheckoutPage } from "../pages/checkout-page.js";
import { settings } from "../support/settings.js";
import type { FictoshopWorld } from "../support/world.js";
import type { ProductRecord } from "../support/models.js";

function cart(world: FictoshopWorld): CartPage { return new CartPage(world.page); }
function checkout(world: FictoshopWorld): CheckoutPage { return new CheckoutPage(world.page); }
function available(world: FictoshopWorld) { return world.state.products.available; }
function secondary(world: FictoshopWorld) { return world.state.products.secondary; }

async function placeOrder(world: FictoshopWorld, products: Array<[ProductRecord, number]>): Promise<void> {
  world.state.expectedItems = [];
  await cart(world).open();
  for (const [product, quantity] of products) {
    await cart(world).addProduct(product.name, quantity);
    world.state.expectedItems.push({ product_name: product.name, unit_price: product.price, quantity, line_total: product.price * quantity });
  }
  await checkout(world).open();
  await checkout(world).fillShipping(world.state.shipping);
  await checkout(world).placeOrder();
  await checkout(world).expectConfirmation();
}

When("the customer opens {string} with an empty cart", async function (this: FictoshopWorld, _path: string) { await checkout(this).open(); });
Then("the customer is redirected to the storefront", async function (this: FictoshopWorld) { await checkout(this).expectStorefront(); });
When("the customer selects \"Checkout\"", async function (this: FictoshopWorld) { await this.page.getByRole("button", { name: "Checkout", exact: true }).click(); });
Then("the shipping details page opens", async function (this: FictoshopWorld) { await checkout(this).expectShippingPage(); });
Then("fields for name, email, phone, address, postal code, city, and country are visible", async function (this: FictoshopWorld) { await checkout(this).expectShippingFields(); });
Then("the ordered product, quantity, and total are visible", async function (this: FictoshopWorld) { await checkout(this).expectSummary(available(this).name, 1, available(this).price); });

Given("the customer is on checkout with a product in the cart", async function (this: FictoshopWorld) {
  await cart(this).open();
  await cart(this).addProduct(available(this).name, 1);
  await checkout(this).open();
});

When("the customer selects \"Back to cart\"", async function (this: FictoshopWorld) { await checkout(this).backToCart(); });
Then("the storefront opens at the cart", function (this: FictoshopWorld) { assert.equal(this.page.url(), `${settings.baseUrl}\/#cart`); });
Then("the product remains in the cart", async function (this: FictoshopWorld) { await cart(this).expectProductInCart(available(this).name); });
When("the customer submits valid shipping details except for {string}", async function (this: FictoshopWorld, field: string) {
  await checkout(this).fillShipping(this.state.shipping, field);
  await checkout(this).placeOrder();
});

for (const step of ["the order is not placed", "no order is created"]) {
  Then(step, async function (this: FictoshopWorld) { assert.equal(await this.data.countOrders(), this.state.initialOrderCount); });
}

Then("a validation message is shown for {string}", async function (this: FictoshopWorld, field: string) { await checkout(this).expectFieldValidation(field); });
When("the customer enters an invalid email address", async function (this: FictoshopWorld) { await checkout(this).fillShipping({ ...this.state.shipping, Email: "invalid-email" }); });
When("attempts to place the order", async function (this: FictoshopWorld) { await checkout(this).placeOrder(); });
Then("the email field reports a validation error", async function (this: FictoshopWorld) { await checkout(this).expectFieldValidation("Email"); });
When("the customer enters valid shipping details", async function (this: FictoshopWorld) { await checkout(this).fillShipping(this.state.shipping); });
When("selects \"Place order\"", async function (this: FictoshopWorld) { await checkout(this).placeOrder(); });
Then("an order confirmation page opens", async function (this: FictoshopWorld) { await checkout(this).expectConfirmation(); });
Then("a unique order number is displayed", async function (this: FictoshopWorld) { await checkout(this).expectOrderNumber(); });
Then("the page confirms that the order was placed successfully", async function (this: FictoshopWorld) { await checkout(this).expectSuccess(); });

When("the customer places a valid order containing multiple products", async function (this: FictoshopWorld) {
  const reference = randomUUID().slice(0, 8);
  this.state.products.secondary = await this.data.createProduct(`Checkout second ${reference}`, "Checkout test product", 12.50, 6);
  await placeOrder(this, [[available(this), 1], [secondary(this), 2]]);
});
Then("every product name, unit price, quantity, and line total is shown", async function (this: FictoshopWorld) { await checkout(this).expectOrderItems(this.state.expectedItems); });
Then("the correct order total is shown", async function (this: FictoshopWorld) { await checkout(this).expectOrderTotal(this.state.expectedItems.reduce((sum, item) => sum + item.line_total, 0)); });

for (const step of ["the customer places an order with valid shipping details", "the customer places a valid order"]) {
  When(step, async function (this: FictoshopWorld) { await placeOrder(this, [[available(this), 2]]); });
}

Then("the confirmation shows the customer's name", async function (this: FictoshopWorld) { await checkout(this).expectShippingSummary({ "Full name": this.state.shipping["Full name"] }); });
Then("it shows the address, postal code, city, and country", async function (this: FictoshopWorld) {
  const shipping = this.state.shipping;
  await checkout(this).expectShippingSummary({ Address: shipping.Address, "Postal code": shipping["Postal code"], City: shipping.City, Country: shipping.Country });
});
Then("it shows the email and phone number", async function (this: FictoshopWorld) { await checkout(this).expectShippingSummary({ Email: this.state.shipping.Email, Phone: this.state.shipping.Phone }); });
When("returns to the storefront", async function (this: FictoshopWorld) { await checkout(this).backToStorefront(); });
Then("product stock is reduced by the purchased quantity", async function (this: FictoshopWorld) { await cart(this).expectCatalogStock(available(this).name, this.state.initialStock - 2); });
Given("the customer has placed an order", async function (this: FictoshopWorld) { await placeOrder(this, [[available(this), 1]]); });
When("the customer selects \"Back to storefront\"", async function (this: FictoshopWorld) { await checkout(this).backToStorefront(); });
Then("the storefront heading and catalog are visible", async function (this: FictoshopWorld) { await checkout(this).expectStorefrontCatalog(); });
Given("a customer has placed an order in one browser session", async function (this: FictoshopWorld) { await placeOrder(this, [[available(this), 1]]); });
When("a different browser session opens that confirmation URL", async function (this: FictoshopWorld) {
  assert.ok(this.browser);
  const result = await checkout(this).openConfirmationInAnotherSession(this.browser);
  this.state.lastBrowserStatus = result.status;
  this.state.lastBrowserBody = result.body;
});
Then("a 404 response is returned", function (this: FictoshopWorld) { assert.equal(this.state.lastBrowserStatus, 404); });
Then("no customer or shipping details are exposed", function (this: FictoshopWorld) {
  for (const value of Object.values(this.state.shipping)) assert.ok(!this.state.lastBrowserBody.includes(value));
});
Given("the customer has products in the cart", async function (this: FictoshopWorld) {
  await cart(this).open();
  await cart(this).addProduct(available(this).name, 2);
  await checkout(this).open();
});
Given("one product no longer has enough stock", async function (this: FictoshopWorld) {
  await this.data.setProductStock(available(this).id, 1);
  this.state.initialStock = 1;
});
When("the customer submits valid shipping details", async function (this: FictoshopWorld) {
  await checkout(this).fillShipping(this.state.shipping);
  await checkout(this).placeOrder();
});
Then("an insufficient-stock message identifies the product", async function (this: FictoshopWorld) { await checkout(this).expectInsufficientStock(available(this).name); });
Then("no product stock is reduced", async function (this: FictoshopWorld) { assert.equal(await this.data.getProductStock(available(this).id), this.state.initialStock); });
Then("the cart remains unchanged", async function (this: FictoshopWorld) {
  const response = await this.api.get("/cart");
  assert.equal((response.json as { total_items: number }).total_items, 2);
});
