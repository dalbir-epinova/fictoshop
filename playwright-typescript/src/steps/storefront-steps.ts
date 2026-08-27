import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { Given, Then, When } from "@cucumber/cucumber";
import { CatalogPage } from "../pages/catalog-page.js";
import type { FictoshopWorld } from "../support/world.js";

function catalog(world: FictoshopWorld): CatalogPage { return new CatalogPage(world.page); }
function product(world: FictoshopWorld, key: string) { return world.state.products[key]; }

Given("the catalog contains available and unavailable products", async function (this: FictoshopWorld) {
  const reference = randomUUID().slice(0, 8);
  this.state.products.available = await this.data.createProduct(`In-stock catalog item ${reference}`, "Available product for storefront tests.", 40, 4);
  this.state.products.secondary = await this.data.createProduct(`Secondary catalog ${reference}`, `Unique storefront description ${reference}`, 15.50, 9);
  this.state.products.unavailable = await this.data.createProduct(`Sold-out catalog item ${reference}`, "Out-of-stock product for storefront tests.", 75, 0);
  this.state.searchQuery = `Unique storefront description ${reference}`;
});

for (const step of ["the heading \"Welcome to FictoShop\" is visible", "the catalog is visible", "at least one product card is displayed"]) {
  Then(step, async function (this: FictoshopWorld) { await catalog(this).expectHeadingAndCatalog(); });
}

for (const step of ["each product card shows its name", "each product card shows its price", "each product card shows its stock status"]) {
  Then(step, async function (this: FictoshopWorld) { await catalog(this).expectCardsHavePurchasingInformation(); });
}

Then("an available product has an enabled \"Add to cart\" button", async function (this: FictoshopWorld) { await catalog(this).expectAvailableAddEnabled(product(this, "available").name); });
When("the customer selects a product name", async function (this: FictoshopWorld) { await catalog(this).openProduct(product(this, "available").name); });

for (const step of ["the product detail page opens", "the product name, description, price, rating summary, and reviews section are visible"]) {
  Then(step, async function (this: FictoshopWorld) { await catalog(this).expectProductDetail(product(this, "available")); });
}

When("the customer searches for part of a product name", async function (this: FictoshopWorld) {
  this.state.initialProductCount = await catalog(this).productCards.count();
  await catalog(this).search(product(this, "available").name);
});
Then("only matching products are displayed", async function (this: FictoshopWorld) { await catalog(this).expectOnlyProduct(product(this, "available").name); });
Then("the catalog status shows the number of matches", async function (this: FictoshopWorld) { await catalog(this).expectCatalogStatus(1, this.state.initialProductCount); });
When("the customer searches for text found only in a product description", async function (this: FictoshopWorld) { await catalog(this).search(this.state.searchQuery); });
Then("the matching product is displayed", async function (this: FictoshopWorld) { await catalog(this).expectOnlyProduct(product(this, "secondary").name); });
When("the customer searches for text that is not in the catalog", async function (this: FictoshopWorld) { await catalog(this).search("no-such-product-playwright-9f31"); });

for (const step of ["no product cards are displayed", "the empty search message is visible"]) {
  Then(step, async function (this: FictoshopWorld) { await catalog(this).expectNoProducts(); });
}

Given("the customer has filtered the catalog using search", async function (this: FictoshopWorld) {
  this.state.initialProductCount = await catalog(this).productCards.count();
  await catalog(this).search(product(this, "available").name);
});
When("the customer clears the search field", async function (this: FictoshopWorld) { await catalog(this).clearSearch(); });
Then("all products are displayed again", async function (this: FictoshopWorld) { await catalog(this).expectProductCount(this.state.initialProductCount); });
When("the customer selects \"Price: Low to high\"", async function (this: FictoshopWorld) { await catalog(this).selectSort("Price: Low to high"); });
Then("product prices are ordered from lowest to highest", async function (this: FictoshopWorld) {
  const values = await catalog(this).displayedPrices();
  assert.deepEqual(values, [...values].sort((a, b) => a - b));
});
When("the customer selects \"Price: High to low\"", async function (this: FictoshopWorld) { await catalog(this).selectSort("Price: High to low"); });
Then("product prices are ordered from highest to lowest", async function (this: FictoshopWorld) {
  const values = await catalog(this).displayedPrices();
  assert.deepEqual(values, [...values].sort((a, b) => b - a));
});
When("the customer selects \"Stock level\"", async function (this: FictoshopWorld) { await catalog(this).selectSort("Stock level"); });
Then("products are ordered from highest to lowest available stock", async function (this: FictoshopWorld) {
  const values = await catalog(this).displayedStocks();
  assert.deepEqual(values, [...values].sort((a, b) => b - a));
});
When("the customer enables \"In stock only\"", async function (this: FictoshopWorld) { await catalog(this).enableInStockOnly(); });
Then("products with zero available stock are hidden", async function (this: FictoshopWorld) { await catalog(this).expectProductHidden(product(this, "unavailable").name); });

for (const step of ["an out-of-stock product shows \"Out of stock\"", "its quantity controls are disabled", "its \"Add to cart\" button is disabled"]) {
  Then(step, async function (this: FictoshopWorld) { await catalog(this).expectOutOfStockControls(product(this, "unavailable").name); });
}

When("the customer decreases the initial quantity", async function (this: FictoshopWorld) { await catalog(this).decreaseInitialQuantity(product(this, "available").name); });
Then("the quantity remains 1", async function (this: FictoshopWorld) { await catalog(this).expectQuantity(product(this, "available").name, 1); });
When("the customer increases the quantity beyond available stock", async function (this: FictoshopWorld) { const item = product(this, "available"); await catalog(this).increaseBeyondStock(item.name, item.in_stock); });
Then("the quantity does not exceed available stock", async function (this: FictoshopWorld) { const item = product(this, "available"); await catalog(this).expectQuantity(item.name, item.in_stock); });
When("the customer selects \"Explore the API\"", async function (this: FictoshopWorld) { await catalog(this).exploreApi(); });
Then("the browser opens the {string} endpoint", async function (this: FictoshopWorld, _path: string) { await catalog(this).expectProductsEndpoint(); });
Then("the response contains catalog products", async function (this: FictoshopWorld) { await catalog(this).expectApiCatalogProducts(); });
