from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import messages

def home(request):
    return render(request, 'index.html')

def register_view(request):
    if request.method == "POST":
        # 1. Get data from the form
        fullname = request.POST.get('fullname')
        role = request.POST.get('role')  # 'lawyer' (User) or 'clerk' (Admin)
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 2. Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'register.html')

        # 3. Create the User
        # We use the email as the username since the form has no username field
        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            
            # Save Full Name
            if fullname:
                names = fullname.split(' ', 1)
                user.first_name = names[0]
                if len(names) > 1:
                    user.last_name = names[1]

            # 4. Handle Roles (Admin vs User)
            if role == 'clerk':  # The form value for "Admin"
                user.is_staff = True  # Gives access to admin dashboard logic
                # user.is_superuser = True # Uncomment if you want them to have full Django Admin access
            
            user.save()
            
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')

        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
            return render(request, 'register.html')

    return render(request, 'register.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User # Import User model

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        print(f"--- DEBUGGING LOGIN ---")
        print(f"Input Username: '{username}'")
        print(f"Input Password: '{password}'")

        # 1. Check if user exists at all
        try:
            user_obj = User.objects.get(username=username)
            print(f"✅ User found: {user_obj}")
            
            # 2. Check if password matches manually
            is_password_correct = user_obj.check_password(password)
            print(f"🔑 Password Correct?: {is_password_correct}")
            
            # 3. Check if user is active
            print(f"🟢 Is Active?: {user_obj.is_active}")

        except User.DoesNotExist:
            print("❌ User NOT found in database.")

        # Actual Authentication
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect(admin_dashboard)
            return redirect("userpage")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


# 🔐 Admin-only access
def is_admin(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin)
@login_required
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")


@login_required
def user_dashboard(request):
    return render(request, "userpage.html")