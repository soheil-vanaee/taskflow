from django.contrib import admin
from .models import ActivityLog, Notification


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'target_type', 'target_id', 'created_at')
    list_filter = ('action', 'created_at', 'user')
    search_fields = ('user__email', 'description')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'target_type')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at', 'recipient')
    search_fields = ('recipient__email', 'title', 'message')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('recipient', 'target_type')