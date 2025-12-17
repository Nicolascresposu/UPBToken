import requests
from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_http_methods

from .utils import api_login_required, role_required

API_BASE = settings.API_BASE_URL

# =========================
# HELPERS
# =========================



LA_PAZ_TZ = ZoneInfo("America/La_Paz")


def redirect_to_login(request):
    return redirect('login')

def _flatten_laravel_errors(errs):
    try:
        if isinstance(errs, dict):
            parts = []
            for k, v in errs.items():
                if isinstance(v, list) and v:
                    parts.append(f"{k}: {v[0]}")
                elif isinstance(v, str):
                    parts.append(f"{k}: {v}")
            return " · ".join(parts) if parts else ""
    except Exception:
        pass
    return ""


def _safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def _api_request(method: str, path: str, headers=None, json=None, params=None, timeout=15):
    if not path.startswith("/"):
        path = "/" + path
    url = f"{API_BASE}{path}"

    try:
        resp = requests.request(
            method=method.upper(),
            url=url,
            headers=headers or {},
            json=json,
            params=params,
            timeout=timeout,
        )
        return resp
    except Exception as e:
        return e


def api_get(path: str, headers=None, default=None):
    r = _api_request("GET", path, headers=headers)
    if isinstance(r, Exception):
        return default
    if r.status_code != 200:
        return default
    try:
        return r.json()
    except Exception:
        return default


def _format_iso_datetime(value):
    """
    ✅ SIEMPRE devuelve hora Bolivia (-04:00).
    Soporta:
      - '2025-12-16T22:34:00Z'
      - '2025-12-16T22:34:00+00:00'
      - '2025-12-16T22:34:00' (naive -> se asume UTC, y se convierte a La Paz)
      - '2025-12-16 22:34:00' (idem)
    """
    if not value:
        return "—"

    try:
        if isinstance(value, str):
            s = value.strip()

            # normalizar Z
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"

            # soportar "YYYY-MM-DD HH:MM:SS"
            s = s.replace(" ", "T")

            dt = datetime.fromisoformat(s)
        elif isinstance(value, datetime):
            dt = value
        else:
            return str(value)

        # si viene sin tz, asumimos UTC (típico backend) y lo pasamos a La Paz
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))

        dt_local = dt.astimezone(LA_PAZ_TZ)
        return dt_local.strftime("%d-%m-%Y %H:%M")

    except Exception:
        return str(value)


def _fmt_dt(iso_str: str) -> str:
    return _format_iso_datetime(iso_str)


def _normalize_order_status(raw: str) -> str:
    s = (raw or "").strip().lower()

    # variantes comunes
    if s in ("paid", "pagado", "payed", "completed", "complete", "success", "successful"):
        return "paid"
    if s in ("pending", "pendiente", "unpaid", "waiting"):
        return "pending"
    if s in ("cancelled", "canceled", "cancelado", "rejected", "failed"):
        return "cancelled"

    # fallback
    return s or "pending"


def _tx_type_label(type_raw: str) -> str:
    t = (type_raw or "").strip().lower()
    if t == "transfer":
        return "Transferencia"
    if t == "withdraw":
        return "Retiro"
    if t == "deposit":
        return "Depósito"
    return (type_raw or "—").title()


# =========================
# AUTH
# =========================

