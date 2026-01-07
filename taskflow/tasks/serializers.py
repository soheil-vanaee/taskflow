from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task
from projects.models import Project

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False, 
        allow_null=True
    )
    dependencies = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), 
        many=True, 
        required=False
    )
    assignee_details = serializers.SerializerMethodField()
    project_details = serializers.SerializerMethodField()
    dependencies_details = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 
            'deadline', 'project', 'assignee', 'dependencies',
            'assignee_details', 'project_details', 'dependencies_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')

    def get_assignee_details(self, obj):
        """
        Return detailed information about the assignee
        """
        if obj.assignee:
            return {
                'id': obj.assignee.id,
                'email': obj.assignee.email,
                'username': obj.assignee.username,
                'first_name': obj.assignee.first_name,
                'last_name': obj.assignee.last_name
            }
        return None

    def get_project_details(self, obj):
        """
        Return detailed information about the project
        """
        return {
            'id': obj.project.id,
            'name': obj.project.name,
            'owner': obj.project.owner.email
        }

    def get_dependencies_details(self, obj):
        """
        Return detailed information about task dependencies
        """
        dependencies = obj.dependencies.all()
        return [
            {
                'id': dep.id,
                'title': dep.title,
                'status': dep.status,
                'is_completed': dep.is_completed
            }
            for dep in dependencies
        ]

    def validate(self, attrs):
        """
        Validate task constraints
        """
        # Check if user has access to the project
        project = attrs.get('project') or self.instance.project if self.instance else None
        if project and not project.can_user_access(self.context['request'].user):
            raise serializers.ValidationError("You don't have access to this project.")
        
        # Check if user has permission to assign to the selected user
        assignee = attrs.get('assignee')
        if assignee and not project.can_user_access(assignee):
            raise serializers.ValidationError("Assignee must be a member of the project.")
        
        # Check status transition validity if status is being updated
        if self.instance and 'status' in attrs:
            new_status = attrs['status']
            if not self.instance.can_transition_to_status(new_status):
                raise serializers.ValidationError(
                    f"Cannot transition from {self.instance.status} to {new_status}."
                )
        
        # Check dependencies are in the same project
        dependencies = attrs.get('dependencies', [])
        for dep in dependencies:
            if dep.project != project:
                raise serializers.ValidationError(
                    "All dependencies must belong to the same project as the task."
                )
        
        return attrs

    def create(self, validated_data):
        """
        Create a new task
        """
        dependencies = validated_data.pop('dependencies', [])
        task = Task.objects.create(**validated_data)
        if dependencies:
            task.dependencies.set(dependencies)
        return task

    def update(self, instance, validated_data):
        """
        Update task and handle dependencies
        """
        dependencies = validated_data.pop('dependencies', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if dependencies is not None:
            instance.dependencies.set(dependencies)

        return instance


class TaskListSerializer(serializers.ModelSerializer):
    project = serializers.StringRelatedField(read_only=True)
    assignee = serializers.StringRelatedField(read_only=True)
    dependencies_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'priority', 
            'deadline', 'project', 'assignee',
            'dependencies_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')

    def get_dependencies_count(self, obj):
        """
        Return the count of dependencies for the task
        """
        return obj.dependencies.count()