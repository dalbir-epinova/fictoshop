"""DRF serializers that mirror the original FastAPI schemas."""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Avg
from rest_framework import serializers

from .models import Product, Review


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "in_stock",
            "image_url",
            "average_rating",
            "review_count",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        available = getattr(instance, "available_in_stock", None)
        data["in_stock"] = available if available is not None else instance.in_stock
        data["price"] = float(Decimal(data["price"]))
        average = getattr(instance, "average_rating", None)
        if average is None:
            average = instance.reviews.aggregate(avg=Avg("rating"))["avg"]
        data["average_rating"] = round(float(average), 2) if average is not None else None
        review_count = getattr(instance, "review_count", None)
        if review_count is None:
            review_count = instance.reviews.count()
        data["review_count"] = review_count
        try:
            data["image_url"] = instance.image_url.url if instance.image_url else ""
        except Exception:
            data["image_url"] = ""
        return data


class CartActionSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartItemSerializer(serializers.Serializer):
    product = ProductSerializer()
    quantity = serializers.IntegerField(min_value=1)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["line_total"] = float(Decimal(data["line_total"]))
        return data


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    total_items = serializers.IntegerField(min_value=0)
    grand_total = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["grand_total"] = float(Decimal(data["grand_total"]))
        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(trim_whitespace=False)


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.get_username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
