import os
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from playwright.sync_api import BrowserContext, Page, Playwright, expect

from clients.storefront_api import StorefrontApi
from pages.admin_page import AdminPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.product_detail_page import ProductDetailPage
from pages.responsive_mobile_page import ResponsiveMobilePage
from pages.sign_in_page import SignInPage
from pages.storefront_page import StorefrontPage


PLAYWRIGHT_TIMEOUT_MS = 10_000


@pytest.fixture(autouse=True)
def clean_up_records_created_by_test():
    """Remove database records created by each Playwright scenario."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fictoshop_django.settings")
    previous_async_setting = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

    import django

    django.setup()

    from django.contrib.auth import get_user_model
    from shop.models import Order, Product, Review

    models = (Order, Review, Product, get_user_model())
    existing_ids = {
        model: set(model.objects.values_list("pk", flat=True)) for model in models
    }

    try:
        yield
    finally:
        # Dependency order matters: orders own order lines, reviews reference
        # users and products, and products/users can then be removed safely.
        for model in models:
            model.objects.exclude(pk__in=existing_ids[model]).delete()

        if previous_async_setting is None:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE", None)
        else:
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = previous_async_setting


@pytest.fixture
def configured_page(page: Page) -> Page:
    """Return a browser page with the shared Playwright timeouts applied."""
    page.set_default_timeout(PLAYWRIGHT_TIMEOUT_MS)
    page.set_default_navigation_timeout(PLAYWRIGHT_TIMEOUT_MS)
    expect.set_options(timeout=PLAYWRIGHT_TIMEOUT_MS)
    return page


@pytest.fixture(scope="session")
def app_base_url() -> str:
    return os.getenv("FICTOSHOP_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def admin_page(configured_page: Page, app_base_url: str) -> AdminPage:
    return AdminPage(configured_page, app_base_url)


@pytest.fixture
def storefront_page(configured_page: Page, app_base_url: str) -> StorefrontPage:
    return StorefrontPage(configured_page, app_base_url)


@pytest.fixture
def sign_in_page(configured_page: Page, app_base_url: str) -> SignInPage:
    return SignInPage(configured_page, app_base_url)


@pytest.fixture
def product_detail_page(configured_page: Page, app_base_url: str) -> ProductDetailPage:
    return ProductDetailPage(configured_page, app_base_url)


@pytest.fixture
def cart_page(configured_page: Page, app_base_url: str) -> CartPage:
    return CartPage(configured_page, app_base_url)


@pytest.fixture
def checkout_page(configured_page: Page, app_base_url: str) -> CheckoutPage:
    return CheckoutPage(configured_page, app_base_url)


@pytest.fixture
def responsive_mobile_page(
    configured_page: Page, app_base_url: str, project_root: Path
) -> ResponsiveMobilePage:
    return ResponsiveMobilePage(configured_page, app_base_url, project_root)


@pytest.fixture
def signed_out_context(context: BrowserContext) -> BrowserContext:
    context.clear_cookies()
    return context


pytest_plugins = [
    "steps.admin_steps",
    "steps.api_steps",
    "steps.authentication_steps",
    "steps.cart_steps",
    "steps.checkout_steps",
    "steps.responsive_mobile_steps",
    "steps.storefront_steps",
]


@pytest.fixture
def admin_credentials():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fictoshop_django.settings")
    previous_async_setting = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    import django
    django.setup()
    from django.contrib.auth import get_user_model

    username = f"playwright_admin_{uuid4().hex[:8]}"
    password = f"Playwright-{uuid4().hex}!"
    user = get_user_model().objects.create_superuser(
        username=username,
        email="playwright-admin@example.com",
        password=password,
    )
    try:
        yield {"username": username, "password": password}
    finally:
        user.delete()
        if previous_async_setting is None:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE", None)
        else:
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = previous_async_setting


@pytest.fixture
def regular_user_credentials():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fictoshop_django.settings")
    previous_async_setting = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

    import django

    django.setup()

    from django.contrib.auth import get_user_model

    username = f"playwright_user_{uuid4().hex[:8]}"
    password = f"Playwright-{uuid4().hex}!"
    user = get_user_model().objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password=password,
    )

    try:
        yield {"username": username, "password": password}
    finally:
        user.delete()
        if previous_async_setting is None:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE", None)
        else:
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = previous_async_setting


@pytest.fixture
def review_data() -> dict[str, object]:
    return {
        "rating": 4, "comment": f"Playwright review {uuid4().hex[:8]}",
        "updated_rating": 5, "updated_comment": f"Updated Playwright review {uuid4().hex[:8]}",
    }


@pytest.fixture
def existing_user_review(regular_user_credentials: dict[str, str], existing_product):
    from django.contrib.auth import get_user_model
    from shop.models import Review
    user = get_user_model().objects.get(username=regular_user_credentials["username"])
    return Review.objects.create(product=existing_product, user=user, rating=Decimal("2.0"), comment="Original Playwright review.")


@pytest.fixture
def product_data(admin_credentials):
    product = {
        "name": f"Playwright product {uuid4().hex[:8]}",
        "description": "Product created by the Playwright admin scenario.",
        "price": "49.95",
        "in_stock": 7,
        "new_stock": 12,
        "image_path": Path(__file__).parent.parent / "images" / "uploads" / "boxing_gloves.jpg",
    }

    try:
        yield product
    finally:
        from shop.models import Product

        saved_product = Product.objects.filter(name=product["name"]).first()
        uploaded_image = None
        if saved_product and saved_product.image_url:
            uploaded_image = Path(saved_product.image_url.path)
        if saved_product:
            saved_product.delete()
        if uploaded_image:
            uploaded_image.unlink(missing_ok=True)


@pytest.fixture
def existing_product(product_data):
    from shop.models import Product

    product = Product.objects.create(
        name=product_data["name"],
        description=product_data["description"],
        price=Decimal(str(product_data["price"])),
        in_stock=product_data["in_stock"],
    )
    product_id = product.id
    try:
        yield product
    finally:
        Product.objects.filter(pk=product_id).delete()


@pytest.fixture
def cart_products(existing_product):
    from shop.models import Product
    secondary = Product.objects.create(
        name=f"Second cart product {uuid4().hex[:8]}",
        description="Second product for Playwright cart scenarios.",
        price=Decimal("15.25"),
        in_stock=8,
    )
    try:
        yield {"primary": existing_product, "secondary": secondary}
    finally:
        secondary.delete()


@pytest.fixture
def checkout_secondary_product(admin_credentials):
    from shop.models import Product
    product = Product.objects.create(name=f"Checkout second {uuid4().hex[:8]}", description="Checkout test product", price=Decimal("12.50"), in_stock=6)
    try:
        yield product
    finally:
        product.delete()


@pytest.fixture
def shipping_data() -> dict[str, str]:
    reference = uuid4().hex[:8]
    return {"Full name": f"Checkout Customer {reference}", "Email": f"checkout-{reference}@example.com", "Phone": "+47 99887766", "Address": "Testveien 42", "Postal code": "0123", "City": "Oslo", "Country": "Norway"}


@pytest.fixture
def checkout_state():
    from shop.models import Order
    initial_ids = set(Order.objects.values_list("id", flat=True))
    state: dict[str, object] = {"initial_order_ids": initial_ids}
    try:
        yield state
    finally:
        Order.objects.exclude(id__in=initial_ids).delete()


@pytest.fixture
def available_product(existing_product, storefront_api):
    storefront_api.delete("/cart")
    try:
        yield existing_product
    finally:
        storefront_api.delete("/cart")


@pytest.fixture
def storefront_catalog(admin_credentials, storefront_api):
    from shop.models import Product

    reference = uuid4().hex[:8]
    products = {
        "available": Product.objects.create(
            name=f"In-stock catalog item {reference}",
            description="Available product for storefront tests.",
            price=Decimal("40.00"),
            in_stock=4,
        ),
        "secondary": Product.objects.create(
            name=f"Secondary catalog {reference}",
            description=f"Unique storefront description {reference}",
            price=Decimal("15.50"),
            in_stock=9,
        ),
        "unavailable": Product.objects.create(
            name=f"Sold-out catalog item {reference}",
            description="Out-of-stock product for storefront tests.",
            price=Decimal("75.00"),
            in_stock=0,
        ),
    }
    storefront_api.delete("/cart")
    catalog = {
        **products,
        "name_query": f"In-stock catalog item {reference}",
        "description_query": f"Unique storefront description {reference}",
    }
    try:
        yield catalog
    finally:
        storefront_api.delete("/cart")
        Product.objects.filter(pk__in=[product.pk for product in products.values()]).delete()


@pytest.fixture
def storefront_state() -> dict[str, int]:
    return {}


@pytest.fixture
def cart_with_product(available_product, storefront_api):
    response = storefront_api.post(
        "/cart",
        {"product_id": available_product.id, "quantity": 2},
    )
    assert response.status == 201, response.text()
    return available_product


@pytest.fixture
def order_data(admin_credentials):
    from shop.models import Order, OrderItem

    reference = uuid4().hex[:8]
    order = Order.objects.create(
        full_name=f"Playwright Customer {reference}",
        email=f"customer-{reference}@example.com",
        phone="+47 99887766",
        address="Testveien 42",
        postal_code="0123",
        city="Oslo",
        country="Norway",
        total_amount=Decimal("84.97"),
    )
    items = [
        OrderItem.objects.create(
            order=order,
            product_name=f"Test shoes {reference}",
            unit_price=Decimal("29.99"),
            quantity=2,
            line_total=Decimal("59.98"),
        ),
        OrderItem.objects.create(
            order=order,
            product_name=f"Test bottle {reference}",
            unit_price=Decimal("24.99"),
            quantity=1,
            line_total=Decimal("24.99"),
        ),
    ]

    try:
        yield {"order": order, "items": items}
    finally:
        order.delete()


@pytest.fixture
def product_with_reviews(admin_credentials):
    from django.contrib.auth import get_user_model
    from shop.models import Product, Review

    reference = uuid4().hex[:8]
    product = Product.objects.create(
        name=f"Reviewed product {reference}",
        description="Product created for the API review scenario.",
        price=Decimal("64.50"),
        in_stock=9,
    )
    users = [
        get_user_model().objects.create_user(username=f"reviewer_one_{reference}"),
        get_user_model().objects.create_user(username=f"reviewer_two_{reference}"),
    ]
    reviews = [
        Review.objects.create(
            product=product,
            user=users[0],
            rating=Decimal("4.5"),
            comment="Excellent test product.",
        ),
        Review.objects.create(
            product=product,
            user=users[1],
            rating=Decimal("3.5"),
            comment="Useful, with room for improvement.",
        ),
    ]

    try:
        yield {"product": product, "reviews": reviews, "users": users}
    finally:
        product.delete()
        for user in users:
            user.delete()


@pytest.fixture
def storefront_api(playwright: Playwright, app_base_url: str):
    request_context = playwright.request.new_context(
        base_url=app_base_url,
        extra_http_headers={"Accept": "application/json"},
    )
    try:
        yield StorefrontApi(request_context)
    finally:
        request_context.dispose()
