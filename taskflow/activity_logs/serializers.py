from rest_framework import serializers
from .models import ActivityLog, Notification


class ActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    target_details = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'action', 'target', 'target_details',
            'description', 'ip_address', 'created_at'
        ]
        read_only_fields = ('user', 'created_at')

    def get_target_details(self, obj):
        """
        Get details about the target object
        """
        if obj.target:
            return {
                'id': obj.target.id,
                'type': obj.target_type.model,
                'repr': str(obj.target)
            }
        return None


class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    target_details = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'is_read', 'target', 'target_details',
            'sender', 'created_at'
        ]
        read_only_fields = ('created_at',)

    def get_sender(self, obj):
        """
        Get the sender of the notification if available
        """
        # This would need to be customized based on the notification type
        # For now, we'll return a placeholder
        return "System"

    def get_target_details(self, obj):
        """
        Get details about the target object
        """
        if obj.target:
            return {
                'id': obj.target.id,
                'type': obj.target_type.model,
                'repr': str(obj.target)
            }
        return None


class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['is_read']