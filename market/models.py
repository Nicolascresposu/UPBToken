import secrets
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver



class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_tokens = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    def __str__(self):
        return f"{self.name} ({self.price_tokens} UPBT)"


class UserTokenAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="token_account")
    token_balance = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"TokenAccount of {self.user.username}: {self.token_balance} UPBT"


@receiver(post_save, sender=User)
def create_user_token_account(sender, instance, created, **kwargs):
    if created:
        UserTokenAccount.objects.create(user=instance)


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_tokens = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.username} bought {self.quantity} x {self.product.name}"

class TokenTopUp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="token_topups")
    amount_tokens = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} +{self.amount_tokens} UPBT on {self.created_at:%Y-%m-%d}"

import secrets
def generate_api_key():
    # 40+ chars, URL safe
    return secrets.token_urlsafe(40)

class VendorAPIKey(models.Model):
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_api_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vendor.username} - {self.name}"
    
class TokenTransfer(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="outgoing_transfers",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="incoming_transfers",
    )
    amount_tokens = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    api_key = models.ForeignKey(
        VendorAPIKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers",
    )

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}: {self.amount_tokens} UPBT"
    

class VendorWebhook(models.Model):
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="webhooks",
    )
    url = models.URLField()
    secret = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional secret used to sign webhook payloads.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Webhook for {self.vendor.username} -> {self.url}"
