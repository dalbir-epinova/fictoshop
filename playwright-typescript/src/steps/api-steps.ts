import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { Given, Then, When } from "@cucumber/cucumber";
import type { ApiResponse } from "../support/models.js";
import type { FictoshopWorld } from "../support/world.js";

function response(world: FictoshopWorld): ApiResponse {
  assert.ok(world.state.response, "API response is missing.");
  return world.state.response;
}
function json(world: FictoshopWorld): any { return response(world).json; }
function available(world: FictoshopWorld) { return world.state.products.available; }

When("the client requests {string}", async function (this: FictoshopWorld, path: string) { this.state.response = await this.api.get(path); });
Then("the response is successful", function (this: FictoshopWorld) { assert.ok(response(this).status >= 200 && response(this).status < 300, response(this).text); });
Then("it identifies the frontend, products, cart, login, and API exploration paths", function (this: FictoshopWorld) {
  assert.deepEqual({ frontend: json(this).frontend, products: json(this).products, cart: json(this).cart, login: json(this).login, docs: json(this).docs }, { frontend: "/", products: "/products", cart: "/cart", login: "/login", docs: "/products" });
});
Then("each product contains id, name, description, price, stock, image, rating, and review count", function (this: FictoshopWorld) {
  const products = json(this) as Array<Record<string, unknown>>;
  assert.ok(Array.isArray(products) && products.length > 0);
  for (const product of products) for (const field of ["id", "name", "description", "price", "in_stock", "image_url", "average_rating", "review_count"]) assert.ok(field in product, `Product is missing ${field}`);
});
Given("a product with reviews exists", async function (this: FictoshopWorld) {
  const reference = randomUUID().slice(0, 8);
  const product = await this.data.createProduct(`Reviewed product ${reference}`, "Product created for the API review scenario.", 64.50, 9);
  this.state.products.reviewed = product;
  const one = await this.data.createUser(false);
  const two = await this.data.createUser(false);
  const first = await this.data.createReview(product, one, 4.5, "Excellent test product.");
  const second = await this.data.createReview(product, two, 3.5, "Useful, with room for improvement.");
  this.state.requestedUrls = [`${first.user}|${first.rating}|${first.comment}`, `${second.user}|${second.rating}|${second.comment}`];
});
When("the client requests that product from {string}", async function (this: FictoshopWorld, _path: string) { this.state.response = await this.api.get(`/products/${this.state.products.reviewed.id}`); });
Then("the response contains the selected product", function (this: FictoshopWorld) {
  const actual = json(this);
  const expected = this.state.products.reviewed;
  assert.ok(response(this).status < 300, response(this).text);
  assert.equal(actual.id, expected.id);
  assert.equal(actual.name, expected.name);
  assert.equal(actual.description, expected.description);
  assert.equal(Number(actual.price), expected.price);
  assert.equal(actual.in_stock, expected.in_stock);
});
Then("it contains the product reviews", function (this: FictoshopWorld) {
  const reviews = new Map((json(this).reviews as any[]).map((item) => [item.user, item]));
  assert.equal(reviews.size, 2);
  for (const encoded of this.state.requestedUrls) {
    const [user, rating, comment] = encoded.split("|", 3);
    assert.equal(String(reviews.get(user).rating), Number(rating).toFixed(1));
    assert.equal(reviews.get(user).comment, comment);
  }
});
When("the client requests an unknown product id", async function (this: FictoshopWorld) { this.state.response = await this.api.get("/products/2147483647"); });
Then(/^the API returns status "?(\d+)"?$/, function (this: FictoshopWorld, status: string) { assert.equal(response(this).status, Number(status), response(this).text); });
Then("the response says \"Product not found\"", function (this: FictoshopWorld) { assert.equal(json(this).detail, "Product not found"); });
When("the client posts its id and a valid quantity to {string}", async function (this: FictoshopWorld, path: string) { this.state.response = await this.api.post(path, { product_id: available(this).id, quantity: 2 }); });
Then("the response contains the updated items, item count, and total", function (this: FictoshopWorld) {
  const actual = json(this);
  assert.equal(actual.items.length, 1);
  assert.equal(actual.items[0].product.id, available(this).id);
  assert.equal(actual.items[0].quantity, 2);
  assert.equal(Number(actual.items[0].line_total), available(this).price * 2);
  assert.equal(actual.total_items, 2);
  assert.equal(Number(actual.grand_total), available(this).price * 2);
});
When("the client posts product id {string} and quantity {string} to {string}", async function (this: FictoshopWorld, productId: string, quantity: string, path: string) {
  if (!this.state.products.available) {
    const reference = randomUUID().slice(0, 8);
    this.state.products.available = await this.data.createProduct(`API product ${reference}`, "Product for TypeScript API scenarios.", 49.95, 7);
    await this.api.delete("/cart");
  }
  const resolvedId = productId === "valid" ? available(this).id : productId === "unknown" ? 2147483647 : Number(productId);
  const resolvedQuantity = quantity === "too many" ? available(this).in_stock + 1 : Number(quantity);
  this.state.response = await this.api.post(path, { product_id: resolvedId, quantity: resolvedQuantity });
});
async function populateCartApi(world: FictoshopWorld): Promise<void> {
  const reference = randomUUID().slice(0, 8);
  world.state.products.available = await world.data.createProduct(`API product ${reference}`, "Product for TypeScript API scenarios.", 49.95, 7);
  await world.api.delete("/cart");
  const result = await world.api.post("/cart", { product_id: available(world).id, quantity: 2 });
  assert.equal(result.status, 201, result.text);
}
for (const step of ["the cart API contains a product", "the cart API contains products"]) Given(step, async function (this: FictoshopWorld) { await populateCartApi(this); });
When("the client deletes {string}", async function (this: FictoshopWorld, target: string) {
  const path = target.includes("<product_id>") ? `/cart/${available(this).id}` : target;
  this.state.response = await this.api.delete(path);
});
Then("that product is absent from the returned cart", function (this: FictoshopWorld) {
  assert.ok(response(this).status < 300, response(this).text);
  assert.ok(!(json(this).items as any[]).some((item) => item.product.id === available(this).id));
  assert.equal(json(this).total_items, 0);
  assert.equal(Number(json(this).grand_total), 0);
});
Then("the returned cart is empty", function (this: FictoshopWorld) { assert.ok(response(this).status < 300); assert.equal(json(this).items.length, 0); });
Then("total items and grand total are zero", function (this: FictoshopWorld) { assert.equal(json(this).total_items, 0); assert.equal(Number(json(this).grand_total), 0); });
