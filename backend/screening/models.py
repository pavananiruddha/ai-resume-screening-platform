from django.db import models
from jobs.models import Job
from django.conf import settings

class Resume(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("SHORTLISTED", "Shortlisted"),
        ("REJECTED", "Rejected"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="resumes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes")
    candidate_name = models.CharField(max_length=255)
    candidate_email = models.EmailField()
    resume_file = models.FileField(upload_to="resumes/")
    extracted_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    score = models.FloatField(null=True, blank=True)
    error_details = models.TextField(blank=True, null=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_name} - {self.job.title}"
