from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from projects.models import Project


User = get_user_model()


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_create_project(self):
        """Test creating a project"""
        project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            owner=self.user
        )
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.owner, self.user)
        self.assertFalse(project.is_overdue)

    def test_project_access_permissions(self):
        """Test project access permissions"""
        project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            owner=self.user
        )
        
        # Owner should have access
        self.assertTrue(project.can_user_access(self.user))
        
        # Another user should not have access initially
        other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='testpass123'
        )
        self.assertFalse(project.can_user_access(other_user))
        
        # After adding as member, should have access
        project.members.add(other_user)
        self.assertTrue(project.can_user_access(other_user))


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.project_data = {
            'name': 'Test Project',
            'description': 'Test Description'
        }

    def test_create_project(self):
        """Test creating a project"""
        url = reverse('project-list')
        response = self.client.post(url, self.project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.project_data['name'])
        self.assertEqual(response.data['owner'], str(self.user))

    def test_get_project_list(self):
        """Test getting project list"""
        # Create a project first
        Project.objects.create(name='Test Project', description='Test Desc', owner=self.user)
        
        url = reverse('project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)