
from django.urls import path
from . import views

urlpatterns = [
    path('', views.redirect_to_login, name='home'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
]
