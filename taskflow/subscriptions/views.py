from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import SubscriptionPlan, UserSubscription, BillingHistory
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer, BillingHistorySerializer


class SubscriptionPlanListView(generics.ListAPIView):
    """
    List all available subscription plans
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer


class UserSubscriptionView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current user's subscription
    """
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Get or create the user's subscription
        """
        subscription, created = UserSubscription.objects.get_or_create(
            user=self.request.user,
            defaults={
                'plan': SubscriptionPlan.objects.get(name='Free'),  # Default to free plan
                'status': UserSubscription.Status.ACTIVE
            }
        )
        return subscription

    def update(self, request, *args, **kwargs):
        """
        Update user's subscription plan
        """
        instance = self.get_object()
        plan_id = request.data.get('plan_id')
        
        if plan_id:
            try:
                new_plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            except SubscriptionPlan.DoesNotExist:
                return Response(
                    {'error': 'Invalid subscription plan'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Here you would typically integrate with a payment processor like Stripe
            # For now, we'll just update the plan
            
            instance.plan = new_plan
            instance.status = UserSubscription.Status.ACTIVE
            instance.save()
            
            # Create a billing history record
            BillingHistory.objects.create(
                user=request.user,
                plan=new_plan,
                amount=new_plan.price,
                transaction_id=f"txn_{request.user.id}_{new_plan.id}_{instance.id}",
                status='succeeded'
            )
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        
        return super().update(request, *args, **kwargs)


@api_view(['GET'])
def check_usage_limits(request):
    """
    Check if the current user has exceeded their plan limits
    """
    try:
        user_subscription = request.user.subscription
        within_limits, message = user_subscription.check_usage_limits(request.user)
        return Response({
            'within_limits': within_limits,
            'message': message,
            'limits': {
                'projects_limit': user_subscription.plan.projects_limit,
                'team_members_limit': user_subscription.plan.team_members_limit,
                'tasks_limit': user_subscription.plan.tasks_limit,
            }
        })
    except UserSubscription.DoesNotExist:
        # If no subscription exists, use the free plan limits
        free_plan = SubscriptionPlan.objects.get(name='Free')
        return Response({
            'within_limits': True,
            'message': 'Using free plan limits',
            'limits': {
                'projects_limit': free_plan.projects_limit,
                'team_members_limit': free_plan.team_members_limit,
                'tasks_limit': free_plan.tasks_limit,
            }
        })


@api_view(['POST'])
def start_trial(request):
    """
    Start a trial for the user
    """
    from datetime import timedelta
    from django.utils import timezone
    
    # Get or create user subscription
    user_subscription, created = UserSubscription.objects.get_or_create(
        user=request.user,
        defaults={
            'plan': SubscriptionPlan.objects.get(name='Free'),
            'status': UserSubscription.Status.TRIALING
        }
    )
    
    # Set trial to end in 7 days
    user_subscription.trial_end_date = timezone.now() + timedelta(days=7)
    user_subscription.status = UserSubscription.Status.TRIALING
    user_subscription.save()
    
    return Response({
        'message': 'Trial started successfully',
        'trial_end_date': user_subscription.trial_end_date
    })