def login_view(request):
    if request.method == 'GET':
        if request.session.get('api_token') and request.session.get('api_user'):
            return redirect('dashboard')
        return render(request, 'login.html')

    email = (request.POST.get('email') or "").strip().lower()
    password = request.POST.get('password') or ""

    try:
        resp = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": email, "password": password},
            timeout=15
        )
    except Exception as e:
        messages.error(request, f"Error al conectar con la API: {e}", extra_tags="login")
        return render(request, 'login.html', status=500)

    if not resp.ok:
        msg = "Credenciales inválidas o error en la API."
        try:
            data = resp.json()
            if isinstance(data, dict):
                msg = data.get('message', msg)
        except ValueError:
            print("LOGIN API ERROR (no JSON):", resp.status_code, resp.text[:300])

        messages.error(request, msg, extra_tags="login")
        return render(request, 'login.html', status=resp.status_code)

    try:
        data = resp.json()
    except ValueError:
        print("LOGIN API NON-JSON BODY:", resp.status_code, resp.text[:300])
        messages.error(request, "La API de login devolvió una respuesta no válida.", extra_tags="login")
        return render(request, 'login.html', status=500)

    token = data.get('token')
    user = data.get('user') or data

    if not token or not user:
        print("LOGIN API INVALID DATA:", data)
        messages.error(request, 'Respuesta inválida de la API de login.', extra_tags="login")
        return render(request, 'login.html', status=500)

    request.session['api_token'] = token
    request.session['api_user'] = user

    role = str(user.get('role', '')).lower()
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'seller':
        return redirect('seller_dashboard')
    else:
        return redirect('buyer_dashboard')


def register_view(request):
    if request.method == "GET":
        return render(request, "register.html")

    name = (request.POST.get("name") or "").strip()
    email = (request.POST.get("email") or "").strip().lower()
    password = request.POST.get("password") or ""
    password_confirmation = request.POST.get("password_confirmation") or ""

    # ✅ Reglas que tú quieres
    if not name:
        messages.error(request, "Ingresa tu nombre.", extra_tags="register")
        return render(request, "register.html", status=400)

    if not email.endswith("@upbolis.com"):
        messages.error(request, "Solo se permiten correos @upbolis.com.", extra_tags="register")
        return render(request, "register.html", status=400)

    if len(password) < 8:
        messages.error(request, "La contraseña debe tener mínimo 8 caracteres.", extra_tags="register")
        return render(request, "register.html", status=400)

    if password != password_confirmation:
        messages.error(request, "Las contraseñas no coinciden.", extra_tags="register")
        return render(request, "register.html", status=400)

    # ✅ Compatibilidad Laravel: algunos esperan snake_case, otros camelCase
    payload = {
        "name": name,
        "email": email,
        "password": password,
        "password_confirmation": password_confirmation,
        "passwordConfirmation": password_confirmation,
    }

    try:
        resp = requests.post(f"{API_BASE}/auth/register", json=payload, timeout=15)
    except Exception as e:
        messages.error(request, f"Error al conectar con la API: {e}", extra_tags="register")
        return render(request, "register.html", status=500)

    if resp.status_code not in (200, 201):
        msg = "No se pudo completar el registro."
        try:
            data = resp.json()
            if isinstance(data, dict):
                msg = data.get("message") or msg
                if data.get("errors"):
                    msg = str(data["errors"])
            else:
                msg = str(data)
        except Exception:
            msg = resp.text[:300] or msg

        # 👇 esto te dice EXACTO por qué no crea
        print("REGISTER API ERROR:", resp.status_code, resp.text[:800])

        messages.error(request, msg, extra_tags="register")
        return render(request, "register.html", status=resp.status_code)

    messages.success(request, "Cuenta creada correctamente. Ahora inicia sesión.", extra_tags="login")
    return redirect("login")


def logout_view(request):
    token = request.session.get('api_token')
    if token:
        try:
            requests.post(
                f"{API_BASE}/auth/logout",
                headers={"Authorization": f"Bearer {token}"},
                timeout=15
            )
        except Exception:
            pass

    request.session.flush()
    return redirect('login')



# =========================
# DASHBOARD GENÉRICO
# =========================

@api_login_required
def dashboard_view(request):
    user = request.session.get('api_user', {})
    role = str(user.get('role', '')).lower()

    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'seller':
        return redirect('seller_dashboard')
    else:
        return redirect('buyer_dashboard')


# =========================
# BUYER DASHBOARD
# =========================

