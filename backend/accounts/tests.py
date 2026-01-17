from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')

        # Create an Admin user
        self.admin_data = {
            'email': 'admin@example.com',
            'password': 'adminpassword',
            'role': 'ADMIN'
        }
        self.admin_user = User.objects.create_superuser(
            email=self.admin_data['email'],
            password=self.admin_data['password']
        )

        # Create an HR user
        self.hr_data = {
            'email': 'hr@example.com',
            'password': 'hrpassword',
            'role': 'HR'
        }
        self.hr_user = User.objects.create_user(
            email=self.hr_data['email'],
            password=self.hr_data['password'],
            role='HR'
        )

    def test_admin_can_register_hr(self):
        """Admin should be able to register an HR user."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'email': 'newhr@example.com',
            'password': 'newpassword',
            'full_name': 'New HR',
            'role': 'HR'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email='newhr@example.com').count(), 1)
        self.assertEqual(User.objects.get(email='newhr@example.com').role, 'HR')

    def test_hr_cannot_register_hr(self):
        """HR user should NOT be able to register another HR user."""
        self.client.force_authenticate(user=self.hr_user)
        data = {
            'email': 'anotherhr@example.com',
            'password': 'newpassword',
            'full_name': 'Another HR',
            'role': 'HR'
        }
        response = self.client.post(self.register_url, data)
        # Expecting 403 Forbidden because of permission check
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_register_hr(self):
        """Anonymous user should NOT be able to register an HR user."""
        data = {
            'email': 'anonhr@example.com',
            'password': 'newpassword',
            'full_name': 'Anon HR',
            'role': 'HR'
        }
        response = self.client.post(self.register_url, data)
        # Permission denied in perform_create
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_returns_token(self):
        """Login should return access and refresh tokens."""
        data = {
            'email': self.hr_data['email'],
            'password': self.hr_data['password']
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], self.hr_data['email'])

    def test_profile_requires_auth(self):
        """Profile endpoint should require authentication."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_data(self):
        """Profile endpoint should return user data."""
        self.client.force_authenticate(user=self.hr_user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.hr_data['email'])
        self.assertEqual(response.data['role'], 'HR')
