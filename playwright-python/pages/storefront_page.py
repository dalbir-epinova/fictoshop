import re

from playwright.sync_api import Page, expect


class StorefrontPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        self.page.goto(self.base_url)

    def expect_open(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}/")

    def expect_signed_in_user(self, username: str) -> None:
        expect(self.page.locator(".nav-user")).to_have_text(
            f"Signed in as {username}"
        )

    def expect_logout_button(self) -> None:
        expect(
            self.page.locator("header").get_by_role(
                "button", name="Log out", exact=True
            )
        ).to_be_visible()

    def expect_product_visible(self, product_name: str) -> None:
        product_card = self.page.locator(".product-card").filter(has_text=product_name)
        expect(product_card).to_have_count(1)
        expect(product_card).to_be_visible()

    def expect_product_image_visible(self, product_name: str) -> None:
        product_card = self.page.locator(".product-card").filter(has_text=product_name)
        image = product_card.get_by_role("img", name=f"{product_name} photo")

        image.scroll_into_view_if_needed()
        expect(image).to_be_visible()
        expect(image).to_have_attribute("src", re.compile(r"/images/uploads/"))
        expect(image).to_have_js_property("complete", True, timeout=15_000)
        assert image.evaluate("element => element.naturalWidth > 0")

    def expect_product_stock(self, product_name: str, stock: int) -> None:
        product_card = self.page.locator(".product-card").filter(has_text=product_name)
        expect(product_card.locator(".badge")).to_have_text(f"{stock} in stock")

    def product_cards(self):
        return self.page.locator(".product-card")

    def product_card(self, product_name: str):
        return self.product_cards().filter(
            has=self.page.get_by_role("heading", name=product_name, exact=True)
        )

    def _wait_for_catalog(self) -> None:
        expect(self.page.locator("#product-grid")).to_have_attribute(
            "aria-busy", "false"
        )

    def expect_heading_and_catalog(self) -> None:
        self._wait_for_catalog()
        expect(
            self.page.get_by_role("heading", name="Welcome to FictoShop", exact=True)
        ).to_be_visible()
        expect(self.page.locator("#catalog")).to_be_visible()
        expect(self.product_cards()).not_to_have_count(0)

    def expect_cards_have_purchasing_information(self) -> None:
        self._wait_for_catalog()
        count = self.product_cards().count()
        assert count > 0
        for index in range(count):
            card = self.product_cards().nth(index)
            expect(card.locator("h3")).not_to_have_text("")
            expect(card.locator(".product-price")).to_contain_text("$")
            expect(card.locator(".badge")).to_be_visible()

    def expect_available_add_enabled(self, product_name: str) -> None:
        button = self.product_card(product_name).get_by_role(
            "button", name="Add to cart", exact=True
        )
        expect(button).to_be_enabled()

    def open_product(self, product_name: str) -> None:
        self.product_card(product_name).locator(
            ".product-card-title"
        ).click()

    def expect_product_detail(self, product: object) -> None:
        expect(self.page).to_have_url(
            re.compile(rf"/products/{product.id}/view$")
        )
        expect(self.page.get_by_role("heading", name=product.name, exact=True)).to_be_visible()
        expect(self.page.get_by_text(product.description, exact=True)).to_be_visible()
        expect(self.page.locator(".product-detail-price")).to_contain_text(
            f"${product.price:.2f}"
        )
        expect(self.page.locator(".product-detail-rating")).to_be_visible()
        expect(self.page.locator("#reviews")).to_be_visible()

    def search(self, query: str) -> None:
        self.page.locator("#product-search").fill(query)

    def expect_only_product(self, product_name: str) -> None:
        expect(self.product_cards()).to_have_count(1)
        expect(self.product_cards().first.locator("h3")).to_have_text(product_name)

    def expect_catalog_status(self, matches: int, total: int) -> None:
        expect(self.page.locator("#product-status")).to_contain_text(
            f"Showing {matches} of {total}"
        )

    def expect_no_products(self) -> None:
        expect(self.product_cards()).to_have_count(0)
        expect(self.page.locator("#product-empty")).to_be_visible()

    def clear_search(self) -> None:
        self.page.locator("#product-search").fill("")

    def expect_product_count(self, count: int) -> None:
        expect(self.product_cards()).to_have_count(count)

    def select_sort(self, label: str) -> None:
        self.page.locator("#product-sort").select_option(label=label)

    def displayed_prices(self) -> list[float]:
        return [
            float(value.replace("$", "").replace(",", ""))
            for value in self.product_cards().locator(".product-price").all_text_contents()
        ]

    def displayed_stocks(self) -> list[int]:
        return [
            int(card.locator(".quantity-input").get_attribute("max") or "0")
            for card in [self.product_cards().nth(i) for i in range(self.product_cards().count())]
        ]

    def enable_in_stock_only(self) -> None:
        self.page.locator("#product-in-stock").check()

    def expect_product_hidden(self, product_name: str) -> None:
        expect(self.product_card(product_name)).to_have_count(0)

    def expect_out_of_stock_controls(self, product_name: str) -> None:
        card = self.product_card(product_name)
        expect(card.locator(".badge")).to_have_text("Out of stock")
        expect(card.locator(".quantity-input")).to_be_disabled()
        expect(card.locator(".quantity-btn").first).to_be_disabled()
        expect(card.locator(".quantity-btn").last).to_be_disabled()
        expect(card.get_by_role("button", name="Add to cart", exact=True)).to_be_disabled()

    def decrease_initial_quantity(self, product_name: str) -> None:
        self.product_card(product_name).locator(
            ".quantity-btn"
        ).first.click()

    def expect_quantity(self, product_name: str, quantity: int) -> None:
        expect(
            self.product_card(product_name).locator(".quantity-input")
        ).to_have_value(str(quantity))

    def increase_beyond_stock(self, product_name: str, stock: int) -> None:
        plus = self.product_card(product_name).locator(
            ".quantity-btn"
        ).last
        for _ in range(stock + 2):
            plus.click()

    def explore_api(self) -> None:
        self.page.get_by_role("link", name="Explore the API", exact=True).click()

    def expect_products_endpoint(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}/products")

    def expect_api_catalog_products(self) -> None:
        body = self.page.locator("body").inner_text()
        assert '"name"' in body or "name" in body