@api_login_required
@role_required('buyer')
def buyer_dashboard(request):
    token = request.session.get('api_token')
    headers = {"Authorization": f"Bearer {token}"}

    wallet = {}
    r = api_get("/wallet", headers=headers, default={})
    if isinstance(r, dict):
        wallet = r.get("wallet", {}) or {}

    products = api_get("/products", headers=headers, default=[]) or []
    orders = api_get("/orders", headers=headers, default=[]) or []
    transactions = api_get("/transactions", headers=headers, default=[]) or []

    recipients = []
    rec = api_get("/wallet/recipients", headers=headers, default={}) or {}
    if isinstance(rec, dict):
        recipients = rec.get("recipients", []) or []

    total_spent = 0
    try:
        total_spent = sum(_safe_float(o.get('total', 0)) for o in orders)
    except Exception:
        total_spent = 0

    stats = {"total_orders": len(orders), "total_spent": total_spent}

    orders_display = []
    for o in orders:
        o_copy = dict(o)
        o_copy['created_at_display'] = _format_iso_datetime(o.get('created_at'))
        orders_display.append(o_copy)

    tx_display = []
    for tx in transactions:
        t_copy = dict(tx)
        t_copy['created_at_display'] = _format_iso_datetime(tx.get('created_at'))
        tx_display.append(t_copy)

    return render(request, 'buyer_dashboard.html', {
        'user_name': request.session.get('api_user', {}).get('name'),
        'wallet': wallet,
        'products': products,
        'orders': orders_display,
        'transactions': tx_display,
        'stats': stats,
        'recipients': recipients,
    })


# =========================
# SELLER DASHBOARD
# =========================

@api_login_required
@role_required('seller', 'admin')
@require_http_methods(["GET", "POST"])
def seller_dashboard(request):
    token = request.session.get('api_token')
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        description = request.POST.get("description")

        try:
            resp = requests.post(
                f"{API_BASE}/seller/products",
                headers=headers,
                json={"name": name, "price": price, "stock": stock, "description": description},
                timeout=15,
            )
            if resp.status_code not in (200, 201):
                try:
                    data = resp.json()
                    msg = data.get("message", "No se pudo crear el producto.")
                except Exception:
                    msg = "No se pudo crear el producto."
                messages.error(request, msg)
            else:
                messages.success(request, "Producto creado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al conectar con la API: {e}")

        return redirect("seller_dashboard")

    wallet = {}
    w = api_get("/wallet", headers=headers, default={})
    if isinstance(w, dict):
        wallet = w.get("wallet", {}) or {}

    products = api_get("/seller/products", headers=headers, default=[]) or []
    orders = api_get("/seller/orders", headers=headers, default=[]) or []

    stats = {"total_products": len(products), "total_orders": len(orders)}

    return render(request, 'seller_dashboard.html', {
        'user': request.session.get('api_user'),
        'wallet': wallet,
        'products': products,
        'orders': orders,
        'stats': stats,
    })


@api_login_required
@role_required('seller', 'admin')
@require_POST
def seller_delete_product(request, product_id):
    token = request.session.get('api_token')
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.delete(f"{API_BASE}/seller/products/{product_id}", headers=headers, timeout=15)
        if resp.status_code not in (200, 204):
            try:
                data = resp.json()
                msg = data.get("message", "No se pudo eliminar el producto.")
            except Exception:
                msg = "No se pudo eliminar el producto."
            messages.error(request, msg)
        else:
            messages.success(request, "Producto eliminado correctamente.")
    except Exception as e:
        messages.error(request, f"Error al conectar con la API: {e}")

    return redirect("seller_dashboard")


# =========================
# ADMIN DASHBOARD ✅ ARREGLADO
# =========================

