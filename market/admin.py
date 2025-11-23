from django.contrib import admin
from .models import (
    Product,
    UserTokenAccount,
    Purchase,
    TokenTopUp,
    VendorAPIKey,
    TokenTransfer,
    VendorWebhook,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price_tokens", "active")
    list_filter = ("active",)
    search_fields = ("name",)


@admin.register(UserTokenAccount)
class UserTokenAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "token_balance")
    search_fields = ("user__username",)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "total_tokens", "created_at")
    list_filter = ("created_at",)

@admin.register(TokenTopUp)
class TokenTopUpAdmin(admin.ModelAdmin):
    list_display = ("user", "amount_tokens", "created_at", "description")
    list_filter = ("created_at",)
    search_fields = ("user__username",)


@admin.register(VendorAPIKey)
class VendorAPIKeyAdmin(admin.ModelAdmin):
    list_display = ("vendor", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("vendor__username", "name")


@admin.register(TokenTransfer)
class TokenTransferAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "amount_tokens", "created_at", "api_key")
    list_filter = ("created_at",)
    search_fields = ("from_user__username", "to_user__username")


@admin.register(VendorWebhook)
class VendorWebhookAdmin(admin.ModelAdmin):
    list_display = ("vendor", "url", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("vendor__username", "url")