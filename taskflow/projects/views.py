from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Project
from .serializers import ProjectSerializer, ProjectListSerializer
from accounts.permissions import IsOwnerOrMember


class ProjectListView(generics.ListCreateAPIView):
    """
    List all projects or create a new project
    """
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        """
        Return projects that the user owns or is a member of
        """
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        """
        Set the owner to the current user when creating a project
        """
        project = serializer.save(owner=self.request.user)
        # Add the owner as a member of the project
        project.members.add(self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a project instance
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        """
        Ensure users can only access projects they own or are members of
        """
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()


@api_view(['POST'])
def add_member_to_project(request, project_id):
    """
    Add a member to a project
    """
    project = get_object_or_404(Project, id=project_id)
    
    # Check if the user is the owner of the project
    if request.user != project.owner:
        return Response(
            {'error': 'Only project owner can add members'}, 
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
    
    project.members.add(user)
    return Response(
        {'message': f'User {user.email} added to project'}, 
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def remove_member_from_project(request, project_id):
    """
    Remove a member from a project
    """
    project = get_object_or_404(Project, id=project_id)
    
    # Check if the user is the owner of the project
    if request.user != project.owner:
        return Response(
            {'error': 'Only project owner can remove members'}, 
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
    
    # Don't allow removing the owner from the project
    if user == project.owner:
        return Response(
            {'error': 'Cannot remove owner from project'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    project.members.remove(user)
    return Response(
        {'message': f'User {user.email} removed from project'}, 
        status=status.HTTP_200_OK
    )