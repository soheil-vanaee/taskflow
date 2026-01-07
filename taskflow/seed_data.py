"""
Seed data script for development environment
"""
from django.contrib.auth import get_user_model
from projects.models import Project
from tasks.models import Task
from subscriptions.models import SubscriptionPlan, UserSubscription
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


def create_sample_data():
    print("Creating sample data...")
    
    # Create sample users
    owner_user = User.objects.create_user(
        email='owner@example.com',
        username='project_owner',
        password='password123',
        first_name='Project',
        last_name='Owner',
        role=User.Role.OWNER
    )
    
    member_user = User.objects.create_user(
        email='member@example.com',
        username='team_member',
        password='password123',
        first_name='Team',
        last_name='Member',
        role=User.Role.MEMBER
    )
    
    print(f"Created users: {owner_user.email}, {member_user.email}")
    
    # Create sample projects
    project1 = Project.objects.create(
        name='Website Redesign',
        description='Redesign company website with modern UI/UX',
        deadline=timezone.now() + timedelta(days=30),
        owner=owner_user
    )
    project1.members.add(owner_user, member_user)
    
    project2 = Project.objects.create(
        name='Mobile App Development',
        description='Develop cross-platform mobile application',
        deadline=timezone.now() + timedelta(days=60),
        owner=owner_user
    )
    project2.members.add(owner_user, member_user)
    
    print(f"Created projects: {project1.name}, {project2.name}")
    
    # Create sample tasks for project 1
    task1 = Task.objects.create(
        title='Design Homepage',
        description='Create wireframes and mockups for homepage',
        status=Task.Status.COMPLETED,
        priority=Task.Status.HIGH,
        deadline=timezone.now() + timedelta(days=5),
        project=project1,
        assignee=owner_user
    )
    
    task2 = Task.objects.create(
        title='Implement Contact Form',
        description='Create and implement contact form with validation',
        status=Task.Status.IN_PROGRESS,
        priority=Task.Status.MEDIUM,
        deadline=timezone.now() + timedelta(days=10),
        project=project1,
        assignee=member_user
    )
    
    task3 = Task.objects.create(
        title='Setup CI/CD Pipeline',
        description='Configure continuous integration and deployment',
        status=Task.Status.TODO,
        priority=Task.Status.LOW,
        deadline=timezone.now() + timedelta(days=15),
        project=project1,
        assignee=owner_user
    )
    
    # Create sample tasks for project 2
    task4 = Task.objects.create(
        title='Research Native Features',
        description='Investigate platform-specific features for mobile app',
        status=Task.Status.COMPLETED,
        priority=Task.Status.HIGH,
        deadline=timezone.now() + timedelta(days=7),
        project=project2,
        assignee=member_user
    )
    
    task5 = Task.objects.create(
        title='Create Login Screen',
        description='Design and implement user login screen',
        status=Task.Status.IN_PROGRESS,
        priority=Task.Status.HIGH,
        deadline=timezone.now() + timedelta(days=12),
        project=project2,
        assignee=owner_user
    )
    
    task6 = Task.objects.create(
        title='Implement Push Notifications',
        description='Add push notification functionality',
        status=Task.Status.TODO,
        priority=Task.Status.MEDIUM,
        deadline=timezone.now() + timedelta(days=25),
        project=project2,
        assignee=member_user
    )
    
    # Create dependency: task3 depends on task2
    task3.dependencies.add(task2)
    
    print(f"Created tasks: {task1.title}, {task2.title}, {task3.title}, {task4.title}, {task5.title}, {task6.title}")
    
    # Create sample subscription
    free_plan = SubscriptionPlan.objects.get(name='Free')
    UserSubscription.objects.get_or_create(
        user=owner_user,
        defaults={
            'plan': free_plan,
            'status': UserSubscription.Status.ACTIVE
        }
    )
    
    UserSubscription.objects.get_or_create(
        user=member_user,
        defaults={
            'plan': free_plan,
            'status': UserSubscription.Status.ACTIVE
        }
    )
    
    print("Sample data creation completed!")
    print("\nLogin credentials:")
    print("- Owner: owner@example.com / password123")
    print("- Member: member@example.com / password123")


if __name__ == '__main__':
    create_sample_data()