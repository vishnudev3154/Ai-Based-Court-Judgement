from django.contrib import admin as django_admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', django_admin.site.urls),

    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('userpage/', views.user_dashboard, name='userpage'),
]
