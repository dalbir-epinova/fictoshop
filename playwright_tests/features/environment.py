import os
from typing import Dict

from playwright.sync_api import APIRequestContext, Browser, BrowserContext, Page, Playwright, sync_playwright

from playwright_tests.pages.home_page import HomePage

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def _headed(userdata: Dict[str, str]) -> bool:
    """Derive headed mode from either environment or Behave userdata."""
    env_value = os.getenv("FICTOSHOP_HEADED", "")
    if env_value:
        return env_value.lower() in {"1", "true", "yes", "on"}
    cli_value = userdata.get("headed", "")
    return cli_value.lower() in {"1", "true", "yes", "on"}


def before_all(context) -> None:
    playwright: Playwright = sync_playwright().start()
    base_url = os.getenv("FICTOSHOP_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    context.playwright = playwright
    context.base_url = base_url
    context.headed = _headed(context.config.userdata)
    context.api_context = playwright.request.new_context(base_url=base_url)


def before_scenario(context, scenario) -> None:
    browser: Browser = context.playwright.chromium.launch(headless=not context.headed)
    browser_context: BrowserContext = browser.new_context(base_url=context.base_url)
    page: Page = browser_context.new_page()

    context.browser = browser
    context.browser_context = browser_context
    context.page = page
    context.cart_state = {}
    context.home_page = HomePage(page, context.base_url)


def after_scenario(context, scenario) -> None:
    # Close in reverse order of creation to keep resources tidy.
    if getattr(context, "page", None):
        context.page.close()
    if getattr(context, "browser_context", None):
        context.browser_context.close()
    if getattr(context, "browser", None):
        context.browser.close()


def after_all(context) -> None:
    if getattr(context, "api_context", None):
        context.api_context.dispose()
    if getattr(context, "playwright", None):
        context.playwright.stop()
