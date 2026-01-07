from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    """
    Model representing different subscription plans
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    projects_limit = models.IntegerField(help_text="Maximum number of projects allowed (-1 for unlimited)")
    team_members_limit = models.IntegerField(help_text="Maximum number of team members allowed (-1 for unlimited)")
    tasks_limit = models.IntegerField(help_text="Maximum number of tasks allowed (-1 for unlimited)")
    features = models.JSONField(default=list, help_text="List of features included in this plan")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return self.name

    @property
    def is_free_plan(self):
        return self.price == 0

    @property
    def has_unlimited_projects(self):
        return self.projects_limit == -1

    @property
    def has_unlimited_team_members(self):
        return self.team_members_limit == -1

    @property
    def has_unlimited_tasks(self):
        return self.tasks_limit == -1


class UserSubscription(models.Model):
    """
    Model representing a user's subscription
    """
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        TRIALING = 'trialing', 'Trialing'
        CANCELLED = 'cancelled', 'Cancelled'
        PAST_DUE = 'past_due', 'Past Due'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    def save(self, *args, **kwargs):
        # Set end date if not set and plan is not free
        if not self.end_date and not self.plan.is_free_plan:
            # Default to 30 days from start date
            self.end_date = self.start_date + timedelta(days=30)
        super().save(*args, **kwargs)

    @property
    def is_trial_period(self):
        """
        Check if the subscription is currently in trial period
        """
        if self.trial_end_date:
            return timezone.now() < self.trial_end_date
        return False

    @property
    def is_active_subscription(self):
        """
        Check if the subscription is active and not expired
        """
        if self.status != self.Status.ACTIVE:
            return False
        if self.end_date and timezone.now() > self.end_date:
            return False
        return True

    @property
    def days_until_expiry(self):
        """
        Calculate days until subscription expires
        """
        if self.end_date:
            delta = self.end_date - timezone.now()
            return delta.days
        return None

    def check_usage_limits(self, user):
        """
        Check if the user has exceeded their plan limits
        """
        from projects.models import Project
        from tasks.models import Task

        # Check projects limit
        if not self.plan.has_unlimited_projects:
            user_projects = Project.objects.filter(owner=user).count()
            if user_projects >= self.plan.projects_limit:
                return False, "Projects limit reached"

        # Check team members limit (for all projects owned by user)
        if not self.plan.has_unlimited_team_members:
            total_members = 0
            user_projects = Project.objects.filter(owner=user).prefetch_related('members')
            for project in user_projects:
                total_members += project.members.count()
            if total_members >= self.plan.team_members_limit:
                return False, "Team members limit reached"

        # Check tasks limit
        if not self.plan.has_unlimited_tasks:
            user_tasks = Task.objects.filter(project__owner=user).count()
            if user_tasks >= self.plan.tasks_limit:
                return False, "Tasks limit reached"

        return True, "Within limits"


class BillingHistory(models.Model):
    """
    Model to track billing history
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billing_history')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, default='succeeded')  # succeeded, failed, refunded
    invoice_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.amount}"
