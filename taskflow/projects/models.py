from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Project(models.Model):
    """
    Project model representing a project with tasks and team members
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='projects',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def clean(self):
        """
        Validate that the project deadline is not in the past
        """
        if self.deadline and self.deadline < timezone.now():
            raise ValidationError('Project deadline cannot be in the past.')

    def save(self, *args, **kwargs):
        """
        Override save to perform validation
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def can_user_access(self, user):
        """
        Check if a user can access this project
        """
        return user == self.owner or user in self.members.all()

    def can_user_modify(self, user):
        """
        Check if a user can modify this project (only owner can)
        """
        return user == self.owner

    def can_user_delete(self, user):
        """
        Check if a user can delete this project (only owner can)
        """
        return user == self.owner

    @property
    def is_overdue(self):
        """
        Check if the project is overdue
        """
        if self.deadline:
            return self.deadline < timezone.now() and not self.is_completed
        return False

    @property
    def is_completed(self):
        """
        Check if all tasks in the project are completed
        """
        return all(task.is_completed for task in self.tasks.all())

    @property
    def progress_percentage(self):
        """
        Calculate the progress percentage of the project based on completed tasks
        """
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0

        completed_tasks = self.tasks.filter(status='completed').count()
        return round((completed_tasks / total_tasks) * 100, 2)
