# import requests
# from django.conf import settings
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .utils import api_login_required, role_required

# API_BASE = settings.API_BASE_URL


# def redirect_to_login(request):
#     return redirect('login')


# def login_view(request):
#     # GET: mostrar formulario
#     if request.method == 'GET':
#         if request.session.get('api_token') and request.session.get('api_user'):
#             return redirect('dashboard')
#         return render(request, 'login.html')

#     # POST: procesar login contra Laravel
#     email = request.POST.get('email')
#     password = request.POST.get('password')

#     try:
#         resp = requests.post(f"{API_BASE}/auth/login", json={
#             "email": email,
#             "password": password,
#         })
#     except Exception as e:
#         messages.error(request, f"Error al conectar con la API: {e}")
#         return render(request, 'login.html', status=500)

#     if resp.status_code != 200:
#         data = {}
#         try:
#             data = resp.json()
#         except Exception:
#             pass
#         msg = data.get('message', 'Credenciales inválidas o error en la API.')
#         messages.error(request, msg)
#         return render(request, 'login.html', status=401)

#     data = resp.json()
#     token = data.get('token')
#     user = data.get('user')

#     if not token or not user:
#         messages.error(request, 'Respuesta inválida de la API de login.')
#         return render(request, 'login.html', status=500)

#     # Guardar en sesión
#     request.session['api_token'] = token
#     request.session['api_user'] = user

#     role = str(user.get('role', '')).lower()
#     if role == 'admin':
#         return redirect('admin_dashboard')
#     elif role == 'seller':
#         return redirect('seller_dashboard')
#     else:
#         return redirect('buyer_dashboard')


# def logout_view(request):
#     token = request.session.get('api_token')
#     if token:
#         try:
#             requests.post(
#                 f"{API_BASE}/auth/logout",
#                 headers={"Authorization": f"Bearer {token}"}
#             )
#         except Exception:
#             pass  # ignoramos error

#     request.session.flush()
#     return redirect('login')


# @api_login_required
# def dashboard_view(request):
#     user = request.session.get('api_user', {})
#     role = str(user.get('role', '')).lower()

#     if role == 'admin':
#         return redirect('admin_dashboard')
#     elif role == 'seller':
#         return redirect('seller_dashboard')
#     else:
#         return redirect('buyer_dashboard')


# @api_login_required
# @role_required('buyer')
# def buyer_dashboard(request):
#     token = request.session.get('api_token')
#     headers = {"Authorization": f"Bearer {token}"}

#     # Wallet
#     wallet = None
#     try:
#         r = requests.get(f"{API_BASE}/wallet", headers=headers)
#         if r.status_code == 200:
#             wallet = r.json().get('wallet')
#     except Exception:
#         wallet = None

#     # Productos
#     products = []
#     try:
#         r = requests.get(f"{API_BASE}/products", headers=headers)
#         if r.status_code == 200:
#             products = r.json()
#     except Exception:
#         products = []

#     return render(request, 'buyer_dashboard.html', {
#         'user': request.session.get('api_user'),
#         'wallet': wallet,
#         'products': products,
#     })


# @api_login_required
# @role_required('seller', 'admin')
# def seller_dashboard(request):
#     token = request.session.get('api_token')
#     headers = {"Authorization": f"Bearer {token}"}

#     products = []
#     try:
#         r = requests.get(f"{API_BASE}/seller/products", headers=headers)
#         if r.status_code == 200:
#             products = r.json()
#     except Exception:
#         products = []

#     return render(request, 'seller_dashboard.html', {
#         'user': request.session.get('api_user'),
#         'products': products,
#     })


# @api_login_required
# @role_required('admin')
# def admin_dashboard(request):
#     token = request.session.get('api_token')
#     headers = {"Authorization": f"Bearer {token}"}

#     users = []
#     try:
#         # cuando tengas este endpoint creado en Laravel
#         r = requests.get(f"{API_BASE}/admin/users", headers=headers)
#         if r.status_code == 200:
#             users = r.json()
#     except Exception:
#         users = []

#     return render(request, 'admin_dashboard.html', {
#         'user': request.session.get('api_user'),
#         'users': users,
#     })
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import api_login_required, role_required

API_BASE = settings.API_BASE_URL


def redirect_to_login(request):
    return redirect('login')


# def login_view(request):
#     # GET: mostrar formulario
#     if request.method == 'GET':
#         if request.session.get('api_token') and request.session.get('api_user'):
#             return redirect('dashboard')
#         return render(request, 'login.html')

#     # POST: procesar login contra Laravel
#     email = request.POST.get('email')
#     password = request.POST.get('password')

#     try:
#         resp = requests.post(f"{API_BASE}/auth/login", json={
#             "email": email,
#             "password": password,
#         })
#     except Exception as e:
#         messages.error(request, f"Error al conectar con la API: {e}")
#         return render(request, 'login.html', status=500)

#     if resp.status_code != 200:
#         data = {}
#         try:
#             data = resp.json()
#         except Exception:
#             pass
#         msg = data.get('message', 'Credenciales inválidas o error en la API.')
#         messages.error(request, msg)
#         return render(request, 'login.html', status=401)

#     data = resp.json()
#     token = data.get('token')
#     user = data.get('user')

#     if not token or not user:
#         messages.error(request, 'Respuesta inválida de la API de login.')
#         return render(request, 'login.html', status=500)

#     # Guardar en sesión
#     request.session['api_token'] = token
#     request.session['api_user'] = user

#     role = str(user.get('role', '')).lower()
#     if role == 'admin':
#         return redirect('admin_dashboard')
#     elif role == 'seller':
#         return redirect('seller_dashboard')
#     else:
#         return redirect('buyer_dashboard')

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

    # Guardar en sesión
    request.session['api_token'] = token
    request.session['api_user'] = user

    # Redirigir según rol
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
