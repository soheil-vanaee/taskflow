from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from subscriptions.models import SubscriptionPlan, UserSubscription


User = get_user_model()


class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.free_plan = SubscriptionPlan.objects.create(
            name='Free',
            description='Free plan',
            price=0,
            projects_limit=1,
            team_members_limit=2,
            tasks_limit=50
        )
        self.pro_plan = SubscriptionPlan.objects.create(
            name='Pro',
            description='Professional plan',
            price=19.99,
            projects_limit=-1,  # Unlimited
            team_members_limit=-1,  # Unlimited
            tasks_limit=-1  # Unlimited
        )

    def test_subscription_plan_creation(self):
        """Test creating subscription plans"""
        self.assertEqual(self.free_plan.name, 'Free')
        self.assertEqual(self.free_plan.price, 0)
        self.assertTrue(self.free_plan.is_free_plan)
        
        self.assertEqual(self.pro_plan.name, 'Pro')
        self.assertEqual(self.pro_plan.price, 19.99)
        self.assertFalse(self.pro_plan.is_free_plan)

    def test_user_subscription(self):
        """Test user subscription creation"""
        subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.free_plan
        )
        
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.plan, self.free_plan)
        self.assertTrue(subscription.is_active_subscription)


class SubscriptionAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.free_plan = SubscriptionPlan.objects.create(
            name='Free',
            description='Free plan',
            price=0,
            projects_limit=1,
            team_members_limit=2,
            tasks_limit=50
        )
        self.client.force_authenticate(user=self.user)

    def test_get_subscription_plans(self):
        """Test getting subscription plans"""
        url = reverse('subscription-plans')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_check_usage_limits(self):
        """Test checking usage limits"""
        url = reverse('check-usage-limits')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('within_limits', response.data)
        self.assertIn('limits', response.data)