from playwright.sync_api import Page, expect


class SignInPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

        self.username = page.get_by_label("Username")
        self.password = page.get_by_label("Password")
        self.login_button = page.get_by_role("button", name="Log in")
        self.login_message = page.get_by_role("status")

    def open_from_storefront(self) -> None:
        self.page.goto(self.base_url)
        self.page.locator("header").get_by_role(
            "link", name="Log in", exact=True
        ).click()

    def open(self) -> None:
        self.page.goto(f"{self.base_url}/signin")

    def submit(self) -> None:
        self.login_button.click()

    def submit_invalid_credentials(self) -> None:
        self.username.fill("unknown-playwright-user")
        self.password.fill("Invalid-Playwright-Password!")
        self.submit()

    def login(self, username: str, password: str) -> None:
        self.open()
        self.username.fill(username)
        self.password.fill(password)
        self.submit()

    def expect_credentials_fields(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}/signin")
        expect(self.username).to_be_visible()
        expect(self.password).to_be_visible()

    def expect_login_button(self) -> None:
        expect(self.login_button).to_be_visible()

    def expect_missing_credentials_message(self) -> None:
        assert self.username.evaluate("element => element.validity.valueMissing")
        validation_message = self.username.evaluate(
            "element => element.validationMessage"
        )
        assert validation_message, "Expected a browser validation message for username"

    def expect_customer_signed_out(self) -> None:
        self.page.goto(self.base_url)
        expect(
            self.page.locator("header").get_by_role(
                "link", name="Log in", exact=True
            )
        ).to_be_visible()

    def expect_invalid_credentials_message(self) -> None:
        expect(self.login_message).to_have_text("Invalid credentials")

    def expect_sign_in_page(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}/signin")
        expect(self.username).to_be_visible()
        expect(self.password).to_be_visible()
