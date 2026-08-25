import os
from typing import Dict, Iterator

import pytest
from playwright.sync_api import APIRequestContext, BrowserContext, Page, Playwright, sync_playwright


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--base-url",
        action="store",
        default=os.getenv("FICTOSHOP_BASE_URL", "http://127.0.0.1:8000"),
        help="Base URL for the storefront under test.",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run Playwright in headed mode (default is headless).",
    )


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config) -> str:
    return str(pytestconfig.getoption("--base-url")).rstrip("/")


@pytest.fixture(scope="session")
def playwright_instance() -> Iterator[Playwright]:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def api_context(playwright_instance: Playwright, base_url: str) -> Iterator[APIRequestContext]:
    context = playwright_instance.request.new_context(base_url=base_url)
    yield context
    context.dispose()


@pytest.fixture
def browser_context(
    playwright_instance: Playwright, base_url: str, pytestconfig: pytest.Config
) -> Iterator[BrowserContext]:
    headless = not bool(pytestconfig.getoption("--headed"))
    browser = playwright_instance.chromium.launch(headless=headless)
    context = browser.new_context(base_url=base_url)
    yield context
    context.close()
    browser.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Iterator[Page]:
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture
def cart_state() -> Dict[str, str]:
    return {}
