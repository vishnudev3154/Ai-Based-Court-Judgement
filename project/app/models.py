from django.db import models
from django.contrib.auth.models import User

# ---------------- AI CHAT MODELS ----------------
class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat {self.id} by {self.user.username}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    text = models.TextField()
    is_user = models.BooleanField(default=True) # True = User, False = AI
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'User' if self.is_user else 'AI'}: {self.text[:20]}"


# ---------------- PREDICTION & FEEDBACK ----------------
class Prediction(models.Model):
    result = models.CharField(max_length=100)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.result

class Feedback(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:40]


## app/models.py
class CaseSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    case_title = models.CharField(max_length=200)
    case_text = models.TextField(blank=True, null=True) # Optional if uploading file
    document = models.FileField(upload_to="case_docs/", blank=True, null=True)
    
    # New field to store the AI output
    analysis_result = models.TextField(blank=True, null=True)
    
    is_reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.case_title