from django.urls import path
from app import views

urlpatterns = [
    path("", views.home, name="home"),

    # Public user
    path("register/", views.register_view, name="register"),
    path("userpage/", views.user_dashboard, name="userpage"),

    # Admin only
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/users/", views.manage_users, name="manage_users"),
    path("admin/users/toggle/<int:user_id>/", views.toggle_user_status, name="toggle_user"),
    path("admin/cases/", views.manage_cases, name="manage_cases"),
    path("admin/cases/review/<int:case_id>/", views.review_case, name="review_case"),
    path("admin/cases/flag/<int:case_id>/", views.flag_case, name="flag_case"),


]
