from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import AppUser

class UserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User',
            'contact_no': '1234567890',
        }
        self.user = get_user_model().objects.create_user(**self.user_data)

    def test_register_user(self):
        response = self.client.post('/api/user/register/', self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AppUser.objects.count(), 2)  # Ensure user is created
        self.assertEqual(AppUser.objects.last().email, 'test@example.com')

    def test_login_user(self):
        login_data = {
            'email': 'test@example.com',
            'password': 'password123',
        }
        response = self.client.post('/api/user/login/', login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_reset_password(self):
        reset_data = {
            'email': 'test@example.com',
            'new_password': 'newpassword456',
        }
        response = self.client.post('/api/user/resetpassword/', reset_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))

