import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { Given, Then, When } from "@cucumber/cucumber";
import { AdminPage } from "../pages/admin-page.js";
import { AuthenticationPage } from "../pages/authentication-page.js";
import { CatalogPage } from "../pages/catalog-page.js";
import { ReviewsPage } from "../pages/reviews-page.js";
import type { FictoshopWorld } from "../support/world.js";

function auth(world: FictoshopWorld) { return new AuthenticationPage(world.page); }
function catalog(world: FictoshopWorld) { return new CatalogPage(world.page); }
function reviews(world: FictoshopWorld) { return new ReviewsPage(world.page); }

async function ensureUser(world: FictoshopWorld): Promise<void> {
  world.state.user ??= await world.data.createUser(false);
}

async function ensureProduct(world: FictoshopWorld): Promise<void> {
  if (!world.state.products.review) {
    const reference = randomUUID().slice(0, 8);
    world.state.products.review = await world.data.createProduct(`Playwright product ${reference}`, "Product created for Playwright authentication scenarios.", 49.95, 7);
  }
}

Given("the customer is on the sign-in page", async function (this: FictoshopWorld) { await this.context?.clearCookies(); await auth(this).open(); });
When("the customer selects \"Log in\"", async function (this: FictoshopWorld) { await auth(this).openFromStorefront(); });
Then("the sign-in page shows username and password fields", async function (this: FictoshopWorld) { await auth(this).expectCredentialFields(); });
Then("it shows a \"Log in\" button", async function (this: FictoshopWorld) { await auth(this).expectLoginButton(); });
When("the customer submits without both credentials", async function (this: FictoshopWorld) { await auth(this).submit(); });
Then("a message asks for username and password", async function (this: FictoshopWorld) { await auth(this).expectMissingCredentials(); });
Then("the customer remains signed out", async function (this: FictoshopWorld) { await auth(this).expectSignedOut(); });
When("the customer submits invalid credentials", async function (this: FictoshopWorld) { await auth(this).submitInvalid(); });
Then("\"Invalid credentials\" is displayed", async function (this: FictoshopWorld) { await auth(this).expectInvalidCredentials(); });
Then("the customer remains on the sign-in page", async function (this: FictoshopWorld) { await auth(this).expectSignInPage(); });
Given("a regular user exists", async function (this: FictoshopWorld) { this.state.user = await this.data.createUser(false); });
When("the user signs in with valid credentials", async function (this: FictoshopWorld) { assert.ok(this.state.user); await auth(this).login(this.state.user); });
Then("the storefront opens", async function (this: FictoshopWorld) { await catalog(this).expectOpen(); });
Then("the navigation identifies the signed-in user", async function (this: FictoshopWorld) { assert.ok(this.state.user); await catalog(this).expectSignedInUser(this.state.user.username); });
Then("a \"Log out\" button is visible", async function (this: FictoshopWorld) { await catalog(this).expectLogoutButton(); });
Given("a superuser exists", async function (this: FictoshopWorld) { this.state.admin = await this.data.createUser(true); });
When("the superuser signs in with valid credentials", async function (this: FictoshopWorld) { assert.ok(this.state.admin); await auth(this).login(this.state.admin); });
Then("Django administration opens", async function (this: FictoshopWorld) { await new AdminPage(this.page).expectIndex(); });

Given("a regular user is signed in", async function (this: FictoshopWorld) {
  await ensureUser(this);
  await auth(this).login(this.state.user!);
  await catalog(this).expectOpen();
});
When("the user selects \"Log out\"", async function (this: FictoshopWorld) { await this.page.locator("header").getByRole("button", { name: "Log out", exact: true }).click(); });
Then("the navigation shows \"Log in\"", async function (this: FictoshopWorld) { await this.page.locator("header").getByRole("link", { name: "Log in", exact: true }).waitFor({ state: "visible" }); });
When("the customer opens a product detail page", async function (this: FictoshopWorld) { await ensureProduct(this); await reviews(this).open(this.state.products.review.id); });
Then("the review form is hidden", async function (this: FictoshopWorld) { await reviews(this).expectFormHidden(); });
Then("a sign-in link for leaving a review is visible", async function (this: FictoshopWorld) { await reviews(this).expectSignInLink(); });
When("the user opens a product detail page", async function (this: FictoshopWorld) { await ensureProduct(this); await reviews(this).open(this.state.products.review.id); });
Then("the rating picker and feedback field are visible", async function (this: FictoshopWorld) { await reviews(this).expectFields(); });
Then("the \"Submit review\" button is visible", async function (this: FictoshopWorld) { await reviews(this).expectSubmit(); });

Given("a regular user is signed in on a product detail page", async function (this: FictoshopWorld) {
  await ensureUser(this);
  await ensureProduct(this);
  await auth(this).login(this.state.user!);
  await catalog(this).expectOpen();
  await reviews(this).open(this.state.products.review.id);
});
When("the user submits feedback without selecting a rating", async function (this: FictoshopWorld) { await reviews(this).submitFeedbackWithoutRating("Feedback without a selected Playwright rating."); });
Then("the review is not created", async function (this: FictoshopWorld) { assert.equal(await this.data.countReviews(this.state.products.review.id, this.state.user!.username), 0); });
Then("a message asks the user to select a rating", async function (this: FictoshopWorld) { await reviews(this).expectRatingRequired(); });
When("the user selects a rating without entering feedback", async function (this: FictoshopWorld) { await reviews(this).selectRating(4); });
When("submits the review", async function (this: FictoshopWorld) { await reviews(this).submit(); });
Then("a message asks the user to provide feedback", async function (this: FictoshopWorld) { await reviews(this).expectFeedbackRequired(); });
When("the user selects a valid rating", async function (this: FictoshopWorld) { await reviews(this).selectRating(this.state.rating); });
When("enters feedback", async function (this: FictoshopWorld) { await reviews(this).enterFeedback(this.state.reviewComment); });
Then("the review appears with username, rating, comment, and date", async function (this: FictoshopWorld) { await reviews(this).expectReview(this.state.user!.username, this.state.rating, this.state.reviewComment); });
Then("the product rating summary is updated", async function (this: FictoshopWorld) { await reviews(this).expectRatingSummary(this.state.rating, 1); });

Given("the signed-in user has already reviewed the product", async function (this: FictoshopWorld) {
  await ensureUser(this);
  await ensureProduct(this);
  this.state.review = await this.data.createReview(this.state.products.review, this.state.user!, 2, "Original Playwright review.");
  await auth(this).login(this.state.user!);
  await reviews(this).open(this.state.products.review.id);
});
When("the user changes the rating and feedback", async function (this: FictoshopWorld) {
  await reviews(this).selectRating(this.state.updatedRating);
  await reviews(this).enterFeedback(this.state.updatedReviewComment);
});
When("selects \"Update review\"", async function (this: FictoshopWorld) { await reviews(this).submitUpdated(); });
Then("the existing review is updated", async function (this: FictoshopWorld) { await reviews(this).expectReview(this.state.user!.username, this.state.updatedRating, this.state.updatedReviewComment); });
Then("no second review from that user is created", async function (this: FictoshopWorld) { assert.equal(await this.data.countReviews(this.state.products.review.id, this.state.user!.username), 1); });
