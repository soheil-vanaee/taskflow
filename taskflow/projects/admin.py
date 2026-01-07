from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'deadline', 'created_at', 'is_completed', 'progress_percentage')
    list_filter = ('created_at', 'deadline', 'owner')
    search_fields = ('name', 'description', 'owner__email', 'members__email')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('members',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('owner').prefetch_related('members')