from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ActivityLog, Notification
from .serializers import ActivityLogSerializer, NotificationSerializer, NotificationUpdateSerializer


class ActivityLogListView(generics.ListAPIView):
    """
    List all activity logs for the current user
    """
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return activity logs for the current user
        """
        return ActivityLog.objects.filter(user=self.request.user).select_related(
            'user'
        ).order_by('-created_at')


class NotificationListView(generics.ListAPIView):
    """
    List all notifications for the current user
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return notifications for the current user
        """
        return Notification.objects.filter(recipient=self.request.user).select_related(
            'recipient'
        ).order_by('-created_at')


class UnreadNotificationListView(generics.ListAPIView):
    """
    List all unread notifications for the current user
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return unread notifications for the current user
        """
        return Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).select_related('recipient').order_by('-created_at')


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, notification_id):
    """
    Mark a specific notification as read
    """
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_as_read(request):
    """
    Mark all notifications as read for the current user
    """
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """
    Delete a specific notification
    """
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.delete()
    return Response({'message': 'Notification deleted'}, status=status.HTTP_204_NO_CONTENT)