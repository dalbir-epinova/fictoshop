import re

from playwright.sync_api import Page, expect


class ProductDetailPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self, product_id: int) -> None:
        self.page.goto(f"{self.base_url}/products/{product_id}/view")

    def expect_review_form_hidden(self) -> None:
        expect(self.page.locator("form.review-form")).to_have_count(0)

    def expect_review_sign_in_link(self) -> None:
        reviews = self.page.locator("#reviews")
        sign_in_link = reviews.get_by_role("link", name="Sign in", exact=True)

        expect(sign_in_link).to_be_visible()
        expect(sign_in_link).to_have_attribute(
            "href", "/signin?next=" + self.page.url.removeprefix(self.base_url)
        )

    def expect_rating_and_feedback_fields(self) -> None:
        expect(self.page.get_by_role("radiogroup", name="Select a rating")).to_be_visible()
        expect(self.page.get_by_label("Feedback")).to_be_visible()

    def expect_submit_review_button(self) -> None:
        expect(self.page.get_by_role("button", name="Submit review", exact=True)).to_be_visible()

    def submit_feedback_without_rating(self, feedback: str) -> None:
        self.page.get_by_label("Feedback").fill(feedback)
        self.page.get_by_role("button", name="Submit review", exact=True).click()

    def expect_rating_required_message(self) -> None:
        expect(self.page.locator(".form-error")).to_have_text("Select a rating using the stars.")

    def select_rating(self, rating: int = 4) -> None:
        button = self.page.locator(f'.star-picker-button[data-index="{rating}"]')
        box = button.bounding_box()
        assert box is not None
        button.click(position={"x": box["width"] * 0.75, "y": box["height"] / 2})
        expect(self.page.locator("#review-rating-value")).to_have_value(f"{rating:.1f}")

    def submit_review(self) -> None:
        self.page.get_by_role("button", name="Submit review", exact=True).click()

    def submit_updated_review(self) -> None:
        self.page.get_by_role("button", name="Update review", exact=True).click()

    def expect_feedback_required_message(self) -> None:
        feedback = self.page.get_by_label("Feedback")
        assert feedback.evaluate("element => element.validity.valueMissing")
        assert feedback.evaluate("element => element.validationMessage")

    def enter_feedback(self, feedback: str) -> None:
        self.page.get_by_label("Feedback").fill(feedback)

    def expect_review(self, username: str, rating: int, comment: str) -> None:
        review = self.page.locator(".review-list li").filter(has_text=username)
        expect(review).to_have_count(1)
        expect(review).to_contain_text(comment)
        expect(review.locator(".review-rating")).to_have_attribute("data-rating", f"{rating:.1f}")
        expect(review.locator(".review-header span")).to_have_text(re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}$"))

    def expect_rating_summary(self, rating: int, review_count: int) -> None:
        summary = self.page.locator(".product-detail-rating")
        expect(summary).to_contain_text(f"{rating:.1f} / 5")
        expect(summary).to_contain_text(f"({review_count} reviews)")
