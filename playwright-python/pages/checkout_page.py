import re
from decimal import Decimal

from playwright.sync_api import Browser, Page, expect


class CheckoutPage:
    FIELD_IDS = {
        "Full name": "#id_full_name",
        "Email": "#id_email",
        "Phone": "#id_phone",
        "Address": "#id_address",
        "Postal code": "#id_postal_code",
        "City": "#id_city",
        "Country": "#id_country",
    }

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.order_id: int | None = None

    def open(self) -> None:
        self.page.goto(f"{self.base_url}/checkout")

    def expect_storefront(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}/")

    def expect_shipping_page(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}/checkout")
        expect(self.page.get_by_role("heading", name="Shipping details")).to_be_visible()

    def expect_shipping_fields(self) -> None:
        for label in ("Full name", "Email", "Phone", "Address", "Postal code", "City", "Country"):
            expect(self.page.get_by_label(label, exact=True)).to_be_visible()

    def expect_summary(self, product_name: str, quantity: int, total: Decimal) -> None:
        summary = self.page.locator(".checkout-summary")
        expect(summary).to_contain_text(product_name)
        expect(summary).to_contain_text(f"{quantity} ")
        expect(summary).to_contain_text(f"${total:.2f}")

    def back_to_cart(self) -> None:
        self.page.get_by_role("link", name="Back to cart", exact=True).click()

    def fill_shipping(self, data: dict[str, str], missing: str | None = None) -> None:
        for label, value in data.items():
            self.page.get_by_label(label, exact=True).fill("" if label == missing else value)

    def place_order(self) -> None:
        self.page.get_by_role("button", name="Place order", exact=True).click()

    def expect_field_validation(self, label: str) -> None:
        assert self.page.url == f"{self.base_url}/checkout", (
            f"Expected checkout validation page, got {self.page.url}"
        )
        field = self.page.locator(self.FIELD_IDS[label])
        expect(field).to_be_visible()
        assert not field.evaluate("element => element.validity.valid")
        assert field.evaluate("element => element.validationMessage")

    def expect_checkout_url(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}/checkout")

    def expect_confirmation(self) -> None:
        expect(self.page).to_have_url(re.compile(r"/orders/\d+/confirmation$"))
        match = re.search(r"/orders/(\d+)/confirmation$", self.page.url)
        assert match
        self.order_id = int(match.group(1))
        expect(
            self.page.get_by_role(
                "heading", name="Your order was placed successfully", exact=True
            )
        ).to_be_visible()

    def expect_order_number(self) -> None:
        expect(self.page.locator(".confirmation > .eyebrow")).to_have_text(
            re.compile(r"Order #\d+")
        )

    def expect_success_message(self) -> None:
        expect(
            self.page.get_by_role(
                "heading", name="Your order was placed successfully", exact=True
            )
        ).to_be_visible()

    def expect_order_items(self, expected: list[dict[str, object]]) -> None:
        for item in expected:
            line = self.page.locator(".confirmation .summary-lines li").filter(
                has_text=str(item["name"])
            )
            expect(line).to_contain_text(str(item["quantity"]))
            expect(line).to_contain_text(f'${item["unit_price"]:.2f}')
            expect(line).to_contain_text(f'${item["line_total"]:.2f}')

    def expect_order_total(self, total: Decimal) -> None:
        expect(self.page.locator(".confirmation .summary-total")).to_contain_text(
            f"${total:.2f}"
        )

    def expect_shipping_summary(self, data: dict[str, str]) -> None:
        summary = self.page.locator('[aria-labelledby="delivery-title"]')
        for value in data.values():
            expect(summary).to_contain_text(value)

    def back_to_storefront(self) -> None:
        self.page.get_by_role("link", name="Back to storefront", exact=True).click()

    def expect_storefront_catalog(self) -> None:
        expect(self.page.get_by_role("heading", name="Welcome to FictoShop")).to_be_visible()
        expect(self.page.get_by_role("heading", name="Our products")).to_be_visible()

    def expect_insufficient_stock(self, product_name: str) -> None:
        expect(self.page.locator(".form-error")).to_contain_text(
            f"There is no longer enough stock for {product_name}."
        )

    def confirmation_denied_in_another_session(self, browser: Browser) -> tuple[int, str]:
        context = browser.new_context()
        try:
            response = context.new_page().goto(self.page.url)
            assert response is not None
            return response.status, response.text()
        finally:
            context.close()
