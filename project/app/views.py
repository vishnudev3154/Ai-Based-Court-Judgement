from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import CaseSubmission, Prediction, Feedback
from .gemini_chat import ask_ai


# ---------------- HOME ----------------
def home(request):
    return render(request, "index.html")


# ---------------- USER REGISTRATION ----------------
def register_view(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")  # ✅ FIXED

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

        user.is_staff = False
        user.save()

        messages.success(request, "Registration successful. Please login.")
        return redirect("login")

    return render(request, "register.html")


# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_staff:
                return redirect("admin_dashboard")
            return redirect("userpage")

        messages.error(request, "Invalid username or password")

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
        "admin_name": request.user.get_full_name() or request.user.username,
        "total_users": User.objects.filter(is_staff=False).count(),
        "total_cases": CaseSubmission.objects.count(),
        "total_predictions": Prediction.objects.count(),
        "total_feedback": Feedback.objects.count(),
    }
    return render(request, "admin_dashboard.html", context)


# ---------------- USER DASHBOARD ----------------
@login_required
@user_passes_test(lambda u: not u.is_staff)
def user_dashboard(request):
    return render(request, "userpage.html")


# ---------------- AI CHAT API ----------------
# app/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ChatSession, ChatMessage
from .gemini_chat import ask_ai

@login_required
def chat_view(request):
    # GET: Load the chat page with sidebar history
    if request.method == "GET":
        # Fetch all chat sessions for this user, newest first
        sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
        return render(request, 'chat.html', {'sessions': sessions})

    # POST: Handle new message
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_text = data.get('message')
            session_id = data.get('session_id') # Frontend will send this if it exists

            # 1. Get or Create Session
            if session_id:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            else:
                # Create title from first 30 chars of message
                short_title = (user_text[:30] + '..') if len(user_text) > 30 else user_text
                session = ChatSession.objects.create(user=request.user, title=short_title)

            # 2. Save User Message
            ChatMessage.objects.create(session=session, text=user_text, is_user=True)

            # 3. Get AI Response
            ai_reply = ask_ai(user_text)

            # 4. Save AI Message
            ChatMessage.objects.create(session=session, text=ai_reply, is_user=False)
            
            # Update session timestamp
            session.save() 

            return JsonResponse({
                'reply': ai_reply,
                'session_id': session.id,
                'session_title': session.title
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_chat_history(request, session_id):
    """API to fetch messages for a specific session"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    messages = session.messages.all().order_by('created_at')
    
    # Convert to JSON
    history_data = [
        {'role': 'user' if msg.is_user else 'ai', 'text': msg.text} 
        for msg in messages
    ]
    
    return JsonResponse({'messages': history_data})

# app/views.py
@login_required
def my_cases_view(request):
    # Fetch all cases submitted by the user, newest first
    cases = CaseSubmission.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        "cases": cases,
        "active_tab": "my_cases" # Used to highlight sidebar
    }
    return render(request, "my_cases.html", context)

# app/views.py
from django.shortcuts import render, redirect
from .models import CaseSubmission
from .ai_helper import analyze_case_file # Import the helper we just made

@login_required
def create_case_view(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        uploaded_file = request.FILES.get('document')

        # 1. Save the Case
        new_case = CaseSubmission.objects.create(
            user=request.user,
            case_title=title,
            case_text=description,
            document=uploaded_file,
            is_reviewed=False # Pending until AI finishes
        )

        # 2. Run AI Analysis
        # Note: In a real production app, you would use Celery to do this in the background
        # For this project, we do it immediately (user waits a few seconds)
        analysis = analyze_case_file(new_case)

        # 3. Save Result
        new_case.analysis_result = analysis
        new_case.is_reviewed = True # Mark as Analyzed
        new_case.save()

        return redirect('my_cases') # Redirect to list page

    return render(request, "create_case.html")