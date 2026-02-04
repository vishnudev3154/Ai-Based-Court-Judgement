from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("userpage/", views.user_dashboard, name="userpage"),

    # ✅ Gemini AI API
    # path("api/chat/", views.ai_chat, name="api_chat"),
    path('chat/', views.chat_view, name='chat'),
    path('chat/history/<int:session_id>/', views.get_chat_history, name='get_chat_history'),
    path('my-cases/', views.my_cases_view, name='my_cases'),
    path('create-case/', views.create_case_view, name='create_case'),
]
