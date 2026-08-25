from playwright.sync_api import Page, expect


class AdminPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.username = page.get_by_label("Username")
        self.password = page.get_by_label("Password")
        self.login_button = page.get_by_role("button", name="Log in")

    def open(self) -> None:
        self.page.goto(f"{self.base_url}/admin/")

    def login(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()

    def expect_login_page(self) -> None:
        expect(self.username).to_be_visible()
        expect(self.password).to_be_visible()
        expect(self.login_button).to_be_visible()

    def expect_admin_index(self) -> None:
        expect(
            self.page.get_by_role("heading", name="Site administration")
        ).to_be_visible()

    def expect_products_and_orders(self) -> None:
        expect(self.page.get_by_role("link", name="Products", exact=True)).to_be_visible()
        expect(self.page.get_by_role("link", name="Orders", exact=True)).to_be_visible()

    def open_new_product_form(self) -> None:
        self.page.goto(f"{self.base_url}/admin/shop/product/add/")

    def fill_product_fields(self, product: dict[str, object]) -> None:
        self.page.get_by_label("Name:").fill(str(product["name"]))
        self.page.get_by_label("Description:").fill(str(product["description"]))
        self.page.get_by_label("Price:").fill(str(product["price"]))
        self.page.get_by_label("In stock:").fill(str(product["in_stock"]))

    def upload_product_image(self, image_path: str) -> None:
        self.page.get_by_label("Image:").set_input_files(image_path)

    def save_product(self) -> None:
        self.page.get_by_role("button", name="Save", exact=True).click()

    def open_product_change_form(self, product_id: int) -> None:
        self.page.goto(f"{self.base_url}/admin/shop/product/{product_id}/change/")

    def change_product_stock(self, stock: int) -> None:
        stock_field = self.page.get_by_label("In stock:")
        stock_field.fill(str(stock))
        self.save_product()

    def expect_product_listed(self, product_name: str) -> None:
        product_link = self.page.locator("#result_list").get_by_role(
            "link",
            name=product_name,
            exact=True,
        )
        expect(product_link).to_be_visible()

    def open_order_change_form(self, order_id: int) -> None:
        self.page.goto(f"{self.base_url}/admin/shop/order/{order_id}/change/")

    def expect_order_details(self, order: object) -> None:
        expect(self.page.get_by_label("Full name:")).to_have_value(order.full_name)
        expect(self.page.get_by_label("Email:")).to_have_value(order.email)
        expect(self.page.get_by_label("Phone:")).to_have_value(order.phone)
        expect(self.page.get_by_label("Address:")).to_have_value(order.address)
        expect(self.page.get_by_label("Postal code:")).to_have_value(order.postal_code)
        expect(self.page.get_by_label("City:")).to_have_value(order.city)
        expect(self.page.get_by_label("Country:")).to_have_value(order.country)

        content = self.page.locator("#content-main")
        expect(content).to_contain_text(str(order.total_amount))
        expect(content.locator(".field-created_at .readonly")).not_to_be_empty()

    def expect_order_items_read_only(self, items: list[object]) -> None:
        inline_group = self.page.locator("#items-group")
        for item in items:
            expect(inline_group).to_contain_text(item.product_name)
            expect(inline_group).to_contain_text(str(item.unit_price))
            expect(inline_group).to_contain_text(str(item.quantity))
            expect(inline_group).to_contain_text(str(item.line_total))

        for field_name in ("product_name", "unit_price", "quantity", "line_total"):
            expect(
                inline_group.locator(f'input[name$="-{field_name}"]')
            ).to_have_count(0)
