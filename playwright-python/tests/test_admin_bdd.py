from pytest_bdd import scenario


@scenario("../features/admin.feature", "Guest cannot access administration")
def test_guest_cannot_access_administration():
    pass


@scenario(
    "../features/admin.feature",
    "Superuser opens administration",
)
def test_superuser_opens_administration():
    pass


@scenario(
    "../features/admin.feature",
    "Administrator creates a product",
)
def test_administrator_creates_a_product():
    pass


@scenario(
    "../features/admin.feature",
    "Administrator updates product stock",
)
def test_administrator_updates_product_stock():
    pass


@scenario(
    "../features/admin.feature",
    "Administrator views an order and its lines",
)
def test_administrator_views_an_order_and_its_lines():
    pass
