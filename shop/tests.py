from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .forms import CheckoutForm
from .models import Order, OrderItem, Product
from .serializers import CartActionSerializer, ProductSerializer
from .storefront import Storefront, storefront


VALID_SHIPPING = {
    "full_name": "Test Customer",
    "email": "customer@example.com",
    "phone": "+47 12345678",
    "address": "Testgata 1",
    "postal_code": "0123",
    "city": "Oslo",
    "country": "Norway",
}


def create_product(**overrides):
    values = {
        "name": "Running shoes",
        "description": "Lightweight shoes",
        "price": Decimal("79.99"),
        "in_stock": 5,
    }
    values.update(overrides)
    return Product.objects.create(**values)


def create_order(**overrides):
    values = {**VALID_SHIPPING, "total_amount": Decimal("79.99")}
    values.update(overrides)
    return Order.objects.create(**values)


class ProductModelTests(TestCase):
    def test_string_representation_is_name(self):
        self.assertEqual(str(create_product(name="Football")), "Football")

    def test_products_are_ordered_by_id(self):
        first = create_product(name="First")
        second = create_product(name="Second")
        product_ids = list(Product.objects.values_list("id", flat=True))
        self.assertLess(product_ids.index(first.id), product_ids.index(second.id))


class OrderModelTests(TestCase):
    def test_order_uses_orders_table(self):
        self.assertEqual(Order._meta.db_table, "orders")

    def test_order_string_contains_id_and_name(self):
        order = create_order(full_name="Ada Lovelace")
        self.assertEqual(str(order), f"Order #{order.id} - Ada Lovelace")

    def test_order_item_string_contains_quantity_and_name(self):
        item = OrderItem.objects.create(
            order=create_order(), product_name="Shoes", unit_price=Decimal("10.00"),
            quantity=2, line_total=Decimal("20.00"),
        )
        self.assertEqual(str(item), "2 x Shoes")

    def test_deleting_product_preserves_order_snapshot(self):
        product = create_product()
        item = OrderItem.objects.create(
            order=create_order(), product=product, product_name=product.name,
            unit_price=product.price, quantity=1, line_total=product.price,
        )
        product.delete()
        item.refresh_from_db()
        self.assertIsNone(item.product)
        self.assertEqual(item.product_name, "Running shoes")
        self.assertEqual(item.unit_price, Decimal("79.99"))

    def test_deleting_order_cascades_to_items(self):
        order = create_order()
        OrderItem.objects.create(
            order=order, product_name="Shoes", unit_price=Decimal("10.00"),
            quantity=1, line_total=Decimal("10.00"),
        )
        order.delete()
        self.assertFalse(OrderItem.objects.exists())


class CheckoutFormTests(TestCase):
    def test_valid_details_are_accepted(self):
        form = CheckoutForm(data=VALID_SHIPPING)
        self.assertTrue(form.is_valid(), form.errors)

    def test_all_fields_are_required(self):
        form = CheckoutForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(set(form.errors), set(VALID_SHIPPING))

    def test_invalid_email_is_rejected(self):
        form = CheckoutForm(data={**VALID_SHIPPING, "email": "invalid"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_model_field_length_is_enforced(self):
        form = CheckoutForm(data={**VALID_SHIPPING, "phone": "1" * 31})
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_autocomplete_hints_are_configured(self):
        form = CheckoutForm()
        self.assertEqual(form.fields["full_name"].widget.attrs["autocomplete"], "name")
        self.assertEqual(form.fields["email"].widget.attrs["autocomplete"], "email")
        self.assertEqual(form.fields["address"].widget.attrs["autocomplete"], "street-address")


class SerializerTests(TestCase):
    def test_cart_quantity_defaults_to_one(self):
        serializer = CartActionSerializer(data={"product_id": 1})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["quantity"], 1)

    def test_cart_rejects_non_positive_values(self):
        serializer = CartActionSerializer(data={"product_id": 0, "quantity": 0})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), {"product_id", "quantity"})

    def test_product_uses_available_stock_and_numeric_price(self):
        product = create_product()
        product.available_in_stock = 3
        product.average_rating = None
        product.review_count = 0
        data = ProductSerializer(product).data
        self.assertEqual(data["price"], 79.99)
        self.assertEqual(data["in_stock"], 3)
        self.assertEqual(data["image_url"], "")
        self.assertIsNone(data["average_rating"])
        self.assertEqual(data["review_count"], 0)


