"""Views providing the DRF implementation of the Fictoshop API."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate, login, logout
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, Review
from .serializers import (
    CartActionSerializer,
    CartSerializer,
    LoginSerializer,
    ProductSerializer,
    ReviewSerializer,
)
from .storefront import storefront


def serve_index(request):
    """Serve the storefront SPA without altering the design."""
    return render(request, "shop/index.html")


def _safe_next_url(request, value: str | None) -> str:
    if not value:
        return ""
    allowed = {request.get_host()}
    if url_has_allowed_host_and_scheme(value, allowed_hosts=allowed):
        return value
    return ""


def serve_login(request):
    """Serve a lightweight login page for non-admin users."""
    next_url = _safe_next_url(request, request.GET.get("next", ""))
    return render(request, "shop/login.html", {"next_url": next_url})


@require_POST
def logout_view(request):
    """Terminate the current session and return to the storefront."""
    logout(request)
    return redirect("storefront")


def product_view(request, product_id: int):
    """Render a single product view with reviews and a submission form."""
    product = get_object_or_404(
        Product.objects.annotate(average_rating=Avg("reviews__rating"), review_count=Count("reviews")),
        id=product_id,
    )
    reviews = product.reviews.select_related("user")
    error = ""
    if request.method == "POST":
        if not request.user.is_authenticated:
            signin_url = f"{reverse('signin')}?next={request.path}"
            return redirect(signin_url)
        rating_raw = request.POST.get("rating")
        comment = (request.POST.get("comment") or "").strip()
        if rating_raw in (None, ""):
            rating = None
        else:
            try:
                rating = Decimal(rating_raw)
            except (TypeError, InvalidOperation):
                rating = None
        if rating is None:
            error = "Select a rating using the stars."
        elif rating < Decimal("0.5") or rating > Decimal("5"):
            error = "Rating must be between 0.5 and 5 stars."
        elif (rating * 2) % 1 != 0:
            error = "Ratings must use 0.5 star increments."
        elif not comment:
            error = "Please share a few words about your experience."
        if not error:
            Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={"rating": rating, "comment": comment},
            )
            return redirect("product-view", product_id=product.id)
    user_review = reviews.filter(user=request.user).first() if request.user.is_authenticated else None
    signin_url = f"{reverse('signin')}?next={request.path}"
    return render(
        request,
        "shop/product_detail.html",
        {
            "product": product,
            "reviews": reviews,
            "error": error,
            "user_review": user_review,
            "star_indices": range(1, 6),
            "signin_url": signin_url,
        },
    )


class MetaView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "message": "Welcome to Fictoshop",
                "docs": "/docs",
                "login": "/login",
                "products": "/products",
                "cart": "/cart",
                "frontend": "/",
            }
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request=request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        payload = {"detail": "Login successful"}
        if user.is_superuser:
            admin_url = request.build_absolute_uri(reverse("admin:index"))
            payload["redirect"] = admin_url
        else:
            payload["redirect"] = "/"
        return Response(payload)


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        products = storefront.list_products()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id: int, *args, **kwargs):
        try:
            product = storefront.get_product(product_id)
        except KeyError:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        review_data = ReviewSerializer(product.reviews.select_related("user"), many=True)
        data = serializer.data
        data["reviews"] = review_data.data
        return Response(data)


class CartView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        cart = storefront.get_cart()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = CartActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            cart = storefront.add_to_cart(data["product_id"], data["quantity"])
        except KeyError:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        output = CartSerializer(cart)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        cart = storefront.clear_cart()
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, product_id: int, *args, **kwargs):
        cart = storefront.remove_from_cart(product_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CheckoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        cart = storefront.get_cart()
        if cart.total_items == 0:
            return Response({"detail": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
