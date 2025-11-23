from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup_view, name="signup"),
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/buy/", views.buy_product, name="buy_product"),
    path("dashboard/", views.dashboard, name="dashboard"),

    
    # Vendor
    path("vendor/products/", views.my_products, name="my_products"),
    path("vendor/products/new/", views.product_create, name="product_create"),
    path("vendor/products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("vendor/api-keys/", views.vendor_api_keys, name="vendor_api_keys"),

    # Tokens
    path("tokens/buy/", views.buy_tokens, name="buy_tokens"),

    # API endpoints for vendors
    path("api/vendor/purchases/<int:pk>/", views.api_purchase_detail, name="api_purchase_detail"),
    path("api/vendor/transfer/", views.api_transfer_tokens, name="api_transfer_tokens"),
    path("vendor/webhooks/", views.vendor_webhooks, name="vendor_webhooks"),

]

