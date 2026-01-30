from django.db import models

class CaseSubmission(models.Model):
    case_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.case_text[:50]


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


class CaseSubmission(models.Model):
    case_title = models.CharField(max_length=200)
    case_text = models.TextField()
    document = models.FileField(upload_to="case_docs/", blank=True, null=True)
    is_reviewed = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.case_title