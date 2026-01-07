from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'project', 'assignee', 'deadline', 'created_at', 'is_completed')
    list_filter = ('status', 'priority', 'created_at', 'deadline', 'project')
    search_fields = ('title', 'description', 'project__name', 'assignee__email')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('dependencies',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('project', 'assignee').prefetch_related('dependencies')