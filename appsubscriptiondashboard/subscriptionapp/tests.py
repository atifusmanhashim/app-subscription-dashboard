from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import SubscriptionPlan, UserApp, UserAppSubscription
from authapp.models import AppUser


class SubscriptionAppTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = AppUser.objects.create_user(email='test@example.com', password='password123')
        self.subscription_plan = SubscriptionPlan.objects.create(
            subscription_plan_name='Free Plan',
            subscription_plan_price=0.00
        )
        self.user_app = UserApp.objects.create(
            app_owner=self.user,
            app_name='Test App',
            app_description='This is a test app.'
        )
        self.user_app_subscription = UserAppSubscription.objects.create(
            subscription_app=self.user_app,
            subscription_plan=self.subscription_plan,
            subscription_user=self.user
        )

    def test_create_user_app(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'app_name': 'New App',
            'app_description': 'This is a new app.'
        }
        response = self.client.post('/api/user-app/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserApp.objects.filter(app_name='New App').exists())

    def test_update_user_app(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'app_name': 'Updated App',
            'app_description': 'This is an updated app.'
        }
        response = self.client.put(f'/api/user-app/{self.user_app.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_app.refresh_from_db()
        self.assertEqual(self.user_app.app_name, 'Updated App')

    def test_delete_user_app(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/user-app/{self.user_app.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserApp.objects.filter(id=self.user_app.id).exists())

    def test_read_selected_user_app(self):
        response = self.client.get(f'/api/user-app/{self.user_app.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['app_name'], 'Test App')

    
    def test_active_apps_with_subscription_plan(self):
        response = self.client.get('/api/active-apps-with-subscription-plan/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Assuming only one active app with a subscription plan

    def test_active_subscriptions(self):
        response = self.client.get('/api/active-subscriptions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Assuming only one active subscription

    # All Inactive Subscription Listing
    def test_inactive_subscriptions(self):
        response = self.client.get('/api/inactive-subscriptions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Assuming no inactive subscriptions

    # All Subscription Plans Listing
    def test_all_subscription_plans(self):
        response = self.client.get('/api/subscription/subscription-plans/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Assuming only one subscription plan


