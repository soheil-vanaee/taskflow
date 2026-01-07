from django.utils import timezone
from datetime import timedelta
from projects.models import Project
from tasks.models import Task
from activity_logs.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


class ReportingService:
    """
    Service class to handle reporting and analytics
    """
    
    @staticmethod
    def generate_project_report(project_id):
        """
        Generate a detailed report for a specific project
        """
        try:
            project = Project.objects.prefetch_related('tasks', 'members').get(id=project_id)
            
            # Calculate various metrics
            total_tasks = project.tasks.count()
            completed_tasks = project.tasks.filter(status=Task.Status.COMPLETED).count()
            in_progress_tasks = project.tasks.filter(status=Task.Status.IN_PROGRESS).count()
            todo_tasks = project.tasks.filter(status=Task.Status.TODO).count()
            overdue_tasks = project.tasks.filter(
                deadline__lt=timezone.now(),
                status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW]
            ).count()
            
            # Calculate progress percentage
            progress_percentage = 0
            if total_tasks > 0:
                progress_percentage = round((completed_tasks / total_tasks) * 100, 2)
            
            # Find most active members (based on task assignments)
            member_stats = {}
            for task in project.tasks.all():
                if task.assignee:
                    member_email = task.assignee.email
                    if member_email in member_stats:
                        member_stats[member_email]['tasks_assigned'] += 1
                        if task.status == Task.Status.COMPLETED:
                            member_stats[member_email]['tasks_completed'] += 1
                    else:
                        member_stats[member_email] = {
                            'tasks_assigned': 1,
                            'tasks_completed': 1 if task.status == Task.Status.COMPLETED else 0
                        }
            
            report = {
                'project_name': project.name,
                'project_owner': project.owner.email,
                'report_generated_at': timezone.now(),
                'project_metrics': {
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'in_progress_tasks': in_progress_tasks,
                    'todo_tasks': todo_tasks,
                    'overdue_tasks': overdue_tasks,
                    'progress_percentage': progress_percentage,
                    'days_since_created': (timezone.now() - project.created_at).days,
                },
                'member_statistics': member_stats,
                'upcoming_deadlines': []
            }
            
            # Add upcoming deadlines (next 7 days)
            upcoming_tasks = project.tasks.filter(
                deadline__gte=timezone.now(),
                deadline__lte=timezone.now() + timedelta(days=7),
                status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW]
            ).order_by('deadline')
            
            for task in upcoming_tasks:
                report['upcoming_deadlines'].append({
                    'task_title': task.title,
                    'task_status': task.status,
                    'deadline': task.deadline,
                    'assignee': task.assignee.email if task.assignee else 'Unassigned'
                })
                
            return report
            
        except Project.DoesNotExist:
            return None
    
    @staticmethod
    def generate_weekly_digest(user_id):
        """
        Generate a weekly digest for a user showing their tasks and projects
        """
        try:
            user = User.objects.prefetch_related('projects', 'assigned_tasks').get(id=user_id)
            
            # Get projects the user is involved in
            projects = Project.objects.filter(
                owner=user
            ).union(
                Project.objects.filter(members=user)
            ).distinct()
            
            # Get user's assigned tasks
            assigned_tasks = Task.objects.filter(assignee=user)
            
            # Get tasks updated in the last week
            week_ago = timezone.now() - timedelta(weeks=1)
            recently_updated_tasks = Task.objects.filter(
                project__in=projects,
                updated_at__gte=week_ago
            )
            
            # Calculate stats
            total_assigned_tasks = assigned_tasks.count()
            completed_this_week = assigned_tasks.filter(
                status=Task.Status.COMPLETED,
                updated_at__gte=week_ago
            ).count()
            overdue_assigned = assigned_tasks.filter(
                deadline__lt=timezone.now(),
                status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW]
            ).count()
            
            # Upcoming deadlines for the user
            upcoming_deadlines = assigned_tasks.filter(
                deadline__gte=timezone.now(),
                deadline__lte=timezone.now() + timedelta(days=7),
                status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW]
            ).order_by('deadline')[:5]
            
            digest = {
                'user_email': user.email,
                'digest_week_start': week_ago,
                'digest_generated_at': timezone.now(),
                'user_metrics': {
                    'total_assigned_tasks': total_assigned_tasks,
                    'completed_this_week': completed_this_week,
                    'overdue_assigned': overdue_assigned,
                    'projects_involved_in': projects.count(),
                },
                'upcoming_deadlines': [
                    {
                        'task_title': task.title,
                        'project_name': task.project.name,
                        'deadline': task.deadline,
                        'status': task.status
                    }
                    for task in upcoming_deadlines
                ],
                'recently_updated_tasks': [
                    {
                        'task_title': task.title,
                        'project_name': task.project.name,
                        'status': task.status,
                        'updated_at': task.updated_at
                    }
                    for task in recently_updated_tasks[:10]  # Limit to 10 most recent
                ]
            }
            
            return digest
            
        except User.DoesNotExist:
            return None