class StorefrontUnitTests(TestCase):
    def setUp(self):
        self.cart = Storefront()
        self.product = create_product()

    def test_new_cart_is_empty(self):
        cart = self.cart.get_cart()
        self.assertEqual(cart.items, [])
        self.assertEqual(cart.total_items, 0)
        self.assertEqual(cart.grand_total, Decimal("0.00"))

    def test_add_product_calculates_line_total(self):
        cart = self.cart.add_to_cart(self.product.id, 2)
        self.assertEqual(cart.total_items, 2)
        self.assertEqual(cart.items[0].quantity, 2)
        self.assertEqual(cart.items[0].line_total, Decimal("159.98"))

    def test_adding_same_product_accumulates_quantity(self):
        self.cart.add_to_cart(self.product.id, 1)
        cart = self.cart.add_to_cart(self.product.id, 2)
        self.assertEqual(cart.items[0].quantity, 3)

    def test_totals_include_multiple_products(self):
        second = create_product(name="Bottle", price=Decimal("10.50"), in_stock=2)
        self.cart.add_to_cart(self.product.id, 2)
        self.cart.add_to_cart(second.id, 1)
        cart = self.cart.get_cart()
        self.assertEqual(cart.total_items, 3)
        self.assertEqual(cart.grand_total, Decimal("170.48"))

    def test_unknown_product_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.cart.add_to_cart(999999, 1)

    def test_quantity_above_stock_is_rejected(self):
        with self.assertRaisesMessage(ValueError, "Only 5 units left of Running shoes"):
            self.cart.add_to_cart(self.product.id, 6)

    def test_reservations_reduce_available_stock(self):
        self.cart.add_to_cart(self.product.id, 4)
        with self.assertRaisesMessage(ValueError, "Only 1 units left of Running shoes"):
            self.cart.add_to_cart(self.product.id, 2)
        self.assertEqual(self.cart.get_product(self.product.id).available_in_stock, 1)
        self.assertEqual(self.cart.reserved_quantity(self.product.id), 4)

    def test_remove_product(self):
        self.cart.add_to_cart(self.product.id, 2)
        self.assertEqual(self.cart.remove_from_cart(self.product.id).total_items, 0)

    def test_remove_unknown_product_is_safe(self):
        self.assertEqual(self.cart.remove_from_cart(999999).total_items, 0)

    def test_clear_cart_removes_all_products(self):
        second = create_product(name="Bottle", price=Decimal("10.50"), in_stock=2)
        self.cart.add_to_cart(self.product.id, 1)
        self.cart.add_to_cart(second.id, 1)
        self.assertEqual(self.cart.clear_cart().items, [])

    def test_get_unknown_product_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.cart.get_product(999999)


