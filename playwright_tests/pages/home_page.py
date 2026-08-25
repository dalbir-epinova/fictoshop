from playwright.sync_api import expect

from .base_page import BasePage


class HomePage(BasePage):
    """Storefront homepage interactions."""

    path = "/"

    def open(self) -> None:
        self.goto(self.path)
        expect(self.page.locator("#catalog-title")).to_be_visible(timeout=10000)

    def assert_hero_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Welcome to FictoShop")).to_be_visible(timeout=5000)
        expect(self.page.get_by_text("Your provider of sports equipment")).to_be_visible(timeout=5000)

    def wait_for_products(self) -> None:
        self.page.wait_for_selector(".product-card", timeout=15000)

    def assert_product_grid_populated(self) -> None:
        self.wait_for_products()
        expect(self.page.locator(".product-card").first).to_be_visible()

    def wait_for_cart_ready(self) -> None:
        self.page.wait_for_selector("#cart-loading", state="hidden", timeout=10000)

    def add_first_product_to_cart(self) -> str:
        self.assert_product_grid_populated()
        self.wait_for_cart_ready()
        card = self.page.locator(".product-card").first
        product_name = card.locator("h3").inner_text().strip()
        add_button = card.get_by_role("button", name="Add to cart")
        add_button.click()
        expect(self.page.locator("#cart-total-items")).not_to_have_text(r"^0\\s*$", timeout=10000)
        expect(self.page.locator("#cart-empty")).to_be_hidden(timeout=5000)
        return product_name

    def cart_items_count(self) -> int:
        self.wait_for_cart_ready()
        text = self.page.locator("#cart-total-items").inner_text().strip()
        try:
            return int(text)
        except ValueError:
            return 0

    def cart_grand_total(self) -> str:
        self.wait_for_cart_ready()
        return self.page.locator("#cart-grand-total").inner_text().strip()
