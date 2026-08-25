import json
import re
from pathlib import Path

from playwright.sync_api import Page, Route, expect


class ResponsiveMobilePage:
    def __init__(self, page: Page, base_url: str, project_root: Path):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.project_root = project_root
        self.requested_urls: list[str] = []
        self.configured_ios_base = ""

    def set_viewport(self, width: int, height: int) -> None:
        self.page.set_viewport_size({"width": width, "height": height})

    def expect_storefront_fits(self) -> None:
        heading = self.page.get_by_role("heading", name="Welcome to FictoShop")
        catalog = self.page.locator("#catalog")
        expect(heading).to_be_visible()
        expect(catalog).to_be_visible()
        self._expect_inside_document_width(heading)
        self._expect_inside_document_width(catalog)

    def expect_primary_controls_usable(self) -> None:
        assert self.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        for control in (
            self.page.get_by_role("link", name="Shop the catalog"),
            self.page.get_by_label("Search catalog"),
            self.page.get_by_label("Sort by"),
        ):
            expect(control).to_be_visible()
            expect(control).to_be_enabled()
            self._expect_inside_document_width(control)

    def _expect_inside_document_width(self, locator) -> None:
        box = locator.bounding_box()
        assert box is not None
        viewport_width = self.page.viewport_size["width"]
        metrics = self.page.evaluate("({ innerWidth, scrollX, visualWidth: visualViewport.width, visualOffset: visualViewport.offsetLeft })")
        scrollbar_gutter = max(0, metrics["innerWidth"] - metrics["visualWidth"])
        assert box["x"] >= -scrollbar_gutter, (
            f"Element starts outside viewport: box={box}, viewport={viewport_width}, metrics={metrics}"
        )
        assert box["x"] + box["width"] <= viewport_width, (
            f"Element ends outside viewport: box={box}, viewport={viewport_width}"
        )

    def expect_cart_width_inside_viewport(self) -> None:
        self.page.evaluate("window.scrollTo(0, window.scrollY)")
        cart = self.page.locator("#cart")
        expect(cart).to_be_visible()
        self._expect_inside_document_width(cart)

    def expect_cart_lines_scrollable(self) -> None:
        cart_items = self.page.locator("#cart-items")
        overflow = cart_items.evaluate("element => getComputedStyle(element).overflowY")
        max_height = cart_items.evaluate("element => getComputedStyle(element).maxHeight")
        assert overflow in {"auto", "scroll"}
        assert max_height != "none"

    def expect_cart_actions_usable(self) -> None:
        for name in ("Clear", "Checkout"):
            button = self.page.get_by_role("button", name=name, exact=True)
            expect(button).to_be_visible()
            expect(button).to_be_enabled()
            self._expect_inside_document_width(button)

    def expect_checkout_single_column(self) -> None:
        form = self.page.locator(".shipping-form")
        columns = form.evaluate("element => getComputedStyle(element).gridTemplateColumns")
        assert len(columns.split()) == 1, f"Expected one column, got {columns}"

    def expect_checkout_actions_usable(self) -> None:
        for control in (
            self.page.get_by_role("link", name="Back to cart", exact=True),
            self.page.get_by_role("button", name="Place order", exact=True),
        ):
            expect(control).to_be_visible()
            self._expect_inside_document_width(control)

    def _bundle_route(self, route: Route) -> None:
        self.requested_urls.append(route.request.url)
        if route.request.url.endswith("/products"):
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps([{
                    "id": 9001,
                    "name": "Bundled mobile product",
                    "description": "Product returned to a mobile bundle test.",
                    "price": 19.95,
                    "in_stock": 5,
                    "image_url": "",
                    "average_rating": None,
                    "review_count": 0,
                }]),
            )
        elif route.request.url.endswith("/cart"):
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"items": [], "total_items": 0, "grand_total": 0}),
            )
        else:
            route.continue_()

    def load_android_bundle(self) -> None:
        index = self.project_root / "android-app/app/src/main/assets/index.html"
        assert index.exists()
        self.page.route("http://10.0.2.2:8000/**", self._bundle_route)
        self.page.goto(index.as_uri())
        expect(self.page.locator("#product-grid")).to_have_attribute("aria-busy", "false")

    def expect_android_host_base(self) -> None:
        assert any(url.startswith("http://10.0.2.2:8000/products") for url in self.requested_urls)

    def load_ios_bundle(self) -> None:
        plist = (self.project_root / "ios-app/fictoshop/Info.plist").read_text(encoding="utf-8")
        swift = (self.project_root / "ios-app/fictoshop/fictoshop/WebView.swift").read_text(encoding="utf-8")
        project = (self.project_root / "ios-app/fictoshop/fictoshop.xcodeproj/project.pbxproj").read_text(encoding="utf-8")
        assert "<key>API_BASE_URL</key>" in plist
        assert 'object(forInfoDictionaryKey: "API_BASE_URL")' in swift
        match = re.search(r'API_BASE_URL = "([^"]+)";', project)
        assert match, "API_BASE_URL is not configured in the Xcode project"
        self.configured_ios_base = match.group(1).rstrip("/")
        self.page.add_init_script(
            f'window.__FICTO_API_BASE__ = "{self.configured_ios_base}";'
        )
        self.page.route(f"{self.configured_ios_base}/**", self._bundle_route)
        index = self.project_root / "mobile-web/index.html"
        self.page.goto(index.as_uri())
        expect(self.page.locator("#product-grid")).to_have_attribute("aria-busy", "false")

    def expect_ios_configured_base(self) -> None:
        assert any(url.startswith(f"{self.configured_ios_base}/products") for url in self.requested_urls)

    def expect_bundle_product(self) -> None:
        expect(self.page.locator(".product-card").filter(has_text="Bundled mobile product")).to_be_visible()
