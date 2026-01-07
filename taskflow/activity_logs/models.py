from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ActivityLog(models.Model):
    """
    Model to track user activities in the system
    """
    class Action(models.TextChoices):
        CREATED = 'created', 'Created'
        UPDATED = 'updated', 'Updated'
        DELETED = 'deleted', 'Deleted'
        ASSIGNED = 'assigned', 'Assigned'
        STATUS_CHANGED = 'status_changed', 'Status Changed'
        JOINED_PROJECT = 'joined_project', 'Joined Project'
        LEFT_PROJECT = 'left_project', 'Left Project'
        SUBSCRIPTION_CHANGED = 'subscription_changed', 'Subscription Changed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_type', 'target_id')
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return f"{self.user.email} {self.action} {self.target_type.model} #{self.target_id}"


class Notification(models.Model):
    """
    Model to represent notifications for users
    """
    class Type(models.TextChoices):
        TASK_ASSIGNED = 'task_assigned', 'Task Assigned'
        TASK_STATUS_CHANGED = 'task_status_changed', 'Task Status Changed'
        PROJECT_INVITE = 'project_invite', 'Project Invite'
        DEADLINE_REMINDER = 'deadline_reminder', 'Deadline Reminder'
        SUBSCRIPTION_EXPIRED = 'subscription_expired', 'Subscription Expired'
        SYSTEM_MESSAGE = 'system_message', 'System Message'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_type', 'target_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.email} - {self.notification_type}"

    def mark_as_read(self):
        """
        Mark the notification as read
        """
        self.is_read = True
        self.save(update_fields=['is_read'])

    def mark_as_unread(self):
        """
        Mark the notification as unread
        """
        self.is_read = False
        self.save(update_fields=['is_read'])
