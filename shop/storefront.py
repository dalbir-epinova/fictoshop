"""In-memory cart that mirrors the FastAPI Storefront behavior."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from threading import RLock
from typing import Dict, List

from django.db import transaction
from django.db.models import Avg, Count

from .models import Product


@dataclass
class CartItem:
    product: Product
    quantity: int
    line_total: Decimal


@dataclass
class Cart:
    items: List[CartItem]
    total_items: int
    grand_total: Decimal


class Storefront:
    """Thread-safe cart implementation backed by Django models."""

    def __init__(self) -> None:
        self._cart: Dict[int, int] = {}
        self._lock = RLock()

    def list_products(self) -> List[Product]:
        with self._lock:
            products = list(
                Product.objects.annotate(
                    average_rating=Avg("reviews__rating"),
                    review_count=Count("reviews"),
                )
            )
            return [self._product_with_remaining_stock(product) for product in products]

    def get_product(self, product_id: int) -> Product:
        with self._lock:
            product = (
                Product.objects.annotate(
                    average_rating=Avg("reviews__rating"),
                    review_count=Count("reviews"),
                )
                .filter(id=product_id)
                .first()
            )
            if product is None:
                raise KeyError(product_id)
            return self._product_with_remaining_stock(product)

    def get_cart(self) -> Cart:
        with self._lock:
            items: List[CartItem] = []
            total_items = 0
            grand_total = Decimal("0.00")
            for product_id, quantity in self._cart.items():
                product = (
                    Product.objects.annotate(
                        average_rating=Avg("reviews__rating"),
                        review_count=Count("reviews"),
                    )
                    .filter(id=product_id)
                    .first()
                )
                if product is None:
                    continue
                line_total = (product.price * quantity).quantize(Decimal("0.01"))
                items.append(CartItem(product=product, quantity=quantity, line_total=line_total))
                total_items += quantity
                grand_total += line_total
            grand_total = grand_total.quantize(Decimal("0.01"))
            return Cart(items=items, total_items=total_items, grand_total=grand_total)

    def add_to_cart(self, product_id: int, quantity: int) -> Cart:
        with self._lock, transaction.atomic():
            product = Product.objects.select_for_update().filter(id=product_id).first()
            if product is None:
                raise KeyError(product_id)
            reserved = self._cart.get(product_id, 0)
            available = product.in_stock - reserved
            if quantity > available:
                raise ValueError(f"Only {available} units left of {product.name}")
            self._cart[product_id] = reserved + quantity
            return self.get_cart()

    def remove_from_cart(self, product_id: int) -> Cart:
        with self._lock:
            self._cart.pop(product_id, None)
            return self.get_cart()

    def clear_cart(self) -> Cart:
        with self._lock:
            self._cart.clear()
            return self.get_cart()

    def reserved_quantity(self, product_id: int) -> int:
        with self._lock:
            return self._cart.get(product_id, 0)

    def _product_with_remaining_stock(self, product: Product) -> Product:
        reserved = self._cart.get(product.id, 0)
        remaining = max(product.in_stock - reserved, 0)
        product.available_in_stock = remaining
        return product


storefront = Storefront()
