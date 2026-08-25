from playwright.sync_api import BrowserContext
from pytest_bdd import given, then, when

from pages.admin_page import AdminPage
from pages.storefront_page import StorefrontPage


@given("the customer is signed out")
def customer_is_signed_out(
    signed_out_context: BrowserContext,
) -> None:
    # Cookies are already cleared by the fixture.
    pass


@given("a superuser is signed in")
def superuser_is_signed_in(admin_page: AdminPage, admin_credentials: dict[str, str]) -> None:
    admin_page.open()
    admin_page.login(admin_credentials["username"], admin_credentials["password"])
    admin_page.expect_admin_index()


@when('the customer opens "/admin/"')
def customer_opens_admin(admin_page: AdminPage) -> None:
    admin_page.open()


@when('the superuser opens "/admin/"')
def superuser_opens_admin(admin_page: AdminPage) -> None:
    admin_page.open()


@then("the Django admin login page is displayed")
def admin_login_is_displayed(admin_page: AdminPage) -> None:
    admin_page.expect_login_page()


@then("the administration index is visible")
def administration_index_is_visible(admin_page: AdminPage) -> None:
    admin_page.expect_admin_index()


@then("Products and Orders are listed")
def products_and_orders_are_listed(admin_page: AdminPage) -> None:
    admin_page.expect_products_and_orders()


@when("the superuser opens the new product form")
def superuser_opens_new_product_form(admin_page: AdminPage) -> None:
    admin_page.open_new_product_form()


@when("enters a valid product name, description, price, and stock")
def superuser_enters_product_details(
    admin_page: AdminPage,
    product_data: dict[str, object],
) -> None:
    admin_page.fill_product_fields(product_data)


@when("uploads a dummy product image")
def superuser_uploads_product_image(
    admin_page: AdminPage,
    product_data: dict[str, object],
) -> None:
    admin_page.upload_product_image(str(product_data["image_path"]))


@when("saves the product")
def superuser_saves_product(admin_page: AdminPage) -> None:
    admin_page.save_product()


@then("the product appears in Django administration")
def product_appears_in_admin(
    admin_page: AdminPage,
    product_data: dict[str, object],
) -> None:
    admin_page.expect_product_listed(str(product_data["name"]))


@then("the product appears in the storefront catalog")
def product_appears_in_storefront(
    storefront_page: StorefrontPage,
    product_data: dict[str, object],
) -> None:
    storefront_page.open()
    storefront_page.expect_product_visible(str(product_data["name"]))


@then("the product image is displayed in the storefront catalog")
def product_image_appears_in_storefront(
    storefront_page: StorefrontPage,
    product_data: dict[str, object],
) -> None:
    storefront_page.expect_product_image_visible(str(product_data["name"]))


@given("a product exists")
def product_exists(existing_product: object) -> None:
    assert existing_product.pk is not None


@when("the superuser changes its stock value")
def superuser_changes_product_stock(
    admin_page: AdminPage,
    existing_product: object,
    product_data: dict[str, object],
) -> None:
    admin_page.open_product_change_form(existing_product.id)
    admin_page.change_product_stock(int(product_data["new_stock"]))


@then("the new stock value appears in the storefront")
def new_stock_appears_in_storefront(
    storefront_page: StorefrontPage,
    product_data: dict[str, object],
) -> None:
    storefront_page.open()
    storefront_page.expect_product_stock(
        str(product_data["name"]),
        int(product_data["new_stock"]),
    )


@given("a customer order exists")
def customer_order_exists(order_data: dict[str, object]) -> None:
    assert order_data["order"].pk is not None


@when("the superuser opens that order in administration")
def superuser_opens_order(
    admin_page: AdminPage,
    order_data: dict[str, object],
) -> None:
    admin_page.open_order_change_form(order_data["order"].id)


@then("customer, shipping, total, and creation details are visible")
def order_details_are_visible(
    admin_page: AdminPage,
    order_data: dict[str, object],
) -> None:
    admin_page.expect_order_details(order_data["order"])


@then("each order line is visible as read-only data")
def order_lines_are_visible_and_read_only(
    admin_page: AdminPage,
    order_data: dict[str, object],
) -> None:
    admin_page.expect_order_items_read_only(order_data["items"])
