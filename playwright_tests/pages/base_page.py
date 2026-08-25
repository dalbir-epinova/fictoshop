from playwright.sync_api import Page


class BasePage:
    """Shared helpers for storefront pages."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def url_for(self, path: str) -> str:
        formatted = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{formatted}"

    def goto(self, path: str = "/") -> None:
        self.page.goto(self.url_for(path), wait_until="networkidle")
