import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import api_login_required, role_required
from django.views.decorators.http import require_POST


API_BASE = settings.API_BASE_URL

def redirect_to_login(request):
    return redirect('login')

def login_view(request):
    # GET: mostrar formulario
    if request.method == 'GET':
        if request.session.get('api_token') and request.session.get('api_user'):
            return redirect('dashboard')
        return render(request, 'login.html')

    # POST: procesar login contra Laravel
    email = request.POST.get('email')
    password = request.POST.get('password')

    try:
        resp = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": email, "password": password},
            timeout=5,
        )
    except Exception as e:
        messages.error(request, f"No se pudo conectar con la API: {e}")
        return render(request, 'login.html', status=502)

    status = resp.status_code
    raw = (resp.text or "")[:300]  # primeros 300 chars para debug

    # Intentamos parsear JSON, pero sin romper si no lo es
    data = None
    try:
        data = resp.json()
    except Exception:
        data = None

    # Si no es 200, mostramos mensaje de error amigable
    if status != 200:
        msg = None
        if isinstance(data, dict):
            msg = data.get('message') or data.get('error')

        if not msg:
            msg = f"Error {status} desde la API. Respuesta: {raw}"

        messages.error(request, msg)
        return render(request, 'login.html', status=status)

    # Si es 200 pero no es JSON válido
    if not isinstance(data, dict):
        messages.error(request, f"La API devolvió una respuesta no JSON: {raw}")
        return render(request, 'login.html', status=500)

    token = data.get('token')
    user = data.get('user')

    if not token or not user:
        messages.error(request, f"Respuesta inesperada de la API: {data}")
        return render(request, 'login.html', status=500)

    # Guardar en sesión (para acceso en templates)
    request.session['api_token'] = token
    request.session['api_user'] = user

    # Redirigir según rol (el token se maneja en cliente con localStorage)
    role = str(user.get('role', '')).lower()
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'seller':
        return redirect('seller_dashboard')
    else:
        return redirect('buyer_dashboard')


def register_view(request):
    # GET: mostrar formulario
    if request.method == 'GET':
        if request.session.get('api_token') and request.session.get('api_user'):
            return redirect('dashboard')
        return render(request, 'register.html')

    # POST: enviar registro a la API Laravel
    name = request.POST.get('name')
    email = request.POST.get('email')
    password = request.POST.get('password')
    password_confirmation = request.POST.get('password_confirmation')

    try:
        resp = requests.post(
            f"{API_BASE}/auth/register",
            json={
                "name": name,
                "email": email,
                "password": password,
                "password_confirmation": password_confirmation,
            },
            timeout=5,
        )
    except Exception as e:
        messages.error(request, f"No se pudo conectar con la API: {e}")
        return render(request, 'register.html', status=502)

    status = resp.status_code
    raw = (resp.text or "")[:400]

    data = None
    try:
        data = resp.json()
    except Exception:
        data = None

    if status not in (200, 201):
        msg = None
        if isinstance(data, dict):
            # Laravel validation errors may be in 'message' or 'errors'
            msg = data.get('message') or data.get('error')
            if not msg and data.get('errors'):
                # join validation messages
                errors = data.get('errors')
                msgs = []
                for k, v in errors.items(): # type: ignore (Because it's not really relevant i think)
                    if isinstance(v, list):
                        msgs.extend(v)
                    else:
                        msgs.append(str(v))
                msg = '; '.join(msgs)

        if not msg:
            msg = f"Error {status} desde la API. Respuesta: {raw}"

        messages.error(request, msg)
        return render(request, 'register.html', status=status)

    if not isinstance(data, dict):
        messages.error(request, f"Respuesta inesperada de la API: {raw}")
        return render(request, 'register.html', status=500)

    token = data.get('token')
    user = data.get('user')

    if not token or not user:
        messages.error(request, f"Respuesta inesperada de la API: {data}")
        return render(request, 'register.html', status=500)

    # Guardar en sesión y redirigir
    request.session['api_token'] = token
    request.session['api_user'] = user

    role = str(user.get('role', '')).lower()
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'seller':
        return redirect('seller_dashboard')
    else:
        return redirect('buyer_dashboard')

def logout_view(request):
    token = request.session.get('api_token')
    if token:
        try:
            requests.post(
                f"{API_BASE}/auth/logout",
                headers={"Authorization": f"Bearer {token}"}
            )
        except Exception:
            pass  # ignoramos error

    request.session.flush()
    return redirect('login')


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


@api_login_required
@role_required('buyer')
def buyer_dashboard(request):
    token = request.session.get('api_token')
    headers = {"Authorization": f"Bearer {token}"}

    # Wallet
    wallet = None
    try:
        r = requests.get(f"{API_BASE}/wallet", headers=headers)
        if r.status_code == 200:
            wallet = r.json().get('wallet')
    except Exception:
        wallet = None

    # Productos
    products = []
    try:
        r = requests.get(f"{API_BASE}/products", headers=headers)
        if r.status_code == 200:
            products = r.json()
    except Exception:
        products = []

    return render(request, 'buyer_dashboard.html', {
        'user': request.session.get('api_user'),
        'wallet': wallet,
        'products': products,
    })


@api_login_required
@role_required('seller', 'admin')
def seller_dashboard(request):
    token = request.session.get('api_token')
    headers = {"Authorization": f"Bearer {token}"}

    products = []
    try:
        r = requests.get(f"{API_BASE}/seller/products", headers=headers)
        if r.status_code == 200:
            products = r.json()
    except Exception:
        products = []

    return render(request, 'seller_dashboard.html', {
        'user': request.session.get('api_user'),
        'products': products,
    })


@api_login_required
@role_required('admin')
def admin_dashboard(request):
    token = request.session.get('api_token')
    headers = {"Authorization": f"Bearer {token}"}

    users = []
    try:
        # cuando tengas este endpoint creado en Laravel
        r = requests.get(f"{API_BASE}/admin/users", headers=headers)
        if r.status_code == 200:
            users = r.json()
    except Exception:
        users = []

    return render(request, 'admin_dashboard.html', {
        'user': request.session.get('api_user'),
        'users': users,
    })

# Unused
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