@api_login_required
@role_required('admin')
def admin_dashboard(request):
    token = request.session.get("api_token")
    if not token:
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}

    users = api_get("/admin/users", headers=headers, default=[]) or []
    wallets = api_get("/admin/wallets", headers=headers, default=[]) or []
    orders = api_get("/admin/orders", headers=headers, default=[]) or []
    txs = api_get("/admin/transactions", headers=headers, default=[]) or []

    users_by_id = {u.get("id"): u for u in users if isinstance(u, dict)}
    wallets_by_id = {w.get("id"): w for w in wallets if isinstance(w, dict)}

    # ÓRDENES: últimos 10
    norm_orders = []
    for o in (orders or [])[:10]:
        buyer = users_by_id.get(o.get("user_id")) or {}

        raw_status = o.get("status")
        status_norm = _normalize_order_status(raw_status)

        total = o.get("total_amount", 0)

        norm_orders.append({
            **o,
            "created_at_display": _fmt_dt(o.get("created_at")),
            "buyer_display": buyer.get("name") or "—",
            "buyer_sub": buyer.get("email") or "",
            "status_norm": status_norm,  # ✅ esto usa tu template
            "total_display": f"{_safe_float(total, 0):.2f}",
        })

    # TRANSACCIONES: últimos 10 (con monto y withdraw correcto)
    norm_txs = []
    for t in (txs or [])[:10]:
        t_type = (t.get("type") or "").strip().lower()

        from_w = wallets_by_id.get(t.get("from_wallet_id")) or {}
        to_w = wallets_by_id.get(t.get("to_wallet_id")) or {}

        from_u = users_by_id.get(from_w.get("user_id")) or {}
        to_u = users_by_id.get(to_w.get("user_id")) or {}

        user_display, user_sub = "—", ""

        if t_type == "transfer":
            user_display = (from_u.get("name") or "—") + " → " + (to_u.get("name") or "—")
            user_sub = (from_u.get("email") or "—") + " → " + (to_u.get("email") or "—")

        elif t_type == "withdraw":
            user_display = from_u.get("name") or "—"
            user_sub = from_u.get("email") or ""

        elif t_type == "deposit":
            pick = to_u if to_u else from_u
            user_display = pick.get("name") or "—"
            user_sub = pick.get("email") or ""

        amount = t.get("amount", 0)

        norm_txs.append({
            **t,
            "created_at_display": _fmt_dt(t.get("created_at")),
            "user_display": user_display,
            "user_sub": user_sub,
            "type_label": _tx_type_label(t_type),
            "amount_display": f"{_safe_float(amount, 0):.2f}",
        })

    # volumen pagado
    total_volume = 0.0
    for o in (orders or []):
        st = _normalize_order_status(o.get("status"))
        if st == "paid":
            total_volume += _safe_float(o.get("total_amount") or 0, 0)

    stats = {
        "total_users": len(users),
        "total_sellers": sum(1 for u in users if (u.get("role") == "seller")),
        "total_orders": len(orders),
        "total_volume": f"{total_volume:.2f}",
    }

    return render(request, "admin_dashboard.html", {
        "users": users,  # ✅ mostrar TODOS
        "orders": norm_orders,
        "transactions": norm_txs,
        "stats": stats,
        "counts": {
            "users_total": len(users),
            "orders_total": len(orders),
            "tx_total": len(txs),
        }
    })


# =========================
# ADMIN ACTIONS
# =========================

@api_login_required
@role_required('admin')
@require_POST
def admin_update_user_role(request, user_id):
    token = request.session.get('api_token')
    headers = {"Authorization": f"Bearer {token}"}
    new_role = request.POST.get("role")

    try:
        resp = requests.patch(
            f"{API_BASE}/admin/users/{user_id}/role",
            headers=headers,
            json={"role": new_role},
            timeout=15,
        )
        if resp.status_code not in (200, 204):
            try:
                data = resp.json()
                msg = data.get("message", "No se pudo actualizar el rol.")
            except Exception:
                msg = "No se pudo actualizar el rol."
            messages.error(request, msg)
        else:
            messages.success(request, "Rol actualizado correctamente.")
    except Exception as e:
        messages.error(request, f"Error al conectar con la API: {e}")

    return redirect("admin_dashboard")


@api_login_required
@role_required('admin')
@require_POST
def admin_toggle_user_active(request, user_id):
    token = request.session.get('api_token')
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.patch(
            f"{API_BASE}/admin/users/{user_id}/deactivate",
            headers=headers,
            timeout=15,
        )
        if resp.status_code not in (200, 204):
            try:
                data = resp.json()
                msg = data.get("message", "No se pudo cambiar el estado del usuario.")
            except Exception:
                msg = "No se pudo cambiar el estado del usuario."
            messages.error(request, msg)
        else:
            messages.success(request, "Estado del usuario actualizado.")
    except Exception as e:
        messages.error(request, f"Error al conectar con la API: {e}")

    return redirect("admin_dashboard")


