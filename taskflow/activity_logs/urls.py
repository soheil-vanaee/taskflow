from django.urls import path
from . import views

urlpatterns = [
    path('activities/', views.ActivityLogListView.as_view(), name='activity-log-list'),
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/unread/', views.UnreadNotificationListView.as_view(), name='unread-notification-list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_as_read, name='mark-notification-read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_as_read, name='mark-all-notifications-read'),
    path('notifications/<int:notification_id>/', views.delete_notification, name='delete-notification'),
]