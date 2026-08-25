from decimal import Decimal

from pytest_bdd import parsers, then, when, given

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


@when('the customer opens "/checkout" with an empty cart')
def open_empty_checkout(checkout_page: CheckoutPage) -> None:
    checkout_page.open()


@then("the customer is redirected to the storefront")
def redirected_to_storefront(checkout_page: CheckoutPage) -> None:
    checkout_page.expect_storefront()


@when('the customer selects "Checkout"')
def select_checkout(cart_page: CartPage) -> None:
    cart_page.page.get_by_role("button", name="Checkout", exact=True).click()


@then("the shipping details page opens")
def shipping_page_opens(checkout_page: CheckoutPage) -> None:
    checkout_page.expect_shipping_page()


@then("fields for name, email, phone, address, postal code, city, and country are visible")
def shipping_fields_visible(checkout_page: CheckoutPage) -> None:
    checkout_page.expect_shipping_fields()


@then("the ordered product, quantity, and total are visible")
def checkout_summary_visible(checkout_page: CheckoutPage, available_product: object) -> None:
    checkout_page.expect_summary(available_product.name, 1, available_product.price)


@given("the customer is on checkout with a product in the cart")
def customer_on_checkout(cart_page: CartPage, checkout_page: CheckoutPage, available_product: object) -> None:
    cart_page.open()
    cart_page.add_product(available_product.name, 1)
    checkout_page.open()


@when('the customer selects "Back to cart"')
def select_back_to_cart(checkout_page: CheckoutPage) -> None:
    checkout_page.back_to_cart()


@then("the storefront opens at the cart")
def storefront_opens_at_cart(cart_page: CartPage) -> None:
    expect_url = f"{cart_page.base_url}/#cart"
    assert cart_page.page.url == expect_url


@then("the product remains in the cart")
def product_remains_in_cart(cart_page: CartPage, available_product: object) -> None:
    cart_page.expect_product_in_cart(available_product.name)


@when(parsers.parse('the customer submits valid shipping details except for "{field}"'))
def submit_shipping_except_field(checkout_page: CheckoutPage, shipping_data: dict[str, str], field: str) -> None:
    checkout_page.fill_shipping(shipping_data, missing=field)
    checkout_page.place_order()


@then("the order is not placed")
@then("no order is created")
def order_not_created(checkout_state: dict[str, object]) -> None:
    from shop.models import Order
    assert set(Order.objects.values_list("id", flat=True)) == checkout_state["initial_order_ids"]


@then(parsers.parse('a validation message is shown for "{field}"'))
def field_validation_shown(checkout_page: CheckoutPage, field: str) -> None:
    checkout_page.expect_field_validation(field)


@when("the customer enters an invalid email address")
def enter_invalid_email(checkout_page: CheckoutPage, shipping_data: dict[str, str]) -> None:
    invalid = dict(shipping_data)
    invalid["Email"] = "invalid-email"
    checkout_page.fill_shipping(invalid)


@when("attempts to place the order")
def attempts_place_order(checkout_page: CheckoutPage) -> None:
    checkout_page.place_order()


@then("the email field reports a validation error")
def email_validation_error(checkout_page: CheckoutPage) -> None:
    checkout_page.expect_field_validation("Email")


@when("the customer enters valid shipping details")
def enter_valid_shipping(checkout_page: CheckoutPage, shipping_data: dict[str, str]) -> None:
    checkout_page.fill_shipping(shipping_data)


@when('selects "Place order"')
def selects_place_order(checkout_page: CheckoutPage) -> None:
    checkout_page.place_order()


@then("an order confirmation page opens")
def confirmation_opens(checkout_page: CheckoutPage) -> None:
    checkout_page.expect_confirmation()


@then("a unique order number is displayed")
def order_number_displayed(checkout_page: CheckoutPage) -> None:
    checkout_page.expect_order_number()


@then("the page confirms that the order was placed successfully")
def placed_successfully(checkout_page: CheckoutPage) -> None:
    checkout_page.expect_success_message()


def _place_order(checkout_page: CheckoutPage, cart_page: CartPage, shipping_data: dict[str, str], products: list[tuple[object, int]]) -> None:
    cart_page.open()
    for product, quantity in products:
        cart_page.add_product(product.name, quantity)
    checkout_page.open()
    checkout_page.fill_shipping(shipping_data)
    checkout_page.place_order()
    checkout_page.expect_confirmation()


@when("the customer places a valid order containing multiple products")
def place_multiple_order(checkout_page: CheckoutPage, cart_page: CartPage, shipping_data: dict[str, str], available_product: object, checkout_secondary_product: object, checkout_state: dict[str, object]) -> None:
    _place_order(checkout_page, cart_page, shipping_data, [(available_product, 1), (checkout_secondary_product, 2)])
    checkout_state["ordered"] = [(available_product, 1), (checkout_secondary_product, 2)]


