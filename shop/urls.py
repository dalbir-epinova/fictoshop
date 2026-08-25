from django.urls import path

from . import views

urlpatterns = [
    path("", views.serve_index, name="storefront"),
    path("signin", views.serve_login, name="signin"),
    path("logout", views.logout_view, name="logout"),
    path("meta", views.MetaView.as_view(), name="meta"),
    path("login", views.LoginView.as_view(), name="login"),
    path("products", views.ProductListView.as_view(), name="products"),
    path("products/<int:product_id>/view", views.product_view, name="product-view"),
    path("products/<int:product_id>", views.ProductDetailView.as_view(), name="product-detail"),
    path("cart", views.CartView.as_view(), name="cart"),
    path("cart/<int:product_id>", views.CartItemView.as_view(), name="cart-item"),
    path("checkout", views.checkout_view, name="checkout"),
    path("orders/<int:order_id>/confirmation", views.order_confirmation_view, name="order-confirmation"),
]
