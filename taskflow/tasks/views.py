from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Task
from .serializers import TaskSerializer, TaskListSerializer
from accounts.permissions import IsOwnerOrMember


class TaskListView(generics.ListCreateAPIView):
    """
    List all tasks or create a new task
    """
    serializer_class = TaskListSerializer

    def get_queryset(self):
        """
        Return tasks that belong to projects the user has access to
        """
        user = self.request.user
        return Task.objects.filter(
            Q(project__owner=user) | Q(project__members=user)
        ).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        """
        Create a task ensuring the user has access to the project
        """
        project = serializer.validated_data.get('project')
        if project and not project.can_user_access(self.request.user):
            raise PermissionError("You don't have access to this project.")
        serializer.save()


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a task instance
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        """
        Ensure users can only access tasks from projects they have access to
        """
        user = self.request.user
        return Task.objects.filter(
            Q(project__owner=user) | Q(project__members=user)
        ).distinct()


@api_view(['POST'])
def update_task_status(request, task_id):
    """
    Update the status of a task
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Check if the user has permission to modify the task
    if not task.can_user_modify(request.user):
        return Response(
            {'error': 'You do not have permission to modify this task'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    new_status = request.data.get('status')
    if not new_status:
        return Response(
            {'error': 'Status is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate status transition
    if not task.can_transition_to_status(new_status):
        return Response(
            {'error': f'Cannot transition from {task.status} to {new_status}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if dependencies are completed when trying to complete the task
    if new_status == 'completed':
        incomplete_dependencies = task.dependencies.exclude(status='completed')
        if incomplete_dependencies.exists():
            return Response(
                {
                    'error': 'Cannot complete task until all dependencies are completed',
                    'incomplete_dependencies': [
                        {'id': t.id, 'title': t.title} 
                        for t in incomplete_dependencies
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    task.status = new_status
    task.save()
    
    return Response(
        {'message': f'Task status updated to {new_status}', 'task': TaskSerializer(task).data},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def assign_task(request, task_id):
    """
    Assign a task to a user
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Check if the user has permission to modify the task
    if not task.can_user_modify(request.user):
        return Response(
            {'error': 'You do not have permission to modify this task'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    user_id = request.data.get('user_id')
    if not user_id:
        return Response(
            {'error': 'User ID is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = request.user.__class__.objects.get(id=user_id)
    except request.user.__class__.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if the user is a member of the project
    if user not in task.project.members.all() and user != task.project.owner:
        return Response(
            {'error': 'User must be a member of the project to be assigned tasks'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    task.assignee = user
    task.save()
    
    return Response(
        {'message': f'Task assigned to {user.email}', 'task': TaskSerializer(task).data},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def add_dependency(request, task_id):
    """
    Add a dependency to a task
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Check if the user has permission to modify the task
    if not task.can_user_modify(request.user):
        return Response(
            {'error': 'You do not have permission to modify this task'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    dependency_id = request.data.get('dependency_id')
    if not dependency_id:
        return Response(
            {'error': 'Dependency ID is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        dependency = Task.objects.get(id=dependency_id)
    except Task.DoesNotExist:
        return Response(
            {'error': 'Dependency task not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if both tasks are in the same project
    if task.project != dependency.project:
        return Response(
            {'error': 'Dependency must be in the same project'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Prevent circular dependencies
    if dependency == task:
        return Response(
            {'error': 'A task cannot depend on itself'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if this would create a circular dependency
    if dependency in task.get_all_dependencies():
        return Response(
            {'error': 'This would create a circular dependency'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    task.dependencies.add(dependency)
    
    return Response(
        {'message': f'Dependency added to task', 'task': TaskSerializer(task).data},
        status=status.HTTP_200_OK
    )