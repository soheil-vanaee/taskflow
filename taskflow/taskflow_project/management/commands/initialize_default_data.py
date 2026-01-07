from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from subscriptions.models import SubscriptionPlan

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize default data for the application'

    def handle(self, *args, **options):
        # Create default subscription plans
        free_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Free',
            defaults={
                'description': 'Free plan with basic features',
                'price': 0,
                'projects_limit': 1,
                'team_members_limit': 2,
                'tasks_limit': 50,
                'features': ['Basic project management', 'Up to 1 project', 'Up to 2 team members', 'Up to 50 tasks'],
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created Free plan: {free_plan.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Free plan already exists: {free_plan.name}')
            )
        
        pro_plan, created = SubscriptionPlan.objects.get_or_create(
            name='Pro',
            defaults={
                'description': 'Professional plan with advanced features',
                'price': 19.99,
                'projects_limit': -1,  # Unlimited
                'team_members_limit': -1,  # Unlimited
                'tasks_limit': -1,  # Unlimited
                'features': ['Unlimited projects', 'Unlimited team members', 'Unlimited tasks', 'Advanced reporting', 'Priority support'],
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created Pro plan: {pro_plan.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Pro plan already exists: {pro_plan.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Default data initialization completed!')
        )