class CartApiTests(TestCase):
    def setUp(self):
        storefront.clear_cart()
        self.product = create_product()

    def tearDown(self):
        storefront.clear_cart()

    def test_product_list_returns_catalog(self):
        response = self.client.get(reverse("products"))
        self.assertEqual(response.status_code, 200)
        products_by_id = {product["id"]: product for product in response.json()}
        self.assertEqual(products_by_id[self.product.id]["name"], "Running shoes")

    def test_missing_product_returns_404(self):
        response = self.client.get(reverse("product-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Product not found")

    def test_empty_cart_response(self):
        response = self.client.get(reverse("cart"))
        self.assertEqual(response.json(), {"items": [], "total_items": 0, "grand_total": 0.0})

    def test_post_adds_product(self):
        response = self.client.post(
            reverse("cart"), {"product_id": self.product.id, "quantity": 2},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["total_items"], 2)
        self.assertEqual(response.json()["grand_total"], 159.98)

    def test_post_rejects_invalid_quantity(self):
        response = self.client.post(
            reverse("cart"), {"product_id": self.product.id, "quantity": 0},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("quantity", response.json())

    def test_post_rejects_unknown_product(self):
        response = self.client.post(
            reverse("cart"), {"product_id": 999999, "quantity": 1},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_post_rejects_quantity_above_stock(self):
        response = self.client.post(
            reverse("cart"), {"product_id": self.product.id, "quantity": 6},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Only 5 units left", response.json()["detail"])

    def test_delete_cart_item(self):
        storefront.add_to_cart(self.product.id, 1)
        response = self.client.delete(reverse("cart-item", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_items"], 0)

    def test_delete_clears_cart(self):
        storefront.add_to_cart(self.product.id, 1)
        response = self.client.delete(reverse("cart"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"], [])


class CheckoutIntegrationTests(TestCase):
    def setUp(self):
        storefront.clear_cart()
        self.product = create_product()

    def tearDown(self):
        storefront.clear_cart()

    def test_empty_cart_redirects_to_storefront(self):
        response = self.client.get(reverse("checkout"))
        self.assertRedirects(response, reverse("storefront"))

    def test_page_shows_form_and_cart_summary(self):
        storefront.add_to_cart(self.product.id, 2)
        response = self.client.get(reverse("checkout"))
        self.assertContains(response, "Shipping details")
        self.assertContains(response, "Running shoes")
        self.assertContains(response, "$159.98")

    def test_checkout_creates_complete_order(self):
        storefront.add_to_cart(self.product.id, 2)
        response = self.client.post(reverse("checkout"), VALID_SHIPPING)
        order = Order.objects.get()
        item = order.items.get()
        self.assertRedirects(response, reverse("order-confirmation", args=[order.id]))
        self.assertEqual(order.total_amount, Decimal("159.98"))
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.product_name, "Running shoes")
        self.assertEqual(item.unit_price, Decimal("79.99"))
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.line_total, Decimal("159.98"))

    def test_success_reduces_stock_and_clears_cart(self):
        storefront.add_to_cart(self.product.id, 2)
        self.client.post(reverse("checkout"), VALID_SHIPPING)
        self.product.refresh_from_db()
        self.assertEqual(self.product.in_stock, 3)
        self.assertEqual(storefront.get_cart().total_items, 0)

    def test_invalid_shipping_does_not_create_order(self):
        storefront.add_to_cart(self.product.id, 1)
        response = self.client.post(reverse("checkout"), {"full_name": "Test"})
        self.assertContains(response, "This field is required")
        self.assertFalse(Order.objects.exists())
        self.assertEqual(storefront.get_cart().total_items, 1)

    def test_stock_change_prevents_partial_order(self):
        second = create_product(name="Bottle", price=Decimal("10.00"), in_stock=2)
        storefront.add_to_cart(self.product.id, 1)
        storefront.add_to_cart(second.id, 2)
        second.in_stock = 1
        second.save(update_fields=["in_stock"])
        response = self.client.post(reverse("checkout"), VALID_SHIPPING)
        self.assertContains(response, "There is no longer enough stock for Bottle")
        self.assertFalse(Order.objects.exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.in_stock, 5)
        self.assertEqual(storefront.get_cart().total_items, 3)

    def test_confirmation_shows_order_details(self):
        storefront.add_to_cart(self.product.id, 1)
        self.client.post(reverse("checkout"), VALID_SHIPPING)
        order = Order.objects.get()
        response = self.client.get(reverse("order-confirmation", args=[order.id]))
        for expected in ("Test Customer", "customer@example.com", "+47 12345678", "Testgata 1", "Running shoes"):
            self.assertContains(response, expected)

    def test_confirmation_is_private_to_session(self):
        order = create_order(full_name="Private Customer")
        response = self.client.get(reverse("order-confirmation", args=[order.id]))
        self.assertEqual(response.status_code, 404)

    def test_unknown_confirmation_returns_404(self):
        session = self.client.session
        session["last_order_id"] = 999999
        session.save()
        response = self.client.get(reverse("order-confirmation", args=[999999]))
        self.assertEqual(response.status_code, 404)
