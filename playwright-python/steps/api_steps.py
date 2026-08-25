from playwright.sync_api import APIResponse
from pytest_bdd import given, parsers, then, when

from clients.storefront_api import StorefrontApi


@when(
    parsers.parse('the client requests "{path}"'),
    target_fixture="api_response",
)
def client_requests_path(
    storefront_api: StorefrontApi,
    path: str,
) -> APIResponse:
    return storefront_api.get(path)


@then("the response is successful")
def response_is_successful(api_response: APIResponse) -> None:
    assert api_response.ok, (
        f"Expected a successful response, got {api_response.status}: "
        f"{api_response.text()}"
    )


@then("it identifies the frontend, products, cart, login, and API exploration paths")
def metadata_identifies_entry_points(api_response: APIResponse) -> None:
    payload = api_response.json()

    assert payload["frontend"] == "/"
    assert payload["products"] == "/products"
    assert payload["cart"] == "/cart"
    assert payload["login"] == "/login"
    assert payload["docs"] == "/products"


@then("each product contains id, name, description, price, stock, image, rating, and review count")
def each_product_contains_expected_fields(api_response: APIResponse) -> None:
    products = api_response.json()
    expected_fields = {
        "id",
        "name",
        "description",
        "price",
        "in_stock",
        "image_url",
        "average_rating",
        "review_count",
    }

    assert isinstance(products, list), "Expected the product response to be a list"
    assert products, "Expected the product collection to contain at least one product"

    for product in products:
        missing_fields = expected_fields - product.keys()
        assert not missing_fields, (
            f"Product {product.get('id', '<unknown>')} is missing fields: "
            f"{sorted(missing_fields)}"
        )


@given("a product with reviews exists")
def product_with_reviews_exists(product_with_reviews: dict[str, object]) -> None:
    assert product_with_reviews["product"].pk is not None
    assert len(product_with_reviews["reviews"]) == 2


@when(
    'the client requests that product from "/products/<id>"',
    target_fixture="api_response",
)
def client_requests_product_detail(
    storefront_api: StorefrontApi,
    product_with_reviews: dict[str, object],
) -> APIResponse:
    product = product_with_reviews["product"]
    return storefront_api.get(f"/products/{product.id}")


@then("the response contains the selected product")
def response_contains_selected_product(
    api_response: APIResponse,
    product_with_reviews: dict[str, object],
) -> None:
    payload = api_response.json()
    product = product_with_reviews["product"]

    assert api_response.ok, api_response.text()
    assert payload["id"] == product.id
    assert payload["name"] == product.name
    assert payload["description"] == product.description
    assert payload["price"] == float(product.price)
    assert payload["in_stock"] == product.in_stock


@then("it contains the product reviews")
def response_contains_product_reviews(
    api_response: APIResponse,
    product_with_reviews: dict[str, object],
) -> None:
    payload = api_response.json()
    reviews_by_user = {review["user"]: review for review in payload["reviews"]}

    assert len(reviews_by_user) == 2
    for expected_review in product_with_reviews["reviews"]:
        actual_review = reviews_by_user[expected_review.user.get_username()]
        assert actual_review["rating"] == str(expected_review.rating)
        assert actual_review["comment"] == expected_review.comment


@when(
    "the client requests an unknown product id",
    target_fixture="api_response",
)
def client_requests_unknown_product(storefront_api: StorefrontApi) -> APIResponse:
    return storefront_api.get("/products/2147483647")


@then(
    parsers.re(r'the API returns status "?(?P<status>\d+)"?'),
    converters={"status": int},
)
def api_returns_status(api_response: APIResponse, status: int) -> None:
    assert api_response.status == status, (
        f"Expected status {status}, got {api_response.status}: {api_response.text()}"
    )


@then('the response says "Product not found"')
def response_says_product_not_found(api_response: APIResponse) -> None:
    assert api_response.json() == {"detail": "Product not found"}


@given("an available product exists")
def available_product_exists(available_product: object) -> None:
    assert available_product.pk is not None
    assert available_product.in_stock > 0


@when(
    'the client posts its id and a valid quantity to "/cart"',
    target_fixture="api_response",
)
def client_adds_product_to_cart(
    storefront_api: StorefrontApi,
    available_product: object,
) -> APIResponse:
    return storefront_api.post(
        "/cart",
        {"product_id": available_product.id, "quantity": 2},
    )


@then("the response contains the updated items, item count, and total")
def response_contains_updated_cart(
    api_response: APIResponse,
    available_product: object,
) -> None:
    payload = api_response.json()

    assert len(payload["items"]) == 1
    assert payload["items"][0]["product"]["id"] == available_product.id
    assert payload["items"][0]["quantity"] == 2
    assert payload["items"][0]["line_total"] == float(available_product.price * 2)
    assert payload["total_items"] == 2
    assert payload["grand_total"] == float(available_product.price * 2)


@when(
    parsers.parse(
        'the client posts product id "{product_id}" and quantity "{quantity}" to "/cart"'
    ),
    target_fixture="api_response",
)
def client_posts_invalid_cart_input(
    storefront_api: StorefrontApi,
    available_product: object,
    product_id: str,
    quantity: str,
) -> APIResponse:
    if product_id == "valid":
        resolved_product_id = available_product.id
    elif product_id == "unknown":
        resolved_product_id = 2147483647
    else:
        resolved_product_id = int(product_id)

    resolved_quantity = (
        available_product.in_stock + 1
        if quantity == "too many"
        else int(quantity)
    )

    return storefront_api.post(
        "/cart",
        {
            "product_id": resolved_product_id,
            "quantity": resolved_quantity,
        },
    )


@given("the cart API contains a product")
def cart_api_contains_product(cart_with_product: object) -> None:
    assert cart_with_product.pk is not None


@when(
    'the client deletes "/cart/<product_id>"',
    target_fixture="api_response",
)
def client_deletes_cart_product(
    storefront_api: StorefrontApi,
    cart_with_product: object,
) -> APIResponse:
    return storefront_api.delete(f"/cart/{cart_with_product.id}")


@then("that product is absent from the returned cart")
def product_is_absent_from_returned_cart(
    api_response: APIResponse,
    cart_with_product: object,
) -> None:
    assert api_response.ok, api_response.text()
    payload = api_response.json()
    returned_product_ids = {
        item["product"]["id"]
        for item in payload["items"]
    }

    assert cart_with_product.id not in returned_product_ids
    assert payload["total_items"] == 0
    assert payload["grand_total"] == 0.0


@given("the cart API contains products")
def cart_api_contains_products(cart_with_product: object) -> None:
    assert cart_with_product.pk is not None


@when(
    'the client deletes "/cart"',
    target_fixture="api_response",
)
def client_clears_cart(storefront_api: StorefrontApi) -> APIResponse:
    return storefront_api.delete("/cart")


@then("the returned cart is empty")
def returned_cart_is_empty(api_response: APIResponse) -> None:
    assert api_response.ok, api_response.text()
    assert api_response.json()["items"] == []


@then("total items and grand total are zero")
def returned_cart_totals_are_zero(api_response: APIResponse) -> None:
    payload = api_response.json()

    assert payload["total_items"] == 0
    assert payload["grand_total"] == 0.0