class ReminderService:
    """
    Service class to handle reminder notifications
    """
    
    @staticmethod
    def send_task_assignment_notification(task_id, assignee_id):
        """
        Send notification when a task is assigned to a user
        """
        try:
            task = Task.objects.select_related('project', 'project__owner').get(id=task_id)
            assignee = User.objects.get(id=assignee_id)
            
            # Create notification
            notification = Notification.objects.create(
                recipient=assignee,
                notification_type=Notification.Type.TASK_ASSIGNED,
                title=f"You've been assigned a task: {task.title}",
                message=f"The task '{task.title}' in project '{task.project.name}' has been assigned to you by {task.project.owner}.",
                target=task
            )
            
            # Trigger the async task to actually send the notification
            from notifications.tasks import send_task_assignment_notification
            send_task_assignment_notification.delay(task_id, assignee_id)
            
            return notification
            
        except (Task.DoesNotExist, User.DoesNotExist):
            return None
    
    @staticmethod
    def send_status_change_notification(task_id, old_status, new_status, changed_by_id):
        """
        Send notification when a task status changes
        """
        try:
            task = Task.objects.select_related('project', 'assignee').get(id=task_id)
            changed_by = User.objects.get(id=changed_by_id)
            
            # Create notification for assignee if different from changer
            notifications_sent = []
            
            if task.assignee and task.assignee != changed_by:
                notification = Notification.objects.create(
                    recipient=task.assignee,
                    notification_type=Notification.Type.TASK_STATUS_CHANGED,
                    title=f"Task status changed: {task.title}",
                    message=f"The status of task '{task.title}' was changed from {old_status} to {new_status} by {changed_by.username}.",
                    target=task
                )
                notifications_sent.append(notification)
            
            # Create notification for project owner if different from changer
            if task.project.owner != changed_by:
                notification = Notification.objects.create(
                    recipient=task.project.owner,
                    notification_type=Notification.Type.TASK_STATUS_CHANGED,
                    title=f"Task status changed: {task.title}",
                    message=f"The status of task '{task.title}' was changed from {old_status} to {new_status} by {changed_by.username}.",
                    target=task
                )
                notifications_sent.append(notification)
            
            # Trigger the async task
            from notifications.tasks import send_status_change_notification
            send_status_change_notification.delay(task_id, old_status, new_status, changed_by_id)
            
            return notifications_sent
            
        except (Task.DoesNotExist, User.DoesNotExist):
            return []
    
    @staticmethod
    def send_project_invitation_notification(project_id, invited_user_id, inviter_id):
        """
        Send notification when a user is invited to join a project
        """
        try:
            project = Project.objects.get(id=project_id)
            invited_user = User.objects.get(id=invited_user_id)
            inviter = User.objects.get(id=inviter_id)
            
            notification = Notification.objects.create(
                recipient=invited_user,
                notification_type=Notification.Type.PROJECT_INVITE,
                title=f"Invitation to join project: {project.name}",
                message=f"You have been invited by {inviter.username} to join the project '{project.name}'.",
                target=project
            )
            
            return notification
            
        except (Project.DoesNotExist, User.DoesNotExist):
            return None