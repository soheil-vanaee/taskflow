from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from tasks.models import Task, Project


User = get_user_model()


class TaskModelTest(TestCase):
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

    def test_create_task(self):
        """Test creating a task"""
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.project, self.project)
        self.assertFalse(task.is_completed)

    def test_task_status_transitions(self):
        """Test valid task status transitions"""
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project
        )
        
        # Test valid transition
        self.assertTrue(task.can_transition_to_status(Task.Status.IN_PROGRESS))
        
        # Change status and test another transition
        task.status = Task.Status.IN_PROGRESS
        self.assertTrue(task.can_transition_to_status(Task.Status.REVIEW))
        self.assertTrue(task.can_transition_to_status(Task.Status.TODO))

    def test_task_dependencies(self):
        """Test task dependencies"""
        task1 = Task.objects.create(
            title='Task 1',
            description='Description 1',
            project=self.project
        )
        task2 = Task.objects.create(
            title='Task 2',
            description='Description 2',
            project=self.project
        )
        
        # Add task1 as dependency of task2
        task2.dependencies.add(task1)
        
        self.assertIn(task1, task2.dependencies.all())
        self.assertIn(task2, task1.dependents.all())


class TaskAPITest(APITestCase):
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
        self.client.force_authenticate(user=self.user)
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'project': self.project.id
        }

    def test_create_task(self):
        """Test creating a task"""
        url = reverse('task-list')
        response = self.client.post(url, self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.task_data['title'])

    def test_update_task_status(self):
        """Test updating task status"""
        # Create a task first
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project
        )
        
        url = reverse('update-task-status', kwargs={'task_id': task.id})
        response = self.client.post(url, {'status': 'in_progress'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task']['status'], 'in_progress')