@then("every product name, unit price, quantity, and line total is shown")
def all_order_item_details(checkout_page: CheckoutPage, checkout_state: dict[str, object]) -> None:
    expected = [{"name": p.name, "quantity": q, "unit_price": p.price, "line_total": p.price * q} for p, q in checkout_state["ordered"]]
    checkout_page.expect_order_items(expected)


@then("the correct order total is shown")
def correct_order_total(checkout_page: CheckoutPage, checkout_state: dict[str, object]) -> None:
    total = sum((p.price * q for p, q in checkout_state["ordered"]), Decimal("0.00"))
    checkout_page.expect_order_total(total)


@when("the customer places an order with valid shipping details")
@when("the customer places a valid order")
def place_valid_order(checkout_page: CheckoutPage, cart_page: CartPage, shipping_data: dict[str, str], available_product: object) -> None:
    _place_order(checkout_page, cart_page, shipping_data, [(available_product, 2)])


@then("the confirmation shows the customer's name")
def confirmation_shows_name(checkout_page: CheckoutPage, shipping_data: dict[str, str]) -> None:
    checkout_page.expect_shipping_summary({"Full name": shipping_data["Full name"]})


@then("it shows the address, postal code, city, and country")
def confirmation_shows_address(checkout_page: CheckoutPage, shipping_data: dict[str, str]) -> None:
    checkout_page.expect_shipping_summary({k: shipping_data[k] for k in ("Address", "Postal code", "City", "Country")})


@then("it shows the email and phone number")
def confirmation_shows_contact(checkout_page: CheckoutPage, shipping_data: dict[str, str]) -> None:
    checkout_page.expect_shipping_summary({k: shipping_data[k] for k in ("Email", "Phone")})


@when("returns to the storefront")
def returns_to_storefront(checkout_page: CheckoutPage) -> None:
    checkout_page.back_to_storefront()


@then("product stock is reduced by the purchased quantity")
def product_stock_reduced(cart_page: CartPage, available_product: object) -> None:
    cart_page.expect_catalog_stock(available_product.name, available_product.in_stock - 2)


@given("the customer has placed an order")
def customer_has_placed_order(checkout_page: CheckoutPage, cart_page: CartPage, shipping_data: dict[str, str], available_product: object) -> None:
    _place_order(checkout_page, cart_page, shipping_data, [(available_product, 1)])


@when('the customer selects "Back to storefront"')
def selects_back_to_storefront(checkout_page: CheckoutPage) -> None:
    checkout_page.back_to_storefront()


@then("the storefront heading and catalog are visible")
def storefront_catalog_visible(checkout_page: CheckoutPage) -> None:
    checkout_page.expect_storefront_catalog()


@given("a customer has placed an order in one browser session")
def order_in_one_session(checkout_page: CheckoutPage, cart_page: CartPage, shipping_data: dict[str, str], available_product: object) -> None:
    _place_order(checkout_page, cart_page, shipping_data, [(available_product, 1)])


@when("a different browser session opens that confirmation URL")
def different_session_opens_confirmation(checkout_page: CheckoutPage, browser, checkout_state: dict[str, object]) -> None:
    status, body = checkout_page.confirmation_denied_in_another_session(browser)
    checkout_state["other_status"] = status
    checkout_state["other_body"] = body


@then("a 404 response is returned")
def response_is_404(checkout_state: dict[str, object]) -> None:
    assert checkout_state["other_status"] == 404


@then("no customer or shipping details are exposed")
def no_details_exposed(checkout_state: dict[str, object], shipping_data: dict[str, str]) -> None:
    body = str(checkout_state["other_body"])
    assert all(value not in body for value in shipping_data.values())


@given("the customer has products in the cart")
def customer_has_products(cart_page: CartPage, checkout_page: CheckoutPage, available_product: object) -> None:
    cart_page.open()
    cart_page.add_product(available_product.name, 2)
    checkout_page.open()


@given("one product no longer has enough stock")
def product_stock_changes(available_product: object, checkout_state: dict[str, object]) -> None:
    available_product.in_stock = 1
    available_product.save(update_fields=["in_stock"])
    checkout_state["changed_stock"] = 1


@when("the customer submits valid shipping details")
def submits_valid_shipping(checkout_page: CheckoutPage, shipping_data: dict[str, str]) -> None:
    checkout_page.fill_shipping(shipping_data)
    checkout_page.place_order()


@then("an insufficient-stock message identifies the product")
def insufficient_stock_message(checkout_page: CheckoutPage, available_product: object) -> None:
    checkout_page.expect_insufficient_stock(available_product.name)


@then("no product stock is reduced")
def no_stock_reduced(available_product: object, checkout_state: dict[str, object]) -> None:
    available_product.refresh_from_db()
    assert available_product.in_stock == checkout_state["changed_stock"]


@then("the cart remains unchanged")
def cart_remains_unchanged(storefront_api) -> None:
    payload = storefront_api.get("/cart").json()
    assert payload["total_items"] == 2