@api_login_required
@role_required('admin')
@require_POST
def admin_create_user(request):
    token = request.session.get('api_token')
    admin_headers = {"Authorization": f"Bearer {token}"} if token else {}

    name = (request.POST.get("name") or "").strip()
    email = (request.POST.get("email") or "").strip().lower()
    role = request.POST.get("role", "buyer")
    initial_balance_raw = request.POST.get("initial_balance") or "0"

    raw_pass = request.POST.get("password") or ""
    raw_conf = request.POST.get("password_confirmation") or ""

    if not name or not email:
        messages.error(request, "Nombre y correo son obligatorios.")
        return redirect("admin_dashboard")

    if not email.endswith("@upbolis.com"):
        messages.error(request, "Solo se permiten correos @upbolis.com.")
        return redirect("admin_dashboard")

    used_default_password = False
    default_password = "UPBolis1234"

    if not raw_pass and not raw_conf:
        password = default_password
        password_confirmation = default_password
        used_default_password = True
    else:
        if raw_pass != raw_conf:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("admin_dashboard")
        if len(raw_pass) < 8:
            messages.error(request, "La contraseña debe tener mínimo 8 caracteres.")
            return redirect("admin_dashboard")
        password = raw_pass
        password_confirmation = raw_conf

    payload = {
        "name": name,
        "email": email,
        "password": password,
        "password_confirmation": password_confirmation,
        "passwordConfirmation": password_confirmation,  # compat
        "role": role,
    }

    try:
        resp = requests.post(
            f"{API_BASE}/auth/register",
            json=payload,
            timeout=15
        )
    except Exception as e:
        messages.error(request, f"Error al conectar con la API: {e}")
        return redirect("admin_dashboard")

    if not resp.ok:
        msg = "No se pudo crear el usuario."
        try:
            data = resp.json()
            if isinstance(data, dict):
                msg = data.get("message") or msg
                flat = _flatten_laravel_errors(data.get("errors"))
                if flat:
                    msg = f"{msg} · {flat}"
            else:
                msg = str(data)
        except Exception:
            msg = resp.text[:300] or msg

        messages.error(request, msg)
        return redirect("admin_dashboard")

    try:
        data = resp.json()
    except Exception:
        data = {}

    user_data = data.get("user") if isinstance(data, dict) and "user" in data else data
    user_id = user_data.get("id") if isinstance(user_data, dict) else None

    initial_balance = _safe_float(initial_balance_raw, 0)

    base_msg = (
        f"Usuario creado. Contraseña por defecto: {default_password}"
        if used_default_password else
        "Usuario creado correctamente."
    )

    if user_id and initial_balance > 0:
        try:
            dep = requests.post(
                f"{API_BASE}/admin/wallets/{user_id}/deposit",
                headers=admin_headers,
                json={"amount": initial_balance, "reason": "Saldo inicial desde panel de admin"},
                timeout=15,
            )
            if dep.status_code not in (200, 201):
                messages.warning(request, base_msg + " · No se pudo cargar saldo inicial.")
            else:
                messages.success(request, base_msg + f" · Se cargaron {initial_balance} UPBolis.")
        except Exception as e:
            messages.warning(request, base_msg + f" · No se pudo cargar saldo inicial ({e}).")
    else:
        messages.success(request, base_msg)

    return redirect("admin_dashboard")



