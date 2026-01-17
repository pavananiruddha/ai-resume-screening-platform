import tempfile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from jobs.models import Job
from .models import Resume

User = get_user_model()

from django.core.files.base import ContentFile

class ScreeningTests(APITestCase):
    def setUp(self):
        self.screener_url = reverse('screening-run')
        
        # Create Admin
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='password'
        )
        
        # Create Job
        self.job = Job.objects.create(
            title="Python Developer",
            description="We are looking for a Python Developer with Django and DRF experience."
        )
        
        # Create Resume
        self.resume = Resume.objects.create(
            job=self.job,
            user=self.admin,
            candidate_name="John Doe",
            candidate_email="john@example.com"
        )
        # Properly save file content so .path works
        self.resume.resume_file.save('resume.txt', ContentFile(b"I am a Python Developer with experience in Django and DRF."))

    def test_screening_requires_auth(self):
        response = self.client.post(self.screener_url, {'resume_id': self.resume.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_screening_logic(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.screener_url, {'resume_id': self.resume.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['id'], self.resume.id)
        self.assertEqual(data['status'], 'SHORTLISTED') # Expect match
        self.assertGreater(data['score'], 0)
        self.assertIn('python', [k.lower() for k in data['matched_keywords']])

    def test_screening_invalid_id(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.screener_url, {'resume_id': 9999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
