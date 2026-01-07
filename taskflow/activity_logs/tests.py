from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from activity_logs.models import ActivityLog, Notification
from projects.models import Project
from tasks.models import Task


User = get_user_model()


class ActivityLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            owner=self.user
        )

    def test_create_activity_log(self):
        """Test creating an activity log"""
        activity = ActivityLog.objects.create(
            user=self.user,
            action=ActivityLog.Action.CREATED,
            target=self.project,
            description='User created a project'
        )
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.action, ActivityLog.Action.CREATED)
        self.assertEqual(activity.target, self.project)

    def test_create_notification(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.Type.TASK_ASSIGNED,
            title='Test Notification',
            message='You have been assigned a task'
        )
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.notification_type, Notification.Type.TASK_ASSIGNED)
        self.assertFalse(notification.is_read)


class ActivityLogAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_activity_logs(self):
        """Test getting activity logs"""
        url = reverse('activity-log-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_notifications(self):
        """Test getting notifications"""
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_notification_as_read(self):
        """Test marking a notification as read"""
        # Create a notification first
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.Type.TASK_ASSIGNED,
            title='Test Notification',
            message='You have been assigned a task'
        )
        
        url = reverse('mark-notification-read', kwargs={'notification_id': notification.id})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from db to check if it's marked as read
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)