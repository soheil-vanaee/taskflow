from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, BillingHistory


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'projects_limit', 'team_members_limit', 'tasks_limit', 'is_active')
    list_filter = ('is_active', 'price')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'is_active_subscription')
    list_filter = ('status', 'start_date', 'end_date', 'plan')
    search_fields = ('user__email', 'user__username', 'plan__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BillingHistory)
class BillingHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'plan')
    search_fields = ('user__email', 'user__username', 'transaction_id')
    readonly_fields = ('created_at',)