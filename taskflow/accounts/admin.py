from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Define which fields to display in the admin list view
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    
    # Define which fields to filter by
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    
    # Define which fields to search by
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    # Define which fields to order by
    ordering = ('email',)
    
    # Override fieldsets to include custom fields
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )
    
    # Override add_fieldsets to include custom fields when creating a user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'role')}),
    )