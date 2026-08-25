from decimal import Decimal

from pytest_bdd import given, then, when

from clients.storefront_api import StorefrontApi
from pages.cart_page import CartPage


@given("the cart has been cleared")
def cart_has_been_cleared(storefront_api: StorefrontApi) -> None:
    response = storefront_api.delete("/cart")
    assert response.ok, response.text()


@given("the catalog contains an available product")
def catalog_contains_available_product(cart_products: dict[str, object]) -> None:
    assert cart_products["primary"].in_stock > 0


@given("the customer opens the storefront")
def customer_opens_storefront(cart_page: CartPage) -> None:
    cart_page.open()


@then("the floating cart is not visible")
@then("the floating cart is hidden")
def floating_cart_is_not_visible(cart_page: CartPage) -> None:
    cart_page.expect_cart_hidden()


@when("the customer adds 1 available product to the cart")
def customer_adds_one_available_product(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.add_product(cart_products["primary"].name, 1)


@then("the floating cart is visible")
def floating_cart_is_visible(cart_page: CartPage) -> None:
    cart_page.expect_cart_visible()


@then("it shows the product name")
def cart_shows_product_name(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.expect_product_in_cart(cart_products["primary"].name)


@then("it shows 1 total item")
def cart_shows_one_total_item(cart_page: CartPage) -> None:
    cart_page.expect_total_items(1)


@then("it shows the correct total price")
def cart_shows_correct_total(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.expect_grand_total(cart_products["primary"].price)


@given("the customer has added a product to the cart")
@given("the customer has added 1 product to the cart")
def customer_has_added_product(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.add_product(cart_products["primary"].name, 1)


@when("the customer scrolls to another part of the storefront")
def customer_scrolls_storefront(cart_page: CartPage) -> None:
    cart_page.scroll_to_top()


@then("the floating cart remains inside the viewport")
def floating_cart_remains_in_viewport(cart_page: CartPage) -> None:
    cart_page.expect_cart_inside_viewport()


@when("the customer selects quantity 3")
def customer_selects_quantity_three(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.select_quantity(cart_products["primary"].name, 3)


@when("adds the product to the cart")
def adds_selected_product(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.add_selected_product(cart_products["primary"].name)


@then("the cart line shows quantity 3")
@then("the line quantity is 3")
def cart_line_shows_quantity_three(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.expect_line_quantity(cart_products["primary"].name, 3)


@then("the total equals three times the unit price")
def total_equals_three_times_price(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.expect_grand_total(cart_products["primary"].price * 3)


@when("the customer adds 2 more of the same product")
def customer_adds_two_more(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.add_product(cart_products["primary"].name, 2)


@then("the cart contains one line for that product")
def cart_contains_one_line(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.expect_one_line(cart_products["primary"].name)


def _add_multiple_products(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.add_product(cart_products["primary"].name, 1)
    cart_page.add_product(cart_products["secondary"].name, 2)


@when("the customer adds multiple different products")
def customer_adds_multiple_products(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    _add_multiple_products(cart_page, cart_products)


@then("every selected product is shown in the cart")
def every_product_is_shown(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.expect_product_in_cart(cart_products["primary"].name)
    cart_page.expect_product_in_cart(cart_products["secondary"].name)


@then("total items equal the sum of all quantities")
def total_items_equal_quantity_sum(cart_page: CartPage) -> None:
    cart_page.expect_total_items(3)


@then("the grand total equals the sum of all line totals")
def grand_total_equals_line_totals(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    expected = cart_products["primary"].price + cart_products["secondary"].price * 2
    cart_page.expect_grand_total(expected)


@given("the cart contains two different products")
def cart_contains_two_products(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    _add_multiple_products(cart_page, cart_products)


@when("the customer removes one product")
def customer_removes_one_product(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.remove_product(cart_products["primary"].name)


@then("only that product disappears from the cart")
def only_removed_product_disappears(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.expect_product_not_in_cart(cart_products["primary"].name)
    cart_page.expect_product_in_cart(cart_products["secondary"].name)


@then("the totals are recalculated")
def totals_are_recalculated(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.expect_total_items(2)
    cart_page.expect_grand_total(cart_products["secondary"].price * 2)


@given("the cart contains products")
def cart_contains_products(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    _add_multiple_products(cart_page, cart_products)


@when('the customer selects "Clear"')
def customer_selects_clear(cart_page: CartPage) -> None:
    cart_page.clear()


@then("all cart lines are removed")
def all_cart_lines_are_removed(cart_page: CartPage) -> None:
    assert cart_page.page.locator("#cart-items .cart-item").count() == 0


@when("the customer reloads the storefront")
def customer_reloads_storefront(cart_page: CartPage) -> None:
    cart_page.reload()


@then("the same product and quantity remain in the cart")
def same_product_and_quantity_remain(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.expect_product_in_cart(cart_products["primary"].name)
    cart_page.expect_line_quantity(cart_products["primary"].name, 1)


@when("the customer attempts to add more units than available")
def customer_attempts_over_stock(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    product = cart_products["primary"]
    cart_page.attempt_to_add_over_stock(product.name, product.in_stock)


@then("the request is rejected")
def request_is_rejected(cart_page: CartPage) -> None:
    cart_page.expect_request_rejected()


@then("a stock error is displayed")
def stock_error_is_displayed(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    product = cart_products["primary"]
    cart_page.expect_stock_error(product.in_stock, product.name)


@then("the cart quantity is unchanged")
def cart_quantity_is_unchanged(cart_page: CartPage) -> None:
    cart_page.expect_total_items(0)


@when("the customer removes that product from the cart")
def customer_removes_added_product(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    cart_page.remove_product(cart_products["primary"].name)


@then("the catalog shows the original available stock")
def catalog_shows_original_stock(
    cart_page: CartPage, cart_products: dict[str, object]
) -> None:
    product = cart_products["primary"]
    cart_page.expect_catalog_stock(product.name, product.in_stock)
