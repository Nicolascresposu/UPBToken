from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import hmac
import hashlib
import requests

from .forms import SignUpForm, ProductForm, BuyTokensForm
from .models import (
    Product,
    Purchase,
    UserTokenAccount,
    TokenTopUp,
    VendorAPIKey,
    TokenTransfer,
    VendorWebhook,
)


def home(request):
    return redirect("product_list")


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserTokenAccount is created by signal
            login(request, user)
            messages.success(request, "Account created! Welcome to UPBolis.")
            return redirect("product_list")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


def product_list(request):
    products = Product.objects.filter(active=True)
    return render(request, "product_list.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)
    return render(request, "product_detail.html", {"product": product})


# @login_required
# @transaction.atomic
# def buy_product(request, pk):
#     product = get_object_or_404(Product, pk=pk, active=True)

#     if request.method != "POST":
#         # Only allow POST
#         return redirect("product_detail", pk=product.pk)

#     quantity = int(request.POST.get("quantity", 1))
#     if quantity < 1:
#         messages.error(request, "Quantity must be at least 1.")
#         return redirect("product_detail", pk=product.pk)

#     # account = request.user.token_account
#     account = UserTokenAccount.objects.select_for_update().get(user=request.user)
#     total_cost = product.price_tokens * quantity

#     # Reload account with lock to avoid race conditions
#     account = UserTokenAccount.objects.select_for_update().get(pk=account.pk)

#     if account.token_balance < total_cost:
#         messages.error(request, "Not enough UPBolis to buy this product.")
#         return redirect("product_detail", pk=product.pk)

#     # Deduct tokens
#     account.token_balance = F("token_balance") - total_cost
#     account.save()

#     Purchase.objects.create(
#         user=request.user,
#         product=product,
#         quantity=quantity,
#         total_tokens=total_cost,
#     )

#     messages.success(
#         request,
#         f"You bought {quantity} x {product.name} for {total_cost} UPBolis."
#     )
#     return redirect("dashboard")

@login_required
@transaction.atomic
def buy_product(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)

    if request.method != "POST":
        return redirect("product_detail", pk=product.pk)

    quantity = int(request.POST.get("quantity", 1))
    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect("product_detail", pk=product.pk)

    # Buyer account (locked)
    buyer_account = UserTokenAccount.objects.select_for_update().get(user=request.user)
    total_cost = product.price_tokens * quantity

    if buyer_account.token_balance < total_cost:
        messages.error(request, "Not enough UPBolis to buy this product.")
        return redirect("product_detail", pk=product.pk)

    # 1) Deduct from buyer
    buyer_account.token_balance = F("token_balance") - total_cost
    buyer_account.save()

    # 2) Credit vendor (if product has an owner with a token account)
    vendor = product.owner
    if vendor and hasattr(vendor, "token_account"):
        vendor_account = UserTokenAccount.objects.select_for_update().get(user=vendor)
        vendor_account.token_balance = F("token_balance") + total_cost
        vendor_account.save()

    # 3) Register purchase
    purchase = Purchase.objects.create(
        user=request.user,
        product=product,
        quantity=quantity,
        total_tokens=total_cost,
    )

    # 🔔 Send webhooks (non-blocking-ish, but inside same request)
    send_purchase_webhooks(purchase)

    messages.success(
        request,
        f"You bought {quantity} x {product.name} for {total_cost} UPBolis."
    )
    return redirect("dashboard")



@login_required
def dashboard(request):
    account = request.user.token_account
    purchases = request.user.purchases.select_related("product").order_by("-created_at")
    return render(
        request,
        "dashboard.html",
        {"account": account, "purchases": purchases},
    )


def is_vendor(user):
    # staff users OR users in Vendors group
    return user.is_staff or user.groups.filter(name="Vendors").exists()


@login_required
@user_passes_test(is_vendor)
def my_products(request):
    products = Product.objects.filter(owner=request.user).order_by("name")
    return render(request, "my_products.html", {"products": products})

@login_required
@user_passes_test(is_vendor)
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            messages.success(request, "Product created successfully.")
            return redirect("my_products")
    else:
        form = ProductForm()
    return render(
        request,
        "product_form.html",
        {"form": form, "title": "Create product"},
    )


@login_required
@user_passes_test(is_vendor)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("my_products")
    else:
        form = ProductForm(instance=product)
    return render(
        request,
        "product_form.html",
        {"form": form, "title": "Edit product"},
    )

@login_required
@transaction.atomic
def buy_tokens(request):
    """
    Very simple 'buy tokens' flow:
    - User chooses how many tokens they want.
    - We immediately credit their balance and record a TokenTopUp.

    In a real app, you'd integrate with a payment gateway and only
    credit tokens after payment confirmation.
    """
    if request.method == "POST":
        form = BuyTokensForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount_tokens"]

            account = UserTokenAccount.objects.select_for_update().get(user=request.user)
            account.token_balance = F("token_balance") + amount
            account.save()

            TokenTopUp.objects.create(
                user=request.user,
                amount_tokens=amount,
                description="Manual top-up (no real payment yet)",
            )

            messages.success(
                request,
                f"Your balance was increased by {amount} UPBolis."
            )
            return redirect("dashboard")
    else:
        form = BuyTokensForm()

    return render(request, "buy_tokens.html", {"form": form})

def get_api_key_from_request(request):
    """
    Try to read API key from:
    - X-API-Key header
    - ?api_key=
    - POST body field 'api_key'
    """
    key = (
        request.headers.get("X-API-Key")
        or request.GET.get("api_key")
        or request.POST.get("api_key")
    )
    if not key:
        return None
    try:
        return VendorAPIKey.objects.select_related("vendor").get(
            key=key,
            is_active=True,
        )
    except VendorAPIKey.DoesNotExist:
        return None

@csrf_exempt
@require_http_methods(["GET"])
def api_purchase_detail(request, pk):
    api_key = get_api_key_from_request(request)
    if not api_key:
        return JsonResponse({"error": "Invalid or missing API key"}, status=401)

    try:
        purchase = Purchase.objects.select_related(
            "user",
            "product",
            "product__owner",
        ).get(pk=pk)
    except Purchase.DoesNotExist:
        return JsonResponse({"error": "Purchase not found"}, status=404)

    # Only allow if this vendor owns the product
    if purchase.product.owner != api_key.vendor:
        return JsonResponse({"error": "Not authorized for this purchase"}, status=403)

    data = {
        "id": purchase.pk,
        "buyer": {
            "id": purchase.user.pk,
            "username": purchase.user.username,
        },
        "product": {
            "id": purchase.product.pk,
            "name": purchase.product.name,
        },
        "quantity": purchase.quantity,
        "total_tokens": purchase.total_tokens,
        "created_at": purchase.created_at.isoformat(),
        "vendor": {
            "id": api_key.vendor.pk,
            "username": api_key.vendor.username,
        },
    }
    return JsonResponse(data, status=200)

@csrf_exempt
@require_http_methods(["POST"])
@transaction.atomic
def api_transfer_tokens(request):
    api_key = get_api_key_from_request(request)
    if not api_key:
        return JsonResponse({"error": "Invalid or missing API key"}, status=401)

    # Parse body try JSON, then if we fail form-encoded 
    payload = {}

    if request.body:
        raw_text = request.body.decode("utf-8", errors="replace")
        try:
            # Try JSON first
            payload = json.loads(raw_text)
        except json.JSONDecodeError:
            # Fall back to form data (curl -d "a=1&b=2")
            if request.POST:
                payload = request.POST
            else:
                # De ultima - tiramos error y mostramos el cuerpo para debuggear si algo sale mal
                return JsonResponse(
                    {
                        "error": "Invalid body; expected JSON or form data",
                        "raw_body": raw_text,
                    },
                    status=400,
                )
    else:
        # No raw body, maybe standard form POST
        payload = request.POST or {}

    recipient_username = payload.get("recipient_username")
    amount = payload.get("amount_tokens")
    description = payload.get("description", "")

    if not recipient_username:
        return JsonResponse({"error": "recipient_username is required"}, status=400)
    if amount is None:
        return JsonResponse({"error": "amount_tokens is required"}, status=400)

    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return JsonResponse({"error": "amount_tokens must be an integer"}, status=400)

    if amount <= 0:
        return JsonResponse({"error": "amount_tokens must be > 0"}, status=400)

    from_user = api_key.vendor

    from django.contrib.auth.models import User
    try:
        to_user = User.objects.get(username=recipient_username)
    except User.DoesNotExist:
        return JsonResponse({"error": "Recipient user not found"}, status=404)

    if from_user == to_user:
        return JsonResponse({"error": "Cannot transfer tokens to self"}, status=400)

    from_account = UserTokenAccount.objects.select_for_update().get(user=from_user)
    to_account = UserTokenAccount.objects.select_for_update().get(user=to_user)

    if from_account.token_balance < amount:
        return JsonResponse({"error": "Insufficient balance"}, status=400)

    from_account.token_balance = F("token_balance") - amount
    to_account.token_balance = F("token_balance") + amount
    from_account.save()
    to_account.save()

    transfer = TokenTransfer.objects.create(
        from_user=from_user,
        to_user=to_user,
        amount_tokens=amount,
        description=description,
        api_key=api_key,
    )

    from_account.refresh_from_db()
    to_account.refresh_from_db()

    data = {
        "status": "ok",
        "transfer_id": transfer.pk,
        "from_user": {
            "username": from_user.username,
            "new_balance": from_account.token_balance,
        },
        "to_user": {
            "username": to_user.username,
            "new_balance": to_account.token_balance,
        },
        "amount_tokens": amount,
        "description": description,
        "created_at": transfer.created_at.isoformat(),
    }
    return JsonResponse(data, status=201)

@login_required
@user_passes_test(is_vendor)
def vendor_api_keys(request):
    keys = VendorAPIKey.objects.filter(vendor=request.user).order_by("-created_at")

    if request.method == "POST":
        name = request.POST.get("name") or "Default API key"
        VendorAPIKey.objects.create(vendor=request.user, name=name)
        messages.success(request, "New API key created.")
        return redirect("vendor_api_keys")

    return render(request, "vendor_api_keys.html", {"keys": keys})

def send_purchase_webhooks(purchase: Purchase):
    """
    Notify all active webhooks for the vendor that owns the product
    for this purchase.
    """
    vendor = purchase.product.owner
    if not vendor:
        return

    webhooks = VendorWebhook.objects.filter(vendor=vendor, is_active=True)
    if not webhooks.exists():
        return

    payload = {
        "event": "purchase.created",
        "purchase": {
            "id": purchase.pk,
            "buyer": {
                "id": purchase.user.pk,
                "username": purchase.user.username,
            },
            "product": {
                "id": purchase.product.pk,
                "name": purchase.product.name,
            },
            "quantity": purchase.quantity,
            "total_tokens": purchase.total_tokens,
            "created_at": purchase.created_at.isoformat(),
        },
        "vendor": {
            "id": vendor.pk,
            "username": vendor.username,
        },
    }

    body = json.dumps(payload)

    for webhook in webhooks:
        headers = {
            "Content-Type": "application/json",
        }

        # Optional HMAC signature with secret
        if webhook.secret:
            signature = hmac.new(
                webhook.secret.encode("utf-8"),
                body.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            headers["X-UPBT-Signature"] = signature

        try:
            # Best-effort: don't crash the main request if webhook fails
            requests.post(webhook.url, data=body, headers=headers, timeout=5)
        except Exception as e:
            # In real life, log this properly
            print(f"Error sending webhook to {webhook.url}: {e}")

@login_required
@user_passes_test(is_vendor)
def vendor_webhooks(request):
    # Assume at most 1 webhook per vendor for simplicity
    webhook, created = VendorWebhook.objects.get_or_create(
        vendor=request.user,
        defaults={"url": "", "is_active": False},
    )

    if request.method == "POST":
        url = (request.POST.get("url") or "").strip()
        secret = (request.POST.get("secret") or "").strip()
        is_active = request.POST.get("is_active") == "on"

        webhook.url = url
        webhook.secret = secret
        # Only activate if we have a non-empty URL
        webhook.is_active = bool(url) and is_active
        webhook.save()

        messages.success(request, "Webhook settings updated.")
        return redirect("vendor_webhooks")

    return render(request, "vendor_webhooks.html", {"webhook": webhook})
