from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from projects.models import Project


class Task(models.Model):
    """
    Task model representing a task within a project
    """
    class Status(models.TextChoices):
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        REVIEW = 'review', 'Review'
        COMPLETED = 'completed', 'Completed'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    deadline = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    dependencies = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        """
        Validate task constraints
        """
        # Validate that the task deadline is not in the past
        if self.deadline and self.deadline < timezone.now():
            raise ValidationError('Task deadline cannot be in the past.')

        # Validate that a task cannot depend on itself
        # Only check if the task has been saved and has dependencies
        if self.pk:
            # Check if the task is in its own dependencies
            if self.dependencies.filter(pk=self.pk).exists():
                raise ValidationError('A task cannot depend on itself.')

        # Validate that a task cannot be completed if its dependencies are not completed
        if self.pk and self.status == self.Status.COMPLETED:
            incomplete_dependencies = self.dependencies.exclude(status=self.Status.COMPLETED)
            if incomplete_dependencies.exists():
                raise ValidationError(
                    f'Task cannot be completed until all dependencies are completed. '
                    f'Incomplete dependencies: {", ".join([task.title for task in incomplete_dependencies])}'
                )

    def save(self, *args, **kwargs):
        """
        Override save to perform validation
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def can_user_access(self, user):
        """
        Check if a user can access this task
        """
        return self.project.can_user_access(user)

    def can_user_modify(self, user):
        """
        Check if a user can modify this task
        """
        return self.project.can_user_modify(user) or user == self.assignee

    def can_user_delete(self, user):
        """
        Check if a user can delete this task (only project owner can)
        """
        return self.project.can_user_modify(user)

    @property
    def is_completed(self):
        """
        Check if the task is completed
        """
        return self.status == self.Status.COMPLETED

    @property
    def is_overdue(self):
        """
        Check if the task is overdue
        """
        if self.deadline:
            return self.deadline < timezone.now() and not self.is_completed
        return False

    def can_transition_to_status(self, new_status):
        """
        Check if the task can transition to a new status
        """
        # Define valid status transitions
        valid_transitions = {
            self.Status.TODO: [self.Status.IN_PROGRESS, self.Status.COMPLETED],
            self.Status.IN_PROGRESS: [self.Status.REVIEW, self.Status.TODO, self.Status.COMPLETED],
            self.Status.REVIEW: [self.Status.IN_PROGRESS, self.Status.COMPLETED, self.Status.TODO],
            self.Status.COMPLETED: [self.Status.IN_PROGRESS, self.Status.TODO]  # Allow reverting completed tasks
        }

        return new_status in valid_transitions.get(self.status, [])

    def get_all_dependencies(self):
        """
        Get all dependencies recursively (in case of dependency chains)
        """
        all_deps = set()
        to_check = list(self.dependencies.all())

        while to_check:
            dep = to_check.pop()
            if dep not in all_deps:
                all_deps.add(dep)
                to_check.extend(dep.dependencies.exclude(id__in=[d.id for d in all_deps]))

        return all_deps

    def get_all_dependents(self):
        """
        Get all tasks that depend on this task recursively
        """
        all_dependents = set()
        to_check = list(self.dependents.all())

        while to_check:
            dep = to_check.pop()
            if dep not in all_dependents:
                all_dependents.add(dep)
                to_check.extend(dep.dependents.exclude(id__in=[d.id for d in all_dependents]))

        return all_dependents
