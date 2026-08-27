import { randomUUID } from "node:crypto";
import { Given } from "@cucumber/cucumber";
import type { FictoshopWorld } from "../support/world.js";

Given("an available product exists", async function (this: FictoshopWorld) {
  const reference = randomUUID().slice(0, 8);
  this.state.products.available = await this.data.createProduct(`Available product ${reference}`, "Product for TypeScript API and checkout scenarios.", 49.95, 7);
  this.state.initialStock = this.state.products.available.in_stock;
  this.state.initialOrderCount = await this.data.countOrders();
  this.state.shipping = {
    "Full name": `Checkout Customer ${reference}`,
    Email: `checkout-${reference}@example.com`,
    Phone: "+47 99887766",
    Address: "Testveien 42",
    "Postal code": "0123",
    City: "Oslo",
    Country: "Norway"
  };
  await this.api.delete("/cart");
});
