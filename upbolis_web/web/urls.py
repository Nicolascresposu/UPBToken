
from django.urls import path
from . import views

urlpatterns = [
    path('', views.redirect_to_login, name='home'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    # Unused
    path(
        'admin/users/<int:user_id>/role/',
        views.admin_update_user_role,
        name='admin_update_user_role',
    ),
    path(
        'admin/users/<int:user_id>/toggle-active/',
        views.admin_toggle_user_active,
        name='admin_toggle_user_active',
    ),
]
