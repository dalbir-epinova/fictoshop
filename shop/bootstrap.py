"""Bootstrap helpers to seed products and a default admin user."""

from __future__ import annotations

import os
from typing import Iterable, List

from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Product

DEFAULT_PRODUCTS: List[dict] = [
    {
        "name": "Orbit Phone Case",
        "description": "Durable matte case that fits most modern phones.",
        "price": 24.99,
        "in_stock": 42,
    },
    {
        "name": "Aurora Headphones",
        "description": "Wireless over-ear headphones with noise cancellation.",
        "price": 149.0,
        "in_stock": 15,
    },
    {
        "name": "Nimbus Backpack",
        "description": "Water resistant everyday backpack with laptop sleeve.",
        "price": 89.5,
        "in_stock": 18,
    },
]


def ensure_superuser() -> None:
    """Create a default superuser if it is missing."""
    User = get_user_model()
    if User.objects.filter(is_superuser=True).exists():
        return
    username = os.getenv("FICTOSHOP_ADMIN_USER", "admin")
    password = os.getenv("FICTOSHOP_ADMIN_PASSWORD", "admin123")
    User.objects.create_superuser(username=username, email="", password=password)


def seed_products(products: Iterable[dict] = DEFAULT_PRODUCTS) -> None:
    """Populate the catalog with demo products if empty."""
    if Product.objects.exists():
        return
    to_create = [
        Product(
            name=product["name"],
            description=product["description"],
            price=product["price"],
            in_stock=product["in_stock"],
        )
        for product in products
    ]
    Product.objects.bulk_create(to_create)


def bootstrap() -> None:
    """Entry point triggered after migrations."""
    with transaction.atomic():
        ensure_superuser()
        seed_products()
