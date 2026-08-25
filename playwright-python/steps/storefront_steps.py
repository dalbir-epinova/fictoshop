from pytest_bdd import given, then, when

from pages.storefront_page import StorefrontPage


@given("the catalog contains available and unavailable products")
def catalog_has_mixed_products(storefront_catalog: dict[str, object]) -> None:
    assert storefront_catalog["available"].in_stock > 0
    assert storefront_catalog["unavailable"].in_stock == 0


@then('the heading "Welcome to FictoShop" is visible')
@then("the catalog is visible")
@then("at least one product card is displayed")
def storefront_core_visible(storefront_page: StorefrontPage) -> None:
    storefront_page.expect_heading_and_catalog()


@then("each product card shows its name")
@then("each product card shows its price")
@then("each product card shows its stock status")
def cards_show_purchase_info(storefront_page: StorefrontPage) -> None:
    storefront_page.expect_cards_have_purchasing_information()


@then('an available product has an enabled "Add to cart" button')
def available_product_add_enabled(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    storefront_page.expect_available_add_enabled(storefront_catalog["available"].name)


@when("the customer selects a product name")
def customer_selects_product(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    storefront_page.open_product(storefront_catalog["available"].name)


@then("the product detail page opens")
@then("the product name, description, price, rating summary, and reviews section are visible")
def product_detail_visible(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    storefront_page.expect_product_detail(storefront_catalog["available"])


@when("the customer searches for part of a product name")
def search_product_name(
    storefront_page: StorefrontPage,
    storefront_catalog: dict[str, object],
    storefront_state: dict[str, int],
) -> None:
    storefront_state["total"] = storefront_page.product_cards().count()
    storefront_page.search(storefront_catalog["name_query"])


@then("only matching products are displayed")
def only_matching_products(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    storefront_page.expect_only_product(storefront_catalog["available"].name)


@then("the catalog status shows the number of matches")
def catalog_match_count(storefront_page: StorefrontPage, storefront_state: dict[str, int]) -> None:
    storefront_page.expect_catalog_status(1, storefront_state["total"])


@when("the customer searches for text found only in a product description")
def search_description(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    storefront_page.search(storefront_catalog["description_query"])


@then("the matching product is displayed")
def description_product_displayed(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    storefront_page.expect_only_product(storefront_catalog["secondary"].name)


@when("the customer searches for text that is not in the catalog")
def search_no_match(storefront_page: StorefrontPage) -> None:
    storefront_page.search("no-such-product-playwright-9f31")


@then("no product cards are displayed")
@then("the empty search message is visible")
def no_products_displayed(storefront_page: StorefrontPage) -> None:
    storefront_page.expect_no_products()


@given("the customer has filtered the catalog using search")
def catalog_filtered(storefront_page: StorefrontPage, storefront_catalog: dict[str, object], storefront_state: dict[str, int]) -> None:
    storefront_state["total"] = storefront_page.product_cards().count()
    storefront_page.search(storefront_catalog["name_query"])


@when("the customer clears the search field")
def clear_search(storefront_page: StorefrontPage) -> None:
    storefront_page.clear_search()


@then("all products are displayed again")
def all_products_displayed(storefront_page: StorefrontPage, storefront_state: dict[str, int]) -> None:
    storefront_page.expect_product_count(storefront_state["total"])


@when('the customer selects "Price: Low to high"')
def sort_price_low(storefront_page: StorefrontPage) -> None:
    storefront_page.select_sort("Price: Low to high")


@then("product prices are ordered from lowest to highest")
def prices_low_to_high(storefront_page: StorefrontPage) -> None:
    prices = storefront_page.displayed_prices()
    assert prices == sorted(prices)


@when('the customer selects "Price: High to low"')
def sort_price_high(storefront_page: StorefrontPage) -> None:
    storefront_page.select_sort("Price: High to low")


@then("product prices are ordered from highest to lowest")
def prices_high_to_low(storefront_page: StorefrontPage) -> None:
    prices = storefront_page.displayed_prices()
    assert prices == sorted(prices, reverse=True)


@when('the customer selects "Stock level"')
def sort_stock(storefront_page: StorefrontPage) -> None:
    storefront_page.select_sort("Stock level")


@then("products are ordered from highest to lowest available stock")
def stocks_high_to_low(storefront_page: StorefrontPage) -> None:
    stocks = storefront_page.displayed_stocks()
    assert stocks == sorted(stocks, reverse=True)


@when('the customer enables "In stock only"')
def enable_stock_filter(storefront_page: StorefrontPage) -> None:
    storefront_page.enable_in_stock_only()


@then("products with zero available stock are hidden")
def zero_stock_hidden(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    storefront_page.expect_product_hidden(storefront_catalog["unavailable"].name)


@then('an out-of-stock product shows "Out of stock"')
@then("its quantity controls are disabled")
@then('its "Add to cart" button is disabled')
def out_of_stock_disabled(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    storefront_page.expect_out_of_stock_controls(storefront_catalog["unavailable"].name)


@when("the customer decreases the initial quantity")
def decrease_quantity(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    storefront_page.decrease_initial_quantity(storefront_catalog["available"].name)


@then("the quantity remains 1")
def quantity_remains_one(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    storefront_page.expect_quantity(storefront_catalog["available"].name, 1)


@when("the customer increases the quantity beyond available stock")
def increase_beyond_stock(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    product = storefront_catalog["available"]
    storefront_page.increase_beyond_stock(product.name, product.in_stock)


@then("the quantity does not exceed available stock")
def quantity_capped(storefront_page: StorefrontPage, storefront_catalog: dict[str, object]) -> None:
    product = storefront_catalog["available"]
    storefront_page.expect_quantity(product.name, product.in_stock)


@when('the customer selects "Explore the API"')
def select_explore_api(storefront_page: StorefrontPage) -> None:
    storefront_page.explore_api()


@then('the browser opens the "/products" endpoint')
def products_endpoint_opens(storefront_page: StorefrontPage) -> None:
    storefront_page.expect_products_endpoint()


@then("the response contains catalog products")
def api_contains_products(storefront_page: StorefrontPage) -> None:
    storefront_page.expect_api_catalog_products()
