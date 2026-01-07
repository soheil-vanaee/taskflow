from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project


User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False
    )
    member_details = serializers.SerializerMethodField()
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'deadline', 
            'owner', 'members', 'member_details',
            'created_at', 'updated_at', 'progress_percentage'
        ]
        read_only_fields = ('owner', 'created_at', 'updated_at')

    def get_member_details(self, obj):
        """
        Return detailed information about project members
        """
        members = obj.members.all()
        return [
            {
                'id': member.id,
                'email': member.email,
                'username': member.username,
                'first_name': member.first_name,
                'last_name': member.last_name
            }
            for member in members
        ]

    def create(self, validated_data):
        """
        Create a new project with the current user as the owner
        """
        members = validated_data.pop('members', [])
        project = Project.objects.create(owner=self.context['request'].user, **validated_data)
        project.members.set(members)
        return project

    def update(self, instance, validated_data):
        """
        Update project and handle members
        """
        members = validated_data.pop('members', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if members is not None:
            instance.members.set(members)

        return instance


class ProjectListSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    members_count = serializers.SerializerMethodField()
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'deadline', 
            'owner', 'members_count', 'progress_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('owner', 'created_at', 'updated_at')

    def get_members_count(self, obj):
        """
        Return the count of members in the project
        """
        return obj.members.count()