@api_login_required
@role_required('admin')
@require_POST
def admin_topup_tokens(request):
    token = request.session.get('api_token')
    headers = {"Authorization": f"Bearer {token}"}

    user_id = request.POST.get("user_id")
    amount_raw = request.POST.get("amount")
    reason = request.POST.get("reason") or "Carga manual desde panel admin"

    amount = _safe_float(amount_raw, 0)
    if not user_id or amount <= 0:
        messages.error(request, "Debes seleccionar un usuario y un monto válido.")
        return redirect("admin_dashboard")

    try:
        resp = requests.post(
            f"{API_BASE}/admin/wallets/{user_id}/deposit",
            headers=headers,
            json={"amount": amount, "reason": reason},
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            try:
                data = resp.json()
                msg = data.get("message", "No se pudo cargar UPBolis al usuario.")
            except Exception:
                msg = "No se pudo cargar UPBolis al usuario."
            messages.error(request, msg)
        else:
            messages.success(request, f"Se cargaron {amount} UPBolis al usuario.")
    except Exception as e:
        messages.error(request, f"Error al conectar con la API: {e}")

    return redirect("admin_dashboard")


@api_login_required
@role_required('admin')
@require_POST
def admin_manage_user(request, user_id):
    token = request.session.get('api_token')
    headers = {"Authorization": f"Bearer {token}"}

    role = request.POST.get("role")
    amount_raw = request.POST.get("amount") or "0"
    operation = request.POST.get("operation") or "deposit"
    reason = request.POST.get("reason") or "Ajuste manual desde panel admin"

    actions_ok, errors = [], []

    if role:
        try:
            r_role = requests.patch(
                f"{API_BASE}/admin/users/{user_id}/role",
                headers=headers,
                json={"role": role},
                timeout=15,
            )
            if r_role.status_code not in (200, 204):
                try:
                    data = r_role.json()
                    msg = data.get("message", "No se pudo actualizar el rol.")
                except Exception:
                    msg = "No se pudo actualizar el rol."
                errors.append(msg)
            else:
                actions_ok.append("Rol actualizado")
        except Exception as e:
            errors.append(f"Error al actualizar rol: {e}")

    amount = _safe_float(amount_raw, 0)
    if amount > 0:
        endpoint = "deposit" if operation == "deposit" else "withdraw"
        try:
            r_wallet = requests.post(
                f"{API_BASE}/admin/wallets/{user_id}/{endpoint}",
                headers=headers,
                json={"amount": amount, "reason": reason},
                timeout=15,
            )
            if r_wallet.status_code not in (200, 201):
                try:
                    data = r_wallet.json()
                    msg = data.get("message", "No se pudo ajustar el saldo.")
                except Exception:
                    msg = "No se pudo ajustar el saldo."
                errors.append(msg)
            else:
                verb = "añadido" if endpoint == "deposit" else "restado"
                actions_ok.append(f"Saldo {verb} ({amount} UPBolis)")
        except Exception as e:
            errors.append(f"Error al ajustar saldo: {e}")

    if actions_ok:
        messages.success(request, " · ".join(actions_ok))
    if errors and not actions_ok:
        messages.error(request, " | ".join(errors))
    elif errors:
        messages.warning(request, " · ".join(errors))

    return redirect("admin_dashboard")


# =========================
# WALLET TRANSFER
# =========================

@api_login_required
@role_required('buyer', 'seller', 'admin')
@require_POST
def wallet_transfer(request):
    token = request.session.get('api_token')
    headers = {"Authorization": f"Bearer {token}"}

    to_email = request.POST.get("to_email")
    amount_raw = request.POST.get("amount")
    reason = request.POST.get("reason") or "Transferencia desde panel web"

    amount = _safe_float(amount_raw, 0)
    if not to_email or amount <= 0:
        messages.error(request, "Debes seleccionar un destinatario y un monto válido.")
        return redirect("buyer_dashboard")

    try:
        resp = requests.post(
            f"{API_BASE}/wallet/transfer",
            headers=headers,
            json={"to_email": to_email, "amount": amount, "reason": reason},
            timeout=15,
        )

        if resp.status_code not in (200, 201):
            try:
                data = resp.json()
                msg = data.get("message") or str(data)
            except Exception:
                msg = "No se pudo realizar la transferencia."
            messages.error(request, msg)
        else:
            try:
                data = resp.json()
                msg = data.get("message", "Transferencia realizada correctamente.")
            except Exception:
                msg = "Transferencia realizada correctamente."
            messages.success(request, msg)

    except Exception as e:
        messages.error(request, f"Error al conectar con la API: {e}")

    return redirect("buyer_dashboard")
