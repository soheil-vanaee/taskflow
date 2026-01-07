from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Notification
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from projects.models import Project
from tasks.models import Task

User = get_user_model()


@shared_task
def send_deadline_reminder():
    """
    Send deadline reminders for tasks and projects that are due soon
    """
    from datetime import timedelta
    
    # Find tasks with deadlines in the next 24 hours
    tomorrow = timezone.now() + timedelta(days=1)
    upcoming_deadline_tasks = Task.objects.filter(
        deadline__date=tomorrow.date(),
        status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW]
    )
    
    for task in upcoming_deadline_tasks:
        # Create a notification for the assignee
        if task.assignee:
            Notification.objects.create(
                recipient=task.assignee,
                notification_type=Notification.Type.DEADLINE_REMINDER,
                title=f"Task Deadline Approaching: {task.title}",
                message=f"The task '{task.title}' is due tomorrow ({task.deadline.strftime('%Y-%m-%d %H:%M')}).",
                target=task
            )
        
        # Also notify the project owner
        if task.project.owner != task.assignee:
            Notification.objects.create(
                recipient=task.project.owner,
                notification_type=Notification.Type.DEADLINE_REMINDER,
                title=f"Task Deadline Approaching: {task.title}",
                message=f"The task '{task.title}' in project '{task.project.name}' is due tomorrow ({task.deadline.strftime('%Y-%m-%d %H:%M')}).",
                target=task
            )
    
    # Find projects with deadlines in the next 24 hours
    upcoming_deadline_projects = Project.objects.filter(
        deadline__date=tomorrow.date(),
        tasks__status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW]
    ).distinct()
    
    for project in upcoming_deadline_projects:
        # Notify the project owner
        Notification.objects.create(
            recipient=project.owner,
            notification_type=Notification.Type.DEADLINE_REMINDER,
            title=f"Project Deadline Approaching: {project.name}",
            message=f"The project '{project.name}' is due tomorrow ({project.deadline.strftime('%Y-%m-%d %H:%M')}).",
            target=project
        )
        
        # Notify all members of the project
        for member in project.members.exclude(id=project.owner.id):
            Notification.objects.create(
                recipient=member,
                notification_type=Notification.Type.DEADLINE_REMINDER,
                title=f"Project Deadline Approaching: {project.name}",
                message=f"The project '{project.name}' is due tomorrow ({project.deadline.strftime('%Y-%m-%d %H:%M')}).",
                target=project
            )
    
    return f"Sent {len(upcoming_deadline_tasks)} task reminders and {len(upcoming_deadline_projects)} project reminders"


@shared_task
def generate_weekly_reports():
    """
    Generate weekly progress reports for all projects
    """
    from datetime import timedelta
    
    # Get projects that had activity in the last week
    week_ago = timezone.now() - timedelta(weeks=1)
    
    # This is a simplified version - in a real app, you'd want to generate
    # detailed reports with statistics, charts, etc.
    projects_with_activity = Project.objects.filter(
        tasks__updated_at__gte=week_ago
    ).distinct()
    
    for project in projects_with_activity:
        # Count completed tasks in the last week
        completed_tasks = project.tasks.filter(
            status=Task.Status.COMPLETED,
            updated_at__gte=week_ago
        ).count()
        
        # Count total tasks
        total_tasks = project.tasks.count()
        
        # Count overdue tasks
        overdue_tasks = project.tasks.filter(
            deadline__lt=timezone.now(),
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW]
        ).count()
        
        # Generate report summary
        report_summary = f"""
        Weekly Report for {project.name}:
        - Total Tasks: {total_tasks}
        - Completed This Week: {completed_tasks}
        - Overdue Tasks: {overdue_tasks}
        - Progress: {project.progress_percentage}%
        """
        
        # Send notification to project owner
        Notification.objects.create(
            recipient=project.owner,
            notification_type=Notification.Type.SYSTEM_MESSAGE,
            title=f"Weekly Report: {project.name}",
            message=report_summary.strip(),
            target=project
        )
        
        # Send to all members
        for member in project.members.exclude(id=project.owner.id):
            Notification.objects.create(
                recipient=member,
                notification_type=Notification.Type.SYSTEM_MESSAGE,
                title=f"Weekly Report: {project.name}",
                message=report_summary.strip(),
                target=project
            )
    
    return f"Generated weekly reports for {len(projects_with_activity)} projects"


@shared_task
def check_subscription_expirations():
    """
    Check for expiring subscriptions and send notifications
    """
    from datetime import timedelta
    
    # Find subscriptions that expire in the next 3 days
    three_days_later = timezone.now() + timedelta(days=3)
    
    expiring_subscriptions = []
    
    # This would normally query the UserSubscription model
    # For now, we'll simulate checking
    from subscriptions.models import UserSubscription
    
    expiring_subs = UserSubscription.objects.filter(
        end_date__date=three_days_later.date(),
        status=UserSubscription.Status.ACTIVE
    )
    
    for sub in expiring_subs:
        Notification.objects.create(
            recipient=sub.user,
            notification_type=Notification.Type.SUBSCRIPTION_EXPIRED,
            title="Subscription Expiring Soon",
            message=f"Your subscription to {sub.plan.name} will expire in 3 days on {sub.end_date.strftime('%Y-%m-%d')}. Renew now to avoid interruption.",
        )
        expiring_subscriptions.append(sub.user.email)
    
    return f"Checked subscriptions, notified {len(expiring_subscriptions)} users: {', '.join(expiring_subscriptions)}"


@shared_task
def send_task_assignment_notification(task_id, assignee_id):
    """
    Send notification when a task is assigned to a user
    """
    try:
        task = Task.objects.get(id=task_id)
        assignee = User.objects.get(id=assignee_id)
        
        Notification.objects.create(
            recipient=assignee,
            notification_type=Notification.Type.TASK_ASSIGNED,
            title=f"You've been assigned a task: {task.title}",
            message=f"The task '{task.title}' in project '{task.project.name}' has been assigned to you by {task.project.owner}.",
            target=task
        )
        
        return f"Notification sent to {assignee.email} about task assignment"
    except (Task.DoesNotExist, User.DoesNotExist):
        return "Task or user not found"


@shared_task
def send_status_change_notification(task_id, old_status, new_status, changed_by_id):
    """
    Send notification when a task status changes
    """
    try:
        task = Task.objects.get(id=task_id)
        changed_by = User.objects.get(id=changed_by_id)
        
        # Notify the assignee if different from the person who changed the status
        if task.assignee and task.assignee != changed_by:
            Notification.objects.create(
                recipient=task.assignee,
                notification_type=Notification.Type.TASK_STATUS_CHANGED,
                title=f"Task status changed: {task.title}",
                message=f"The status of task '{task.title}' was changed from {old_status} to {new_status} by {changed_by.username}.",
                target=task
            )
        
        # Notify the project owner if different from the person who changed the status
        if task.project.owner != changed_by:
            Notification.objects.create(
                recipient=task.project.owner,
                notification_type=Notification.Type.TASK_STATUS_CHANGED,
                title=f"Task status changed: {task.title}",
                message=f"The status of task '{task.title}' was changed from {old_status} to {new_status} by {changed_by.username}.",
                target=task
            )
        
        return f"Status change notifications sent for task {task.title}"
    except (Task.DoesNotExist, User.DoesNotExist):
        return "Task or user not found"