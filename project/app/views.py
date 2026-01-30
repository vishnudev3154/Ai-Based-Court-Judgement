from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages

from .models import CaseSubmission, Prediction, Feedback


# ---------------- HOME ----------------
def home(request):
    return render(request, "index.html")


# ---------------- USER REGISTRATION ----------------
def register_view(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "register.html")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return render(request, "register.html")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        if fullname:
            names = fullname.split(" ", 1)
            user.first_name = names[0]
            if len(names) > 1:
                user.last_name = names[1]

        user.is_staff = False  # ❌ NOT admin
        user.save()

        messages.success(request, "Registration successful")
        return redirect("userpage")

    return render(request, "register.html")


# ---------------- ADMIN LOGIN ----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")

        messages.error(request, "Admin access only")

    return render(request, "login.html")


# ---------------- LOGOUT ----------------
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------- ADMIN CHECK ----------------
def is_admin(user):
    return user.is_staff


# ---------------- ADMIN DASHBOARD ----------------
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    context = {
        "total_users": User.objects.filter(is_staff=False).count(),
        "total_cases": CaseSubmission.objects.count(),
        "total_predictions": Prediction.objects.count(),
        "total_feedback": Feedback.objects.count(),
        "recent_cases": CaseSubmission.objects.order_by("-created_at")[:5],
        "feedbacks": Feedback.objects.order_by("-created_at")[:5],
        "model_accuracy": "78%",
        "model_status": "Stable",
    }
    return render(request, "admin_dashboard.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_users(request):
    users = User.objects.filter(is_staff=False)

    return render(request, "admin_manage_users.html", {
        "users": users
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def toggle_user_status(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect("manage_users")



@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_cases(request):
    cases = CaseSubmission.objects.all().order_by("-created_at")
    return render(request, "admin_manage_cases.html", {
        "cases": cases
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def review_case(request, case_id):
    case = CaseSubmission.objects.get(id=case_id)
    case.is_reviewed = True
    case.save()
    return redirect("manage_cases")


@login_required
@user_passes_test(lambda u: u.is_staff)
def flag_case(request, case_id):
    case = CaseSubmission.objects.get(id=case_id)
    case.is_flagged = not case.is_flagged
    case.save()
    return redirect("manage_cases")



# ---------------- PUBLIC USER PAGE ----------------
def user_dashboard(request):
    return render(request, "userpage.html")
