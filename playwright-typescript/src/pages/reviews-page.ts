import assert from "node:assert/strict";
import { expect, type Page } from "@playwright/test";
import { settings } from "../support/settings.js";

export class ReviewsPage {
  constructor(private readonly page: Page) {}

  open(productId: number): Promise<unknown> { return this.page.goto(`${settings.baseUrl}/products/${productId}/view`); }
  expectFormHidden(): Promise<void> { return expect(this.page.locator("form.review-form")).toHaveCount(0); }

  async expectSignInLink(): Promise<void> {
    const link = this.page.locator("#reviews").getByRole("link", { name: "Sign in", exact: true });
    await expect(link).toBeVisible();
    await expect(link).toHaveAttribute("href", `/signin?next=${this.page.url().replace(settings.baseUrl, "")}`);
  }

  async expectFields(): Promise<void> {
    await expect(this.page.getByRole("radiogroup", { name: "Select a rating" })).toBeVisible();
    await expect(this.page.getByLabel("Feedback")).toBeVisible();
  }

  expectSubmit(): Promise<void> { return expect(this.page.getByRole("button", { name: "Submit review", exact: true })).toBeVisible(); }

  async submitFeedbackWithoutRating(feedback: string): Promise<void> {
    await this.page.getByLabel("Feedback").fill(feedback);
    await this.submit();
  }

  expectRatingRequired(): Promise<void> { return expect(this.page.locator(".form-error")).toHaveText("Select a rating using the stars."); }

  async selectRating(rating: number): Promise<void> {
    const button = this.page.locator(`.star-picker-button[data-index="${rating}"]`);
    const box = await button.boundingBox();
    assert.ok(box);
    await button.click({ position: { x: box.width * 0.75, y: box.height / 2 } });
    await expect(this.page.locator("#review-rating-value")).toHaveValue(rating.toFixed(1));
  }

  submit(): Promise<void> { return this.page.getByRole("button", { name: "Submit review", exact: true }).click(); }
  submitUpdated(): Promise<void> { return this.page.getByRole("button", { name: "Update review", exact: true }).click(); }

  async expectFeedbackRequired(): Promise<void> {
    const field = this.page.getByLabel("Feedback");
    assert.equal(await field.evaluate((element: HTMLTextAreaElement) => element.validity.valueMissing), true);
    assert.ok(await field.evaluate((element: HTMLTextAreaElement) => element.validationMessage));
  }

  enterFeedback(feedback: string): Promise<void> { return this.page.getByLabel("Feedback").fill(feedback); }

  async expectReview(username: string, rating: number, comment: string): Promise<void> {
    const review = this.page.locator(".review-list li").filter({ hasText: username });
    await expect(review).toHaveCount(1);
    await expect(review).toContainText(comment);
    await expect(review.locator(".review-rating")).toHaveAttribute("data-rating", rating.toFixed(1));
    await expect(review.locator(".review-header span")).toHaveText(/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}$/);
  }

  async expectRatingSummary(rating: number, count: number): Promise<void> {
    const summary = this.page.locator(".product-detail-rating");
    await expect(summary).toContainText(`${rating.toFixed(1)} / 5`);
    await expect(summary).toContainText(`(${count} reviews)`);
  }
}
