from functools import wraps
from django.shortcuts import redirect
from django.conf import settings

def api_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('api_token'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def role_required(*allowed_roles):
    """
    Uso: @role_required('buyer') o @role_required('seller', 'admin')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.session.get('api_user')
            if not user:
                return redirect('login')
            role = str(user.get('role', '')).lower()
            if allowed_roles and role not in allowed_roles:
                # Si no tiene rol correcto, mandamos al dashboard general
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
