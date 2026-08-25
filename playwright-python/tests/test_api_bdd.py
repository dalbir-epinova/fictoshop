from pytest_bdd import scenario


@scenario(
    "../features/api_admin.feature",
    "API metadata lists available entry points",
)
def test_api_metadata_lists_available_entry_points():
    pass


@scenario(
    "../features/api_admin.feature",
    "Product collection returns products",
)
def test_product_collection_returns_products():
    pass


@scenario(
    "../features/api_admin.feature",
    "Product detail returns one product and reviews",
)
def test_product_detail_returns_one_product_and_reviews():
    pass


@scenario(
    "../features/api_admin.feature",
    "Unknown product returns not found",
)
def test_unknown_product_returns_not_found():
    pass


@scenario(
    "../features/api_admin.feature",
    "Add product through cart API",
)
def test_add_product_through_cart_api():
    pass


@scenario(
    "../features/api_admin.feature",
    "Cart API rejects invalid input",
)
def test_cart_api_rejects_invalid_input():
    pass


@scenario(
    "../features/api_admin.feature",
    "Remove product through cart API",
)
def test_remove_product_through_cart_api():
    pass


@scenario(
    "../features/api_admin.feature",
    "Clear cart through API",
)
def test_clear_cart_through_api():
    pass
