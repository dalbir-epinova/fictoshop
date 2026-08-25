from behave import given, then, when
from playwright.sync_api import expect


@given("the storefront service is up")
def storefront_service_is_up(context) -> None:
    response = context.api_context.get("/products")
    assert (
        response.ok
    ), f"Products endpoint unavailable: {response.status} {response.text()}"


@given("I open the storefront home page")
@when("I open the storefront home page")
def open_storefront(context) -> None:
    context.home_page.open()


@when('I click on "{button_label}" button')
def click_named_button(context, button_label: str) -> None:
    # Special-case the header login control to match the expected DOM structure.
    if button_label.strip().lower() == "log in":
        locator = context.page.get_by_role("banner").get_by_role(
            "link", name=button_label
        )
    else:
        print("Button: " + button_label + " not found!")
    locator.first.click()


@then('The "{page_label}" page is shown')
def signin_page_is_shown(context, page_label) -> None:
    if page_label.strip().lower() == "sign_in":
        expect(
            context.page.get_by_role("heading", name="Sign in to continue")
        ).to_be_visible()
    else:
        print("Page: " + page_label + " was not shown!")


@then("I can see the hero content")
def see_hero(context) -> None:
    context.home_page.assert_hero_visible()


@then("I can see products listed")
def see_products(context) -> None:
    context.home_page.assert_product_grid_populated()


@when("I add the first listed product to the cart")
def add_first_product(context) -> None:
    context.cart_state["added_product"] = context.home_page.add_first_product_to_cart()


@then("the cart summary shows at least one item")
def cart_summary_updated(context) -> None:
    total_items = context.home_page.cart_items_count()
    assert (
        total_items > 0
    ), "Cart count should be greater than zero after adding a product."
    assert (
        context.home_page.cart_grand_total()
    ), "Cart total should render a currency value."
    if "added_product" in context.cart_state:
        assert context.cart_state[
            "added_product"
        ], "Expected added product name to be recorded."
