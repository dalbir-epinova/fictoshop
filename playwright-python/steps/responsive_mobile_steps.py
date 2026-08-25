from pytest_bdd import given, parsers, then, when

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.responsive_mobile_page import ResponsiveMobilePage


@given(parsers.parse('the browser viewport is "{viewport}"'))
def browser_viewport_is(responsive_mobile_page: ResponsiveMobilePage, viewport: str) -> None:
    width, height = (int(value.strip()) for value in viewport.lower().split("x"))
    responsive_mobile_page.set_viewport(width, height)


@given("the browser uses a mobile viewport")
def browser_uses_mobile_viewport(responsive_mobile_page: ResponsiveMobilePage) -> None:
    responsive_mobile_page.set_viewport(390, 844)


@when("the customer opens the storefront")
def customer_opens_storefront_mobile(cart_page: CartPage) -> None:
    cart_page.open()


@then("the heading and catalog fit within the viewport")
def heading_and_catalog_fit(responsive_mobile_page: ResponsiveMobilePage) -> None:
    responsive_mobile_page.expect_storefront_fits()


@then("primary controls are usable without horizontal scrolling")
def primary_controls_usable(responsive_mobile_page: ResponsiveMobilePage) -> None:
    responsive_mobile_page.expect_primary_controls_usable()


@when("the customer adds a product to the cart")
def customer_adds_product_mobile(cart_page: CartPage, available_product: object) -> None:
    cart_page.open()
    cart_page.add_product(available_product.name, 1)


@then("the entire floating cart width remains inside the viewport")
def cart_width_inside_viewport(responsive_mobile_page: ResponsiveMobilePage) -> None:
    responsive_mobile_page.expect_cart_width_inside_viewport()


@then("the cart lines can scroll when their content exceeds the maximum height")
def cart_lines_scrollable(responsive_mobile_page: ResponsiveMobilePage) -> None:
    responsive_mobile_page.expect_cart_lines_scrollable()


@then('"Clear" and "Checkout" remain usable')
def cart_actions_usable(responsive_mobile_page: ResponsiveMobilePage) -> None:
    responsive_mobile_page.expect_cart_actions_usable()


@given("the cart contains a product")
def mobile_cart_contains_product(cart_page: CartPage, available_product: object) -> None:
    cart_page.open()
    cart_page.add_product(available_product.name, 1)


@when("the customer opens checkout")
def customer_opens_checkout(checkout_page: CheckoutPage) -> None:
    checkout_page.open()


@then("shipping fields are arranged in one column")
def shipping_fields_single_column(responsive_mobile_page: ResponsiveMobilePage) -> None:
    responsive_mobile_page.expect_checkout_single_column()


@then('"Back to cart" and "Place order" are usable')
def checkout_actions_usable(responsive_mobile_page: ResponsiveMobilePage) -> None:
    responsive_mobile_page.expect_checkout_actions_usable()


@given("the storefront is running in an Android emulator")
def android_bundle_is_available(responsive_mobile_page: ResponsiveMobilePage) -> None:
    assert (responsive_mobile_page.project_root / "android-app/app/src/main/assets/index.html").exists()


@given("the storefront is running in the iOS app")
def ios_bundle_is_available(responsive_mobile_page: ResponsiveMobilePage) -> None:
    assert (responsive_mobile_page.project_root / "ios-app/fictoshop/fictoshop/WebView.swift").exists()


@when("the mobile bundle requests products")
def mobile_bundle_requests_products(request, responsive_mobile_page: ResponsiveMobilePage) -> None:
    if "android" in request.node.keywords:
        responsive_mobile_page.load_android_bundle()
    else:
        responsive_mobile_page.load_ios_bundle()


@then('it uses "http://10.0.2.2:8000"')
def uses_android_host(responsive_mobile_page: ResponsiveMobilePage) -> None:
    responsive_mobile_page.expect_android_host_base()


@then('it uses the configured "API_BASE_URL"')
def uses_ios_base(responsive_mobile_page: ResponsiveMobilePage) -> None:
    responsive_mobile_page.expect_ios_configured_base()


@then("catalog products are displayed")
def bundle_products_displayed(responsive_mobile_page: ResponsiveMobilePage) -> None:
    responsive_mobile_page.expect_bundle_product()
