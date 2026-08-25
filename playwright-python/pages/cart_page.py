from decimal import Decimal

from playwright.sync_api import Page, expect


class CartPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.cart = page.locator("#cart")
        self.last_cart_response_status: int | None = None

    def open(self) -> None:
        self.page.goto(self.base_url)
        expect(self.page.locator("#product-grid")).to_have_attribute(
            "aria-busy", "false"
        )

    def product_card(self, product_name: str):
        return self.page.locator(".product-card").filter(has_text=product_name)

    def cart_line(self, product_name: str):
        return self.page.locator("#cart-items .cart-item").filter(
            has_text=product_name
        )

    def add_product(self, product_name: str, quantity: int = 1) -> None:
        card = self.product_card(product_name)
        if card.count() == 0:
            self.open()
            card = self.product_card(product_name)
        expect(card).to_have_count(1)
        quantity_input = card.locator(".quantity-input")
        quantity_input.fill(str(quantity))
        quantity_input.dispatch_event("change")
        card.get_by_role("button", name="Add to cart", exact=True).click()
        expect(self.page.locator("#app-toast")).to_contain_text(
            f"Added {quantity}"
        )
        expect(self.page.locator("#app-toast")).to_contain_text(product_name)
        expect(self.cart_line(product_name)).to_be_visible()

    def select_quantity(self, product_name: str, quantity: int) -> None:
        card = self.product_card(product_name)
        quantity_input = card.locator(".quantity-input")
        quantity_input.fill(str(quantity))
        quantity_input.dispatch_event("change")
        expect(quantity_input).to_have_value(str(quantity))

    def add_selected_product(self, product_name: str) -> None:
        card = self.product_card(product_name)
        quantity = int(card.locator(".quantity-input").input_value())
        card.get_by_role("button", name="Add to cart", exact=True).click()
        expect(self.page.locator("#app-toast")).to_contain_text(
            f"Added {quantity}"
        )
        expect(self.page.locator("#app-toast")).to_contain_text(product_name)
        expect(self.cart_line(product_name)).to_be_visible()

    def expect_cart_hidden(self) -> None:
        expect(self.cart).to_be_hidden()

    def expect_cart_visible(self) -> None:
        expect(self.cart).to_be_visible()

    def expect_product_in_cart(self, product_name: str) -> None:
        expect(self.cart_line(product_name)).to_be_visible()

    def expect_product_not_in_cart(self, product_name: str) -> None:
        expect(self.cart_line(product_name)).to_have_count(0)

    def expect_total_items(self, quantity: int) -> None:
        expect(self.page.locator("#cart-total-items")).to_have_text(str(quantity))

    def expect_grand_total(self, total: Decimal) -> None:
        expect(self.page.locator("#cart-grand-total")).to_have_text(
            f"${total:.2f}"
        )

    def expect_line_quantity(self, product_name: str, quantity: int) -> None:
        expect(self.cart_line(product_name).locator(".muted")).to_contain_text(
            f"{quantity} "
        )

    def expect_one_line(self, product_name: str) -> None:
        expect(self.cart_line(product_name)).to_have_count(1)

    def scroll_to_top(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def expect_cart_inside_viewport(self) -> None:
        box = self.cart.bounding_box()
        viewport = self.page.viewport_size
        assert box is not None, "Floating cart has no visible bounding box"
        assert viewport is not None, "Browser viewport size is unavailable"
        assert box["x"] >= 0 and box["y"] >= 0
        assert box["x"] + box["width"] <= viewport["width"]
        assert box["y"] + box["height"] <= viewport["height"]

    def remove_product(self, product_name: str) -> None:
        line = self.cart_line(product_name)
        line.get_by_role("button", name="Remove", exact=True).click()
        expect(line).to_have_count(0)

    def clear(self) -> None:
        self.page.get_by_role("button", name="Clear", exact=True).click()
        self.expect_cart_hidden()

    def reload(self) -> None:
        self.page.reload()
        expect(self.page.locator("#product-grid")).to_have_attribute(
            "aria-busy", "false"
        )

    def attempt_to_add_over_stock(self, product_name: str, stock: int) -> None:
        card = self.product_card(product_name)
        quantity_input = card.locator(".quantity-input")
        attempted_quantity = stock + 1
        quantity_input.evaluate(
            "(element, value) => { element.max = value; element.value = value; }",
            str(attempted_quantity),
        )
        with self.page.expect_response(
            lambda response: response.url.rstrip("/").endswith("/cart")
            and response.request.method == "POST"
        ) as response_info:
            card.get_by_role("button", name="Add to cart", exact=True).click()
        self.last_cart_response_status = response_info.value.status

    def expect_request_rejected(self) -> None:
        assert self.last_cart_response_status == 400

    def expect_stock_error(self, available: int, product_name: str) -> None:
        expect(self.page.locator("#cart-message")).to_have_text(
            f"Only {available} units left of {product_name}"
        )

    def expect_catalog_stock(self, product_name: str, stock: int) -> None:
        expect(self.product_card(product_name).locator(".badge")).to_have_text(
            f"{stock} in stock"
        )
