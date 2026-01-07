from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('my-subscription/', views.UserSubscriptionView.as_view(), name='user-subscription'),
    path('check-limits/', views.check_usage_limits, name='check-usage-limits'),
    path('start-trial/', views.start_trial, name='start-trial